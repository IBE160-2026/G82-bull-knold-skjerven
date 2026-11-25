"""Dekningsgraden per notat og emne (FR-24, FR-25, AD-4). Eneste sted som regner den ut. Bare lesing.

Et spørsmål er dekket når det har minst ett riktig svar i en levert økt (forsøk
eller øving) og ingen åpen feilbankrad (`laert_tidspunkt` er tom, som
`apne_rader`). Meldte spørsmål (FR-31) telles verken som dekket eller i
nevneren, og et nivå der alle spørsmålene er meldt, teller som et nivå uten
quiz. Tallene er mellom 0 og 1 uten avrunding. Avrundingen skjer bare i malen
(`hel_prosent`). Et emnes dekningsgrad er snittet av notatene som har quiz.
"""

from typing import NamedTuple

from django.db.models import Count, Exists, OuterRef, Q

from studier.models import (
    Feilbankrad,
    Notat,
    Oktstatus,
    Quiz,
    Sporsmal,
    Svar,
    Vanskelighetsgrad,
)

VEKTER = {
    Vanskelighetsgrad.LETT: 0.2,
    Vanskelighetsgrad.MIDDELS: 0.3,
    Vanskelighetsgrad.VANSKELIG: 0.5,
}


class Dekning(NamedTuple):
    total: float
    # Andelen per nivå i `Vanskelighetsgrad`, eller `None` når nivået ikke har quiz.
    nivaer: dict

    @property
    def har_quiz(self) -> bool:
        """Sann når minst ett nivå har quiz. Et nivå der alt er meldt, har ikke quiz (FR-31)."""
        return any(andel is not None for andel in self.nivaer.values())


def for_notater(notater) -> dict:
    """Dekningsgraden for hvert av `notater`, som `{notat_id: Dekning}`.

    To spørringer uansett antall notater og spørsmål. `notater` må alt være
    hentet med `hent_egen` eller `egne`, som sikrer eieren. Totalen er vektet
    med `VEKTER`, og et nivå uten quiz teller 0. Bare spørsmål som ikke er
    meldt, telles.
    """
    notater = list(notater)
    riktig = Svar.objects.filter(
        sporsmal=OuterRef("pk"),
        okt__status=Oktstatus.LEVERT,
        alternativ__er_riktig=True,
    )
    apen = Feilbankrad.objects.filter(
        sporsmal=OuterRef("pk"), laert_tidspunkt__isnull=True
    )
    tall = {
        (rad["quiz__notat"], rad["quiz__vanskelighetsgrad"]): rad
        for rad in Sporsmal.objects.ikke_meldt()
        .filter(quiz__notat__in=notater)
        .alias(riktig=Exists(riktig), apen=Exists(apen))
        .values("quiz__notat", "quiz__vanskelighetsgrad")
        .annotate(
            antall=Count("pk"), dekket=Count("pk", filter=Q(riktig=True, apen=False))
        )
        .order_by()
    }
    # Et nivå teller som uten quiz når ingen av quizene har spørsmål som ikke er meldt.
    med_quiz = set(
        Quiz.objects.filter(notat__in=notater)
        .filter(Exists(Sporsmal.objects.ikke_meldt().filter(quiz=OuterRef("pk"))))
        .values_list("notat_id", "vanskelighetsgrad")
        .distinct()
    )

    dekninger = {}
    for notat in notater:
        nivaer = {}
        for nivaa in Vanskelighetsgrad:
            if (notat.pk, nivaa) not in med_quiz:
                nivaer[nivaa] = None
                continue
            rad = tall.get((notat.pk, nivaa))
            # En quiz har alltid spørsmål (2.1). Grenen hindrer bare deling med 0.
            nivaer[nivaa] = rad["dekket"] / rad["antall"] if rad else 0.0
        total = sum(
            (VEKTER[nivaa] * (andel or 0.0) for nivaa, andel in nivaer.items()), 0.0
        )
        dekninger[notat.pk] = Dekning(total=total, nivaer=nivaer)
    return dekninger


def for_notat(notat) -> Dekning:
    """Dekningsgraden for `notat`, totalt og per nivå. To spørringer, som `for_notater`.

    `notat` må alt være hentet med `hent_egen`, som sikrer eieren.
    """
    return for_notater([notat])[notat.pk]


def snitt(dekninger) -> float | None:
    """Emnets dekningsgrad fra notatenes `Dekning` (FR-25). Ingen spørringer.

    Snittet av `total` for notatene som har quiz, uavhengig av lengden på
    notatene. `None` når ingen av dem har quiz, eller det ikke er noen.
    """
    totaler = [dekning.total for dekning in dekninger if dekning.har_quiz]
    return sum(totaler) / len(totaler) if totaler else None


def for_emner(emner) -> dict:
    """Dekningsgraden for hvert av `emner`, som `{emne_id: float | None}` (FR-25).

    Regnes med `snitt`, så `None` når emnet ikke har notater, eller ingen av
    dem har quiz. Tre spørringer uansett antall emner, notater og spørsmål. `emner` må alt
    være hentet med `hent_egen` eller `egne`, som sikrer eieren.
    """
    emner = list(emner)
    notater = list(Notat.objects.filter(emne__in=emner).only("pk", "emne_id"))
    dekninger = for_notater(notater)
    per_emne = {emne.pk: [] for emne in emner}
    for notat in notater:
        per_emne[notat.emne_id].append(dekninger[notat.pk])
    return {emne_id: snitt(verdier) for emne_id, verdier in per_emne.items()}
