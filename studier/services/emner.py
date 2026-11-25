"""Emner (FR-4–FR-6). Eneste sted som oppretter, endrer eller sletter `Emne` (AD-1, AD-14)."""

import logging

from django.core.files.storage import default_storage
from django.db import transaction
from django.http import Http404

from studier.models import Emne, Notat

logger = logging.getLogger(__name__)


def _rens_navn(navn):
    """Trimmer og avviser tomt eller for langt navn. Skjemaet sjekker det samme først."""
    navn = navn.strip()
    if not navn or len(navn) > 100:
        raise ValueError("Ugyldig navn for emne.")
    return navn


def opprett_emne(eier, navn):
    """Lagrer et nytt emne for `eier`. Avviser tomt og for langt navn selv om skjemaet er omgått."""
    return Emne.objects.create(eier=eier, navn=_rens_navn(navn))


def gi_nytt_navn(emne, navn):
    """Endrer navnet på `emne`. Notater, quizer og historikk er uendret."""
    navn = _rens_navn(navn)
    # Én UPDATE. Hvis emnet er slettet mellom henting og lagring, gir det 404 og ikke 500.
    if not Emne.objects.filter(pk=emne.pk).update(navn=navn):
        raise Http404("Fant ikke siden.")
    emne.navn = navn
    return emne


def _slett_filer(filnavn):
    """Sletter filene etter commit. En fil som mangler eller ikke kan slettes, hoppes over."""
    for navn in filnavn:
        try:
            default_storage.delete(navn)
        except Exception:  # Én feil skal aldri stoppe resten av filene.
            logger.warning("Kunne ikke slette fila %s.", navn, exc_info=True)


def slett_emne(emne):
    """Sletter `emne` med alt innhold (cascade), og filene etter commit (AD-14).

    Eneste sted som sletter `Notat`, `Quiz`, `Okt` eller `Feilbankrad`.
    """
    with transaction.atomic():
        filnavn = [
            navn
            for navn in Notat.objects.filter(emne=emne).values_list("fil", flat=True)
            if navn
        ]
        Emne.objects.filter(pk=emne.pk).delete()
        transaction.on_commit(lambda: _slett_filer(filnavn), robust=True)
