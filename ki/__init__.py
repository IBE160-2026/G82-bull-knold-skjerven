"""
KI-adapteren: fil inn, sjekket quizutkast ut.

`ki` kjenner ikke databasen og importerer aldri fra `studier` eller `kontoer`.
`er_testmodus()` er eneste kilde til om appen kjører i testmodus (AD-12).
"""

from django.conf import settings

from .feil import KIFeil
from .fil import Innhold, les_fil
from .format import QuizUtkast, sjekk
from .generering import PROMPT_VERSJON, RaattSvar, generer, visningsnavn

__all__ = [
    "PROMPT_VERSJON",
    "Innhold",
    "KIFeil",
    "QuizUtkast",
    "RaattSvar",
    "er_testmodus",
    "generer",
    "les_fil",
    "sjekk",
    "tving_testmodus",
    "visningsnavn",
]

_SANNE_VERDIER = frozenset({"1", "true", "yes", "on"})

_tvunget = False


def tving_testmodus():
    """Slår testmodus på for resten av prosessen, uansett miljø. Brukes av tester og seed."""
    global _tvunget
    _tvunget = True


def er_testmodus():
    """Sann når testmodus er tvunget, `TESTMODUS` er sann, eller API-nøkkelen mangler."""
    if _tvunget:
        return True
    verdi = str(getattr(settings, "TESTMODUS", "") or "").strip().lower()
    if verdi in _SANNE_VERDIER:
        return True
    nokkel = str(getattr(settings, "ANTHROPIC_API_KEY", "") or "").strip()
    return not nokkel
