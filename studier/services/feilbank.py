"""Feilbanken (FR-21, FR-23, AD-2, AD-3). Eneste sted som oppretter eller endrer `Feilbankrad`.

Et spørsmål er i feilbanken når raden finnes og `laert_tidspunkt` er tom. Det
blir lært etter `RIKTIGE_FOR_LAERT` riktige svar på rad. Feil svar nullstiller
telleren, også for et lært spørsmål, som da kommer tilbake. Rader slettes aldri
(bare med emnet, AD-14). Kalles bare fra leveringen (`lever_okt`, story 3.3).
"""

from django.db import transaction
from django.utils import timezone

from studier.models import Feilbankrad, Hendelse

RIKTIGE_FOR_LAERT = 2


def registrer_svar(sporsmal, *, riktig) -> Hendelse:
    """Registrerer ett svar på `sporsmal` mot feilbanken og gir hendelsen (AD-2).

    Gir `lagt_i`, `nullstilt`, `opp`, `laert` eller `ingen`. `riktig` må gis som
    nøkkelord, så sant og usant ikke byttes om. Spørsmål identifiseres bare av
    ID, så lik tekst i en annen quiz påvirkes ikke (AD-5).
    """
    with transaction.atomic():
        rad = Feilbankrad.objects.select_for_update().filter(sporsmal=sporsmal).first()
        if rad is None:
            if riktig:
                return Hendelse.INGEN
            rad, opprettet = Feilbankrad.objects.get_or_create(
                sporsmal=sporsmal, defaults={"riktige_pa_rad": 0}
            )
            if opprettet:
                return Hendelse.LAGT_I
            # Bare på en database med radlåser: raden ble laget av et samtidig
            # kall. Med SQLite i IMMEDIATE-modus kjører skrivinger én om gangen.

        if not riktig:
            rad.riktige_pa_rad = 0
            rad.laert_tidspunkt = None
            rad.save(update_fields=["riktige_pa_rad", "laert_tidspunkt"])
            return Hendelse.NULLSTILT

        if rad.laert_tidspunkt is not None:
            return Hendelse.INGEN

        rad.riktige_pa_rad += 1
        if rad.riktige_pa_rad >= RIKTIGE_FOR_LAERT:
            rad.laert_tidspunkt = timezone.now()
            rad.save(update_fields=["riktige_pa_rad", "laert_tidspunkt"])
            return Hendelse.LAERT
        rad.save(update_fields=["riktige_pa_rad"])
        return Hendelse.OPP


def fasit_synlig(sporsmal):
    """Sann når spørsmålet er lært: raden har `laert_tidspunkt` (AD-20). Bare lesing."""
    return Feilbankrad.objects.filter(
        sporsmal=sporsmal, laert_tidspunkt__isnull=False
    ).exists()
