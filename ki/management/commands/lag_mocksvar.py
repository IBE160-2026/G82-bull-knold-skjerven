"""Lager mock-svarene i `ki/mock/` fra testdokumentene med ekte modell (AD-12, NFR-9).

Krever gruppas API-nøkkel. Skriver bare ut varighet per kall, aldri innhold.
Filene skrives først når alle genereringene er sjekket, så mappen aldri blir halvferdig.
"""

import json
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ki import KIFeil, er_testmodus, generer, generering, les_fil, sjekk
from ki.fil import TYPER

ANTALL = generering.MAKS_ANTALL
TIMEOUT = 300
STANDARD = "html-struktur-og-semantikk.pdf"
# Feil som kan gå over av seg selv. `api_nokkel` og `for_stor` gjør ikke det.
NYTT_FORSOK = frozenset({"format", "timeout", "api_feil"})


class Command(BaseCommand):
    help = "Lager mock-svar fra testdokumentene med ekte modell. Krever API-nøkkel."

    def handle(self, *args, **options):
        if er_testmodus():
            raise CommandError(
                "Testmodus er på. Sett ANTHROPIC_API_KEY og TESTMODUS=0 i .env først."
            )

        mappe = settings.BASE_DIR / "testdokumenter"
        dokumenter = sorted(
            sti for sti in mappe.iterdir() if sti.suffix.lower() in TYPER
        )
        if STANDARD not in {sti.name for sti in dokumenter}:
            raise CommandError(f"Fant ikke standarddokumentet {STANDARD} i {mappe}.")

        manifest = {"standard": _dokumentnavn(STANDARD), "filer": {}}
        svar = {}
        for sti in dokumenter:
            navn = _dokumentnavn(sti.name)
            innhold = les_fil(sti)
            manifest["filer"][innhold.sha256] = navn
            for nivaa in generering.VANSKELIGHETSGRADER:
                svar[navn, nivaa] = self._generer_sjekket(innhold, navn, nivaa)

        mock = generering.MOCK_MAPPE
        for (navn, nivaa), utkast in svar.items():
            _skriv_json(mock / navn / f"{nivaa}.json", _som_mockfil(utkast))
        _skriv_json(mock / "manifest.json", manifest)
        self.stdout.write(
            self.style.SUCCESS(
                f"Skrev {len(svar)} mock-filer og manifest.json i {mock}."
            )
        )

    def _generer_sjekket(self, innhold, navn, nivaa):
        """Ett nytt forsøk ved format, timeout og api_feil. Andre feil stopper kommandoen."""
        for forsok in (1, 2):
            start = time.monotonic()
            try:
                raatt = generer(innhold, nivaa, ANTALL, timeout=TIMEOUT)
                utkast = sjekk(raatt.tekst, ANTALL)
            except KIFeil as feil:
                varighet = time.monotonic() - start
                self.stdout.write(
                    f"{navn} / {nivaa}, forsøk {forsok}: {feil.kode} etter {varighet:.1f} s"
                )
                if feil.kode in NYTT_FORSOK and forsok == 1:
                    continue
                raise CommandError(
                    f"{navn} / {nivaa} feilet med {feil.kode}. Ingen filer er skrevet."
                ) from feil
            varighet = time.monotonic() - start
            self.stdout.write(f"{navn} / {nivaa}, forsøk {forsok}: {varighet:.1f} s")
            return utkast
        raise AssertionError("uoppnåelig")


def _dokumentnavn(filnavn):
    """Mappenavnet for et testdokument: filnavnet uten endelse."""
    return filnavn.rsplit(".", 1)[0]


def _som_mockfil(utkast):
    return {
        "sprak": utkast.sprak,
        "modell": utkast.modell,
        "prompt_versjon": utkast.prompt_versjon,
        "sporsmal": [
            {
                "tekst": s.tekst,
                "begrunnelse": s.begrunnelse,
                "alternativer": [
                    {"tekst": a.tekst, "er_riktig": a.er_riktig} for a in s.alternativer
                ],
            }
            for s in utkast.sporsmal
        ],
    }


def _skriv_json(sti, data):
    sti.parent.mkdir(parents=True, exist_ok=True)
    # Fast LF og UTF-8, så filene er like på alle maskiner (`ki/mock/** -text`).
    sti.write_bytes(
        (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
