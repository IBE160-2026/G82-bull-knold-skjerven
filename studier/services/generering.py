"""Generering av quiz (FR-11–FR-14, AD-9). Eneste sted som lager `Genereringsjobb` og `Quiz` (AD-1).

Jobben går gjennom stegene `leser` → `lager` → `sjekker` → `ferdig`, ett steg per
kall på `kjor_steg`. Ingen `ki`-kall mens en transaksjon er åpen, og hver
statusovergang committes for seg (AD-19). Filinnhold lagres aldri på jobben og
logges aldri.
"""

import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

import ki
from studier.models import (
    Alternativ,
    Feilkode,
    Genereringsjobb,
    Jobbstatus,
    Notat,
    Quiz,
    Sporsmal,
    Vanskelighetsgrad,
)

logger = logging.getLogger(__name__)

TIDSFRIST = 120  # sekunder fra `startet` (FR-15)
MIN_ANTALL = 5
MAKS_ANTALL = 30
MAKS_STEG = 5  # leser, lager, sjekker, og lager og sjekker i runde 2
SLUTTSTATUSER = (Jobbstatus.FERDIG, Jobbstatus.FEILET)


def _aktive(notat):
    return Genereringsjobb.objects.filter(notat=notat).exclude(status__in=SLUTTSTATUSER)


def aktiv_jobb(notat):
    """Notatets aktive jobb, eller `None`. Eneste definisjon av aktiv jobb (AD-9).

    En aktiv jobb som startet for mer enn `TIDSFRIST` sekunder siden settes til
    `feilet`/`timeout` og regnes ikke som aktiv.
    """
    grense = timezone.now() - timedelta(seconds=TIDSFRIST)
    gamle = list(_aktive(notat).filter(startet__lt=grense).values_list("pk", flat=True))
    if gamle:
        Genereringsjobb.objects.filter(pk__in=gamle).exclude(
            status__in=SLUTTSTATUSER
        ).update(status=Jobbstatus.FEILET, feilkode=Feilkode.TIMEOUT, i_gang=False)
        for pk in gamle:
            logger.warning(
                "Genereringsjobb %s feilet med koden %s.", pk, Feilkode.TIMEOUT
            )
    return _aktive(notat).order_by("-startet", "-pk").first()


def opprett_jobb(notat, vanskelighetsgrad, antall):
    """Notatets aktive jobb hvis den finnes, ellers en ny (FR-14). Hever `ValueError` ved ugyldig valg."""
    if vanskelighetsgrad not in Vanskelighetsgrad.values:
        raise ValueError(f"Ukjent vanskelighetsgrad: {vanskelighetsgrad!r}")
    if (
        isinstance(antall, bool)
        or not isinstance(antall, int)
        or not MIN_ANTALL <= antall <= MAKS_ANTALL
    ):
        raise ValueError(f"Antall må være {MIN_ANTALL}–{MAKS_ANTALL}, fikk {antall!r}")
    with transaction.atomic():
        # På SQLite er select_for_update uten virkning. Der serialiseres samtidige
        # kall av transaction_mode IMMEDIATE i settings, som tar skrivelåsen ved
        # BEGIN. På databaser med radlås låser denne linjen notatet.
        Notat.objects.select_for_update().filter(pk=notat.pk).first()
        jobb = aktiv_jobb(notat)
        if jobb is not None:
            return jobb
        return Genereringsjobb.objects.create(
            notat=notat, vanskelighetsgrad=vanskelighetsgrad, antall=antall
        )


def _gjenstaende_tid(jobb):
    return TIDSFRIST - (timezone.now() - jobb.startet).total_seconds()


def _overgang(jobb, fra, **felter):
    """Setter nye felt hvis jobben fortsatt har status `fra`. Gir antall endrede rader."""
    return Genereringsjobb.objects.filter(pk=jobb.pk, status=fra).update(**felter)


def _leser(jobb):
    # Bare for å validere filen. Innholdet kastes.
    ki.les_fil(jobb.notat.fil.path)
    _overgang(jobb, Jobbstatus.LESER, status=Jobbstatus.LAGER)


def _lager(jobb):
    innhold = ki.les_fil(jobb.notat.fil.path)
    gjenstaende = _gjenstaende_tid(jobb)
    if gjenstaende <= 0:
        raise ki.KIFeil(Feilkode.TIMEOUT, "fristen er ute før generering")
    raatt = ki.generer(
        innhold, jobb.vanskelighetsgrad, jobb.antall, timeout=gjenstaende
    )
    _overgang(
        jobb,
        Jobbstatus.LAGER,
        status=Jobbstatus.SJEKKER,
        raatt_svar=raatt.tekst,
        forhandslagret=raatt.forhandslagret,
        modell=raatt.modell,
        prompt_versjon=raatt.prompt_versjon,
    )


