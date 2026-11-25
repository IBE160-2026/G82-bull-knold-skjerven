"""Dekningsgraden (FR-24, AD-4). Eneste sted som regner den ut. Bare lesing.

Et spørsmål er dekket når det har minst ett riktig svar i en levert økt (forsøk
eller øving) og ingen åpen feilbankrad (`laert_tidspunkt` er tom, som
`apne_rader`). Tallene er mellom 0 og 1 uten avrunding. Avrundingen skjer bare i
malen (`hel_prosent`). Meldte spørsmål telles med til story 4.3 legger til
`ikke_meldt()` her.
"""

from typing import NamedTuple

from django.db.models import Count, Exists, OuterRef, Q

from studier.models import Feilbankrad, Oktstatus, Sporsmal, Svar, Vanskelighetsgrad

VEKTER = {
    Vanskelighetsgrad.LETT: 0.2,
    Vanskelighetsgrad.MIDDELS: 0.3,
    Vanskelighetsgrad.VANSKELIG: 0.5,
}


class Dekning(NamedTuple):
    total: float
    # Andelen per nivå i `Vanskelighetsgrad`, eller `None` når nivået ikke har quiz.
    nivaer: dict


def for_notat(notat) -> Dekning:
    """Dekningsgraden for `notat`, totalt og per nivå. To spørringer uansett antall spørsmål.

    `notat` må alt være hentet med `hent_egen`, som sikrer eieren. Totalen er
    vektet med `VEKTER`, og et nivå uten quiz teller 0.
    """
    riktig = Svar.objects.filter(
        sporsmal=OuterRef("pk"),
        okt__status=Oktstatus.LEVERT,
        alternativ__er_riktig=True,
    )
    apen = Feilbankrad.objects.filter(
        sporsmal=OuterRef("pk"), laert_tidspunkt__isnull=True
    )
    tall = {
        rad["quiz__vanskelighetsgrad"]: rad
        for rad in Sporsmal.objects.filter(quiz__notat=notat)
        .alias(riktig=Exists(riktig), apen=Exists(apen))
        .values("quiz__vanskelighetsgrad")
        .annotate(
            antall=Count("pk"), dekket=Count("pk", filter=Q(riktig=True, apen=False))
        )
        .order_by()
    }
    med_quiz = set(notat.quizer.values_list("vanskelighetsgrad", flat=True))

    nivaer = {}
    for nivaa in Vanskelighetsgrad:
        if nivaa not in med_quiz:
            nivaer[nivaa] = None
            continue
        rad = tall.get(nivaa)
        # En quiz har alltid spørsmål (2.1). Grenen hindrer bare deling med 0.
        nivaer[nivaa] = rad["dekket"] / rad["antall"] if rad else 0.0
    total = sum(
        (VEKTER[nivaa] * (andel or 0.0) for nivaa, andel in nivaer.items()), 0.0
    )
    return Dekning(total=total, nivaer=nivaer)
