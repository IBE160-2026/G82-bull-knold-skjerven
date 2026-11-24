"""Emner (FR-4). Eneste sted som oppretter `Emne` (AD-1)."""

from studier.models import Emne


def opprett_emne(eier, navn):
    """Lagrer et nytt emne for `eier`. Navnet må være godkjent av `EmneForm`."""
    return Emne.objects.create(eier=eier, navn=navn.strip())
