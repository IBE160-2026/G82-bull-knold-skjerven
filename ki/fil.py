"""Leser en notatfil (FR-9). PDF sendes hel. Fra DOCX og TXT hentes teksten."""

import hashlib
import io
from dataclasses import dataclass
from pathlib import Path

import docx

from .feil import KIFeil

TYPER = {".pdf": "pdf", ".docx": "docx", ".txt": "txt"}


@dataclass(frozen=True)
class Innhold:
    """`sha256` er hex-digest av filens bytes. `data` er bytes for PDF og tekst ellers."""

    sha256: str
    type: str
    data: bytes | str


def les_fil(sti):
    """Leser filen på `sti` og gir `Innhold`. Hever `KIFeil` hvis filen ikke kan brukes."""
    sti = Path(sti)
    filtype = TYPER.get(sti.suffix.lower())
    if filtype is None:
        raise KIFeil("api_feil", "filtypen støttes ikke")
    try:
        raa = sti.read_bytes()
    except OSError as feil:
        raise KIFeil("api_feil", "filen kunne ikke leses") from feil

    sha256 = hashlib.sha256(raa).hexdigest()
    if filtype == "pdf":
        return Innhold(sha256, filtype, raa)

    # Teksten hentes fra de samme bytene som hashen, ikke fra en ny lesing av filen.
    tekst = _docx_tekst(raa) if filtype == "docx" else _txt_tekst(raa)
    if not tekst.strip():
        raise KIFeil("for_lite_innhold", "filen har ingen tekst")
    return Innhold(sha256, filtype, tekst)


def _docx_tekst(raa):
    try:
        dokument = docx.Document(io.BytesIO(raa))
    except Exception as feil:
        # python-docx kan feile på mange måter med en ødelagt fil (zip, XML, deler).
        raise KIFeil("api_feil", "DOCX-filen kunne ikke åpnes") from feil
    return "\n".join(avsnitt.text for avsnitt in dokument.paragraphs)


def _txt_tekst(raa):
    try:
        return raa.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raa.decode("cp1252", errors="replace")
