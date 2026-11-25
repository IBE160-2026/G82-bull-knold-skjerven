"""Malfiltre for dekningsgraden (AD-4: avrundingen skjer bare i malen)."""

from decimal import ROUND_HALF_UP, Decimal

from django import template

register = template.Library()


@register.filter
def hel_prosent(verdi):
    """Andelen `verdi` (0–1) som hel prosent, med ,5 opp. Gir et heltall.

    Aldri 100 før `verdi` er nøyaktig 1 (da 99), og aldri 0 når `verdi` er over 0
    (da 1). Ikke `widthratio`: den bruker `round()`, som runder ,5 til partall.
    Verdien kuttes først til 9 desimaler, så flyttallsfeil som 0,3 × 0,75 =
    0,22499999999999998 regnes som 0,225 og gir 23.
    """
    if verdi is None or verdi == "":
        return ""
    andel = Decimal(str(verdi)).quantize(Decimal("0.000000001"), ROUND_HALF_UP)
    prosent = int((andel * 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    if prosent >= 100 and verdi < 1:
        return 99
    if prosent <= 0 and verdi > 0:
        return 1
    return prosent
