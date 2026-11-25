"""Melde et spørsmål som feil eller uklart (FR-31). Eneste sted som skriver `Sporsmal.meldt_tidspunkt`.

Et meldt spørsmål er ute av feilbanken, dekningsgraden og nye økter. Utvalgene
bruker `Sporsmal.objects.ikke_meldt()`. Meldingen kan ikke angres.
"""

import logging

from django.utils import timezone

from studier.models import Sporsmal

logger = logging.getLogger(__name__)


def meld_sporsmal(sporsmal) -> bool:
    """Melder `sporsmal` som feil. Gir `True` hvis dette kallet meldte, `False` hvis det alt var meldt.

    Et tidspunkt som finnes, beholdes. `sporsmal` må alt være hentet med
    `hent_egen` eller fra en egen økt, som sikrer eieren.
    """
    naa = timezone.now()
    # Betinget oppdatering, slik at tidspunktet aldri overskrives, heller ikke
    # ved to samtidige forespørsler eller et utdatert objekt.
    endret = Sporsmal.objects.filter(
        pk=sporsmal.pk, meldt_tidspunkt__isnull=True
    ).update(meldt_tidspunkt=naa)
    if not endret:
        sporsmal.refresh_from_db(fields=["meldt_tidspunkt"])
        return False
    sporsmal.meldt_tidspunkt = naa
    logger.info(
        "Spørsmål %s i quiz %s meldt som feil (modell %s).",
        sporsmal.pk,
        sporsmal.quiz_id,
        sporsmal.quiz.modell,
    )
    return True
