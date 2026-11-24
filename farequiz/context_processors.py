"""Felles variabler for alle maler."""

from ki import er_testmodus


def testmodus(request):
    """Sann når testmodus er på. Eneste kilde er `ki.er_testmodus()`."""
    return {"testmodus": er_testmodus()}
