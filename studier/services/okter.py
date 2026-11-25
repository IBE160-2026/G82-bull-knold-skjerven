"""Økter: forsøk på en quiz (AD-6, AD-16, AD-17). Eneste sted som lager `Okt` og skriver `Svar`.

`Okt.innhold` er `[{"sporsmal": id, "alternativer": [id, id, id]}, …]` i
visningsrekkefølge. Listen lages når økten opprettes og endres aldri etterpå.
`nr` (1-basert) brukes bare til navigering.
"""

import logging
import random

from django.db import IntegrityError, transaction
from django.utils import timezone

from studier.models import Okt, Oktstatus, Okttype, Svar
from studier.services.feilbank import registrer_svar

logger = logging.getLogger(__name__)


class SvarAvvist(ValueError):
    """`lagre_svar` lagret ingenting: spørsmålet eller alternativet passer ikke økten."""


class OktErLevert(SvarAvvist):
    """`lagre_svar` lagret ingenting fordi økten ikke er påbegynt lenger."""


class UbesvarteSporsmal(ValueError):
    """`lever_okt` leverte ikke: `nr` er numrene (1-basert) til spørsmålene uten svar."""

    def __init__(self, nr):
        self.nr = list(nr)
        super().__init__(f"Ubesvarte spørsmål: {self.nr}.")


def _pabegynt_forsok(quiz):
    return Okt.objects.filter(
        quiz=quiz, type=Okttype.FORSOK, status=Oktstatus.PABEGYNT
    ).first()


def _lag_innhold(quiz):
    """Spørsmålene i quizens rekkefølge, hvert med alternativene stokket."""
    innhold = []
    for sporsmal in quiz.sporsmal.order_by("id").prefetch_related("alternativer"):
        alternativer = [alternativ.pk for alternativ in sporsmal.alternativer.all()]
        random.shuffle(alternativer)
        innhold.append({"sporsmal": sporsmal.pk, "alternativer": alternativer})
    return innhold


def start_eller_fortsett_okt(quiz):
    """Den påbegynte `forsok`-økten for quizen, eller en ny (AD-6, AD-16).

    Kalles bare fra POST. To samtidige kall gir samme økt: den betingede unike
    begrensningen stopper den andre opprettelsen, og da hentes den første.
    """
    try:
        with transaction.atomic():
            okt = _pabegynt_forsok(quiz)
            if okt is not None:
                return okt
            okt = Okt.objects.create(
                notat_id=quiz.notat_id,
                quiz=quiz,
                type=Okttype.FORSOK,
                status=Oktstatus.PABEGYNT,
                innhold=_lag_innhold(quiz),
            )
    except IntegrityError:
        okt = _pabegynt_forsok(quiz)
        if okt is None:
            raise
        return okt
    logger.info("Økt %s startet for quiz %s.", okt.pk, quiz.pk)
    return okt


def element(okt, nr):
    """Elementet i `okt.innhold` for `nr` (1-basert), eller `None` for ukjent nr."""
    if (
        isinstance(nr, bool)
        or not isinstance(nr, int)
        or not 1 <= nr <= len(okt.innhold)
    ):
        return None
    return okt.innhold[nr - 1]


def besvarte(okt):
    """ID-ene til spørsmålene i økten som har et `Svar`."""
    return set(okt.svar.values_list("sporsmal_id", flat=True))


def forste_ubesvarte(okt):
    """nr (1-basert) for første spørsmål uten svar. Er alle besvart, gir den 1."""
    svart = besvarte(okt)
    for nr, rad in enumerate(okt.innhold, start=1):
        if rad["sporsmal"] not in svart:
            return nr
    return 1


def lagre_svar(okt, sporsmal, alternativ):
    """Lagrer eller endrer svaret på `sporsmal` i økten (AD-17). Eneste sted som skriver `Svar`.

    Hever `OktErLevert` hvis økten ikke er påbegynt, og `SvarAvvist` hvis
    spørsmålet ikke står i `okt.innhold` eller alternativet ikke hører til det.
    """
    rad = next((r for r in okt.innhold if r["sporsmal"] == sporsmal.pk), None)
    if rad is None:
        raise SvarAvvist(f"Spørsmål {sporsmal.pk} står ikke i økt {okt.pk}.")
    if (
        alternativ.sporsmal_id != sporsmal.pk
        or alternativ.pk not in rad["alternativer"]
    ):
        raise SvarAvvist(
            f"Alternativ {alternativ.pk} hører ikke til spørsmål {sporsmal.pk}."
        )
    naa = timezone.now()
    with transaction.atomic():
        # Første skriving sjekker statusen og tar skrivelåsen, så en samtidig
        # levering ikke kan komme mellom sjekken og svaret.
        oppdatert = Okt.objects.filter(pk=okt.pk, status=Oktstatus.PABEGYNT).update(
            sist_endret=naa
        )
        if not oppdatert:
            raise OktErLevert(f"Økt {okt.pk} er ikke påbegynt.")
        svar, _ = Svar.objects.update_or_create(
            okt=okt, sporsmal=sporsmal, defaults={"alternativ": alternativ}
        )
    okt.sist_endret = naa
    return svar


def lever_okt(okt):
    """Leverer økten (AD-18). Gir `True` hvis dette kallet leverte, `False` hvis den alt var levert.

    Hever `UbesvarteSporsmal` (og rulles tilbake) hvis et spørsmål mangler svar.
    Eneste sted som kaller `registrer_svar`, én gang per spørsmål i `okt.innhold`.
    """
    naa = timezone.now()
    with transaction.atomic():
        # Første skriving sjekker statusen og tar skrivelåsen, så to samtidige
        # leveringer ikke begge registrerer mot feilbanken.
        endret = Okt.objects.filter(pk=okt.pk, status=Oktstatus.PABEGYNT).update(
            status=Oktstatus.LEVERT, levert_tidspunkt=naa
        )
        if not endret:
            return False
        svar_per_sporsmal = {
            svar.sporsmal_id: svar
            for svar in Svar.objects.filter(okt=okt).select_related(
                "alternativ", "sporsmal"
            )
        }
        ubesvarte = [
            nr
            for nr, rad in enumerate(okt.innhold, start=1)
            if rad["sporsmal"] not in svar_per_sporsmal
        ]
        if ubesvarte:
            raise UbesvarteSporsmal(ubesvarte)
        poengsum = 0
        for rad in okt.innhold:
            svar = svar_per_sporsmal[rad["sporsmal"]]
            riktig = svar.alternativ.er_riktig
            poengsum += bool(riktig)
            svar.hendelse = registrer_svar(svar.sporsmal, riktig=riktig)
            svar.save(update_fields=["hendelse"])
        antall = len(okt.innhold)
        Okt.objects.filter(pk=okt.pk).update(poengsum=poengsum, antall=antall)
    okt.status = Oktstatus.LEVERT
    okt.levert_tidspunkt = naa
    okt.poengsum = poengsum
    okt.antall = antall
    logger.info("Økt %s levert: %s av %s.", okt.pk, poengsum, antall)
    return True
