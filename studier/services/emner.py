"""Emner (FR-4). Eneste sted som oppretter `Emne` (AD-1)."""

from studier.models import Emne


def opprett_emne(eier, navn):
    """Lagrer et nytt emne for `eier`. Avviser tomt og for langt navn selv om skjemaet er omgått."""
    navn = navn.strip()
    if not navn or len(navn) > 100:
        raise ValueError("Ugyldig navn for emne.")
    return Emne.objects.create(eier=eier, navn=navn)


def gi_nytt_navn(emne, navn):
    """Endrer navnet på `emne`. Notater, quizer og historikk er uendret."""
    navn = navn.strip()
    if not navn or len(navn) > 100:
        raise ValueError("Ugyldig navn for emne.")
    emne.navn = navn
    emne.save(update_fields=["navn"])
    return emne
