"""Emner (FR-4). Eneste sted som oppretter eller endrer `Emne` (AD-1)."""

from django.http import Http404

from studier.models import Emne


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