def _sjekker(jobb):
    try:
        utkast = ki.sjekk(jobb.raatt_svar, jobb.antall)
    except ki.KIFeil as feil:
        if feil.kode == Feilkode.FORMAT and jobb.runde == 1:
            logger.info(
                "Genereringsjobb %s hadde feil format i runde 1. Lager på nytt.",
                jobb.pk,
            )
            _overgang(jobb, Jobbstatus.SJEKKER, status=Jobbstatus.LAGER, runde=2)
            return
        raise

    with transaction.atomic():
        if not _overgang(jobb, Jobbstatus.SJEKKER, status=Jobbstatus.FERDIG):
            return
        quiz = Quiz.objects.create(
            notat_id=jobb.notat_id,
            jobb=jobb,
            vanskelighetsgrad=jobb.vanskelighetsgrad,
            sprak=utkast.sprak,
            modell=utkast.modell,
            prompt_versjon=utkast.prompt_versjon,
            forhandslagret=utkast.forhandslagret,
        )
        for utkast_sporsmal in utkast.sporsmal:
            sporsmal = Sporsmal.objects.create(
                quiz=quiz,
                tekst=utkast_sporsmal.tekst,
                begrunnelse=utkast_sporsmal.begrunnelse,
            )
            Alternativ.objects.bulk_create(
                Alternativ(
                    sporsmal=sporsmal,
                    tekst=alternativ.tekst,
                    er_riktig=alternativ.er_riktig,
                )
                for alternativ in utkast_sporsmal.alternativer
            )


_STEG = {
    Jobbstatus.LESER: _leser,
    Jobbstatus.LAGER: _lager,
    Jobbstatus.SJEKKER: _sjekker,
}


def _feilet(jobb, fra, kode):
    _overgang(jobb, fra, status=Jobbstatus.FEILET, feilkode=kode)
    logger.warning("Genereringsjobb %s feilet med koden %s.", jobb.pk, kode)


def kjor_steg(jobb_id):
    """Kjører ett steg av jobben. Gir `True` hvis et steg ble kjørt.

    Jobben tas med `i_gang`, så to samtidige kall aldri kjører samme steg. Er
    jobben ferdig, feilet eller i gang et annet sted, gjøres ingenting.
    """
    jobb = Genereringsjobb.objects.filter(pk=jobb_id).first()
    if jobb is None or jobb.status in SLUTTSTATUSER:
        return False
    # Setter jobben til `feilet`/`timeout` hvis fristen er ute.
    aktiv_jobb(jobb.notat_id)

    status = jobb.status
    tatt = Genereringsjobb.objects.filter(
        pk=jobb_id, status=status, i_gang=False
    ).update(i_gang=True)
    if not tatt:
        return False
    try:
        jobb = Genereringsjobb.objects.select_related("notat").get(pk=jobb_id)
        _STEG[status](jobb)
    except ki.KIFeil as feil:
        _feilet(jobb, status, feil.kode)
    except Exception as feil:  # noqa: BLE001 Brukeren skal ikke bli stående på S8.
        logger.error(
            "Genereringsjobb %s fikk en uventet feil i steget %s: %s.",
            jobb_id,
            status,
            type(feil).__name__,
        )
        _feilet(jobb, status, Feilkode.API_FEIL)
    finally:
        Genereringsjobb.objects.filter(pk=jobb_id).update(i_gang=False)
    return True


def generer_synkront(notat, vanskelighetsgrad, antall):
    """Lager en quiz uten HTMX, med de samme stegene (brukes av seed).

    Gir `Quiz`, eller hever `KIFeil(feilkode)` når jobben feiler.
    """
    jobb = opprett_jobb(notat, vanskelighetsgrad, antall)
    for _ in range(MAKS_STEG):
        kjor_steg(jobb.pk)
        jobb.refresh_from_db()
        if jobb.status == Jobbstatus.FERDIG:
            return Quiz.objects.get(jobb=jobb)
        if jobb.status == Jobbstatus.FEILET:
            raise ki.KIFeil(jobb.feilkode or Feilkode.API_FEIL)
    raise ki.KIFeil(Feilkode.API_FEIL, f"jobb {jobb.pk} ble ikke ferdig")
