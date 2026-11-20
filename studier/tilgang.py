"""
Eierhjelpere (AD-8). Alle ID-er fra URL, GET og POST slås opp her.

Veien fra hver modell til eieren står bare i `EIERVEI`. Et rått pk-oppslag i
views er forbudt.
"""

from django.core.exceptions import ValidationError
from django.http import Http404

from studier.models import (
    Alternativ,
    Emne,
    Feilbankrad,
    Genereringsjobb,
    Notat,
    Okt,
    Quiz,
    Sporsmal,
    Svar,
)

EIERVEI = {
    Emne: "eier",
    Notat: "emne__eier",
    Genereringsjobb: "notat__emne__eier",
    Quiz: "notat__emne__eier",
    Sporsmal: "quiz__notat__emne__eier",
    Alternativ: "sporsmal__quiz__notat__emne__eier",
    Okt: "notat__emne__eier",
    Svar: "okt__notat__emne__eier",
    Feilbankrad: "sporsmal__quiz__notat__emne__eier",
}


def _eiervei(modell):
    try:
        return EIERVEI[modell]
    except KeyError, TypeError:
        navn = getattr(modell, "__name__", repr(modell))
        raise ValueError(
            f"{navn} har ingen eiervei i studier.tilgang.EIERVEI. "
            "Legg modellen til der før den brukes med hent_egen eller egne."
        ) from None


def egne(modell, bruker):
    """Queryset med bare radene som tilhører `bruker`."""
    vei = _eiervei(modell)
    if not getattr(bruker, "is_authenticated", False):
        return modell.objects.none()
    return modell.objects.filter(**{vei: bruker})


def hent_egen(modell, pk, bruker):
    """Brukerens objekt med denne pk-en. `Http404` for andres data og ugyldige ID-er."""
    queryset = egne(modell, bruker)  # Ukjent modell feiler her, utenfor try.
    try:
        return queryset.get(pk=pk)
    except modell.DoesNotExist, ValueError, TypeError, ValidationError:
        raise Http404("Fant ikke siden.") from None
