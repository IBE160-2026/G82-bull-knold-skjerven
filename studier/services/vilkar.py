"""Vilkårene i FR-7. Eneste sted som skriver `Bruker.vilkar_godtatt` (AD-1, AD-23)."""

from django.contrib.auth import get_user_model
from django.utils import timezone


def godta_vilkar(bruker):
    """Lagrer når `bruker` godtok vilkårene. Et tidspunkt som finnes, beholdes."""
    naa = timezone.now()
    # Betinget oppdatering, slik at et tidspunkt i databasen aldri overskrives,
    # heller ikke ved to samtidige forespørsler eller et utdatert objekt.
    endret = (
        get_user_model()
        .objects.filter(pk=bruker.pk, vilkar_godtatt__isnull=True)
        .update(vilkar_godtatt=naa)
    )
    if endret:
        bruker.vilkar_godtatt = naa
    else:
        bruker.refresh_from_db(fields=["vilkar_godtatt"])
