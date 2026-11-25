"""Notater (FR-7, FR-8). Eneste sted som lager `Notat` (AD-1, AD-14).

Originalfilene lagres under `MEDIA_ROOT` og serveres aldri over HTTP (AD-8).
"""

import io
import logging
import zipfile
from pathlib import PurePosixPath

import docx
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.storage import default_storage
from django.db import transaction
from django.http import Http404

from farequiz import feilmeldinger
from studier.models import Emne, Filtype, Notat

logger = logging.getLogger(__name__)

MAKS_STORRELSE = 5 * 1024 * 1024
ENDELSER = {
    ".pdf": Filtype.PDF,
    ".docx": Filtype.DOCX,
    ".txt": Filtype.TXT,
}


def _originalnavn(opplastet_fil):
    """Filnavnet uten sti, også når nettleseren sender en Windows-sti."""
    return PurePosixPath(str(opplastet_fil.name or "").replace("\\", "/")).name


def _les_bytes(opplastet_fil):
    opplastet_fil.seek(0)
    raa = opplastet_fil.read()
    opplastet_fil.seek(0)
    return raa


def _docx_tekst(raa):
    """Teksten i avsnittene, slik `ki` leser den. `None` hvis filen ikke er en DOCX."""
    try:
        with zipfile.ZipFile(io.BytesIO(raa)) as arkiv:
            if "word/document.xml" not in arkiv.namelist():
                return None
        dokument = docx.Document(io.BytesIO(raa))
    except Exception:  # noqa: BLE001 Ødelagt zip, XML eller deler gir mange ulike feil.
        return None
    return "\n".join(avsnitt.text for avsnitt in dokument.paragraphs)


def _txt_tekst(raa):
    """Teksten som UTF-8 med cp1252 som reserve. `None` hvis ingen av dem passer."""
    # NUL finnes ikke i vanlig tekst, men i binærfiler og UTF-16.
    if b"\x00" in raa:
        return None
    for koding in ("utf-8-sig", "cp1252"):
        try:
            return raa.decode(koding)
        except UnicodeDecodeError:
            continue
    return None


def valider_fil(opplastet_fil):
    """Sjekker filen og gir `Filtype`. Hever `ValidationError` med brukerteksten."""
    if not opplastet_fil:
        raise ValidationError(feilmeldinger.VELG_FIL, code="required")
    if opplastet_fil.size > MAKS_STORRELSE:
        raise ValidationError(feilmeldinger.FIL_FOR_STOR, code="for_stor")
    filtype = ENDELSER.get(PurePosixPath(_originalnavn(opplastet_fil)).suffix.lower())
    if filtype is None:
        raise ValidationError(feilmeldinger.FIL_FEIL_FORMAT, code="format")
    if opplastet_fil.size == 0:
        raise ValidationError(feilmeldinger.FIL_TOM, code="tom")

    raa = _les_bytes(opplastet_fil)
    if not raa:
        raise ValidationError(feilmeldinger.FIL_TOM, code="tom")
    if filtype == Filtype.PDF:
        if not raa.startswith(b"%PDF-"):
            raise ValidationError(feilmeldinger.FIL_FEIL_FORMAT, code="format")
        return filtype

    tekst = _docx_tekst(raa) if filtype == Filtype.DOCX else _txt_tekst(raa)
    if tekst is None:
        raise ValidationError(feilmeldinger.FIL_FEIL_FORMAT, code="format")
    if not tekst.strip():
        raise ValidationError(feilmeldinger.FIL_TOM, code="tom")
    return filtype


def _slett_fil(navn):
    try:
        default_storage.delete(navn)
    except Exception:  # Feilen som utløste slettingen er viktigst.
        logger.warning("Kunne ikke slette fila %s.", navn, exc_info=True)


def last_opp(emne, opplastet_fil, bruker):
    """Lagrer filen og et nytt `Notat` i `emne`. Eneste sted som lager `Notat`.

    Hever `PermissionDenied` uten godtatte vilkår (FR-7, AD-23), `ValidationError`
    for en ugyldig fil og `Http404` hvis emnet ikke finnes eller ikke er brukerens.
    Feiler noe etter at filen er skrevet, slettes filen før feilen hever seg videre.
    """
    if not getattr(bruker, "vilkar_godtatt", None):
        raise PermissionDenied("Vilkårene er ikke godtatt.")
    filtype = valider_fil(opplastet_fil)
    originalnavn = _originalnavn(opplastet_fil)[:255]

    lagret = None
    try:
        with transaction.atomic():
            try:
                laast = Emne.objects.select_for_update().get(pk=emne.pk, eier=bruker)
            except Emne.DoesNotExist:
                raise Http404("Fant ikke siden.") from None
            notat = Notat(
                emne=laast,
                originalnavn=originalnavn,
                filtype=filtype,
                storrelse=opplastet_fil.size,
            )
            opplastet_fil.seek(0)
            notat.fil.save(f"notat.{filtype}", opplastet_fil, save=False)
            lagret = notat.fil.name
            notat.save()
    except BaseException:
        if lagret:
            _slett_fil(lagret)
        raise
    return notat
