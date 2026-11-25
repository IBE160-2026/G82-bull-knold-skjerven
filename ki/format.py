"""Sjekker et rått svar fra modellen eller et mock-svar (FR-13). Feltene er låst av AD-11."""

import json
from dataclasses import dataclass

from .feil import KIFeil

ANTALL_ALTERNATIVER = 3


@dataclass(frozen=True)
class Alternativ:
    tekst: str
    er_riktig: bool


@dataclass(frozen=True)
class Sporsmal:
    tekst: str
    begrunnelse: str
    alternativer: tuple[Alternativ, ...]


@dataclass(frozen=True)
class QuizUtkast:
    sprak: str
    modell: str
    prompt_versjon: str
    forhandslagret: bool
    sporsmal: tuple[Sporsmal, ...]


def sjekk(raatt, antall):
    """Gir `QuizUtkast` fra JSON-teksten `raatt`, eller hever `KIFeil("format")`."""
    try:
        data = json.loads(raatt)
    except (TypeError, ValueError, RecursionError) as feil:
        raise KIFeil("format", "svaret er ikke gyldig JSON") from feil
    if not isinstance(data, dict):
        raise KIFeil("format", "svaret er ikke et JSON-objekt")

    forhandslagret = data.get("forhandslagret", False)
    if not isinstance(forhandslagret, bool):
        raise KIFeil("format", "forhandslagret er ikke true eller false")

    liste = _liste(data, "sporsmal", "svaret")
    if len(liste) != antall:
        raise KIFeil("format", f"{len(liste)} spørsmål, ventet {antall}")
    sporsmal = tuple(_sporsmal(s, nr) for nr, s in enumerate(liste, start=1))
    _sjekk_ulike([s.tekst for s in sporsmal], "to spørsmål er like")

    return QuizUtkast(
        sprak=_tekst(data, "sprak", "svaret"),
        modell=_tekst(data, "modell", "svaret"),
        prompt_versjon=_tekst(data, "prompt_versjon", "svaret"),
        forhandslagret=forhandslagret,
        sporsmal=sporsmal,
    )


def _sporsmal(data, nr):
    hvor = f"spørsmål {nr}"
    if not isinstance(data, dict):
        raise KIFeil("format", f"{hvor} er ikke et objekt")
    liste = _liste(data, "alternativer", hvor)
    if len(liste) != ANTALL_ALTERNATIVER:
        raise KIFeil(
            "format",
            f"{hvor} har {len(liste)} alternativer, ventet {ANTALL_ALTERNATIVER}",
        )
    alternativer = tuple(
        _alternativ(a, f"{hvor}, alternativ {i}") for i, a in enumerate(liste, start=1)
    )
    riktige = sum(a.er_riktig for a in alternativer)
    if riktige != 1:
        raise KIFeil("format", f"{hvor} har {riktige} riktige alternativer, ventet 1")
    _sjekk_ulike([a.tekst for a in alternativer], f"{hvor} har like alternativer")
    return Sporsmal(
        tekst=_tekst(data, "tekst", hvor),
        begrunnelse=_tekst(data, "begrunnelse", hvor),
        alternativer=alternativer,
    )


def _alternativ(data, hvor):
    if not isinstance(data, dict):
        raise KIFeil("format", f"{hvor} er ikke et objekt")
    er_riktig = data.get("er_riktig")
    if not isinstance(er_riktig, bool):
        raise KIFeil("format", f"{hvor}: er_riktig mangler eller er ikke true/false")
    return Alternativ(tekst=_tekst(data, "tekst", hvor), er_riktig=er_riktig)


def _tekst(data, felt, hvor):
    verdi = data.get(felt)
    if not isinstance(verdi, str) or not verdi.strip():
        raise KIFeil("format", f"{hvor}: {felt} mangler eller er tomt")
    return verdi.strip()


def _liste(data, felt, hvor):
    verdi = data.get(felt)
    if not isinstance(verdi, list):
        raise KIFeil("format", f"{hvor}: {felt} mangler eller er ikke en liste")
    return verdi


def _sjekk_ulike(tekster, melding):
    # Mellomrom inni teksten teller ikke: «Riktig  1» og «riktig 1» er like.
    normalisert = [" ".join(t.split()).casefold() for t in tekster]
    if len(set(normalisert)) != len(normalisert):
        raise KIFeil("format", melding)
