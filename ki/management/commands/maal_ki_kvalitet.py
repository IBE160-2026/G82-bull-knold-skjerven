"""Måler KI-kvaliteten (SM-2, SM-4) og genereringstiden (FR-15, NFR-7) mot ekte modell.

Krever gruppas API-nøkkel og koster API-kall. Kjører de fem testdokumentene på
alle tre nivåer og måler tiden for 30 spørsmål fra tekst-PDF-en. Bruker `generer`
og `sjekk` slik appen gjør. En `KIFeil` i ett kall føres i rapporten og stopper
ikke kjøringen.

Skriver bare ut dokument, nivå, resultat og tid per kall, aldri innhold. Rapporten
skrives først når alle kallene er ferdige, så det aldri ligger en halvferdig rapport.
Den inneholder spørsmålene modellen laget, aldri filinnholdet eller API-nøkkelen.
"""

import html
import re
import statistics
import time
from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.test import override_settings
from django.utils import timezone

from ki import KIFeil, er_testmodus, generer, generering, les_fil, sjekk
from ki.fil import TYPER

STANDARD_ANTALL = 10
STANDARD_RUNDER = 3
EFFORT_VALG = ("low", "medium", "high")
TIMEOUT = 300
TIDSDOKUMENT = "html-struktur-og-semantikk.pdf"
TIDSNIVAA = "middels"
TIDSANTALL = generering.MAKS_ANTALL
# Samme frist som `TIDSFRIST` i `studier.services.generering` (FR-15). `ki`
# importerer aldri fra `studier`, så verdien står også her.
FRIST = 120
# Ventet språk per testdokument (testdokumenter/KILDER.md). Resten er bokmål.
SPRAK = {"javascript-og-dom.txt": "en"}
STANDARD_SPRAK = "nb"
STANDARD_UT = Path("_bmad-output") / "implementation-artifacts" / "ki-kvalitet"


@dataclass(frozen=True)
class Resultat:
    """Ett kall. `utkast` er satt når svaret besto `sjekk`, ellers er `feilkode` satt."""

    dokument: str
    nivaa: str
    antall: int
    sekunder: float
    sprak_ventet: str
    feilkode: str = ""
    detalj: str = ""
    stoppgrunn: str = ""
    modell: str = ""
    utkast: object = None

    @property
    def ok(self):
        return not self.feilkode

    @property
    def resultat(self):
        return "OK" if self.ok else f"feil: {self.feilkode}"


class Command(BaseCommand):
    help = (
        "Måler KI-kvalitet og genereringstid med ekte modell og skriver en rapport "
        "for manuell vurdering. Krever API-nøkkel og koster API-kall."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--antall",
            type=int,
            default=STANDARD_ANTALL,
            help=f"Spørsmål per quiz i kvalitetskjøringen, "
            f"{generering.MIN_ANTALL}–{generering.MAKS_ANTALL} "
            f"(standard {STANDARD_ANTALL}).",
        )
        parser.add_argument(
            "--runder",
            type=int,
            default=STANDARD_RUNDER,
            help=f"Antall tidsmålinger med {TIDSANTALL} spørsmål "
            f"(standard {STANDARD_RUNDER}).",
        )
        parser.add_argument("--modell", help="Overstyrer KI_MODELL under kjøringen.")
        parser.add_argument(
            "--effort",
            choices=EFFORT_VALG,
            help="Overstyrer EFFORT under kjøringen.",
        )
        parser.add_argument(
            "--ut",
            help=f"Mappen rapporten skrives til (standard {STANDARD_UT.as_posix()}/).",
        )

    def handle(self, *args, **options):
        if er_testmodus():
            raise CommandError(
                "Testmodus er på. Sett ANTHROPIC_API_KEY og TESTMODUS=0 i .env først."
            )
        valg = _sjekk_valg(options)
        dokumenter = _les_testdokumenter()

        modell_patch = (
            override_settings(KI_MODELL=valg["modell"])
            if valg["modell"]
            else nullcontext()
        )
        gammel_effort = generering.EFFORT
        try:
            if valg["effort"]:
                generering.EFFORT = valg["effort"]
            with modell_patch:
                modell_valgt = settings.KI_MODELL
                effort = generering.EFFORT
                kvalitet = [
                    self._kall(navn, innhold, sprak, nivaa, valg["antall"])
                    for navn, innhold, sprak in dokumenter
                    for nivaa in generering.VANSKELIGHETSGRADER
                ]
                navn, innhold, sprak = next(
                    d for d in dokumenter if d[0] == _dokumentnavn(TIDSDOKUMENT)
                )
                tider = [
                    self._kall(navn, innhold, sprak, TIDSNIVAA, TIDSANTALL, runde=runde)
                    for runde in range(1, valg["runder"] + 1)
                ]
        finally:
            generering.EFFORT = gammel_effort

        naa = timezone.localtime()
        rapport = _rapport(
            naa=naa,
            modell_valgt=modell_valgt,
            effort=effort,
            valg=valg,
            kvalitet=kvalitet,
            tider=tider,
        )
        sti = valg["ut"] / (
            f"ki-kvalitet-{naa:%Y-%m-%d-%H-%M-%S}-{_filnavn(modell_valgt)}"
            f"-{_filnavn(effort)}.md"
        )
        # Fast LF og UTF-8, så rapporten er lik på alle maskiner.
        sti.write_bytes(rapport.encode("utf-8"))
        self.stdout.write(self.style.SUCCESS(f"Skrev rapporten {sti}"))

    def _kall(self, navn, innhold, sprak, nivaa, antall, runde=None):
        raatt = None
        start = time.monotonic()
        try:
            raatt = generer(innhold, nivaa, antall, timeout=TIMEOUT)
            utkast = sjekk(raatt.tekst, antall)
        except KIFeil as feil:
            resultat = Resultat(
                dokument=navn,
                nivaa=nivaa,
                antall=antall,
                sekunder=time.monotonic() - start,
                sprak_ventet=sprak,
                feilkode=feil.kode,
                # `detalj` har aldri filinnhold (KIFeil), bare regelen som brøt.
                detalj=feil.detalj,
                stoppgrunn=raatt.stoppgrunn if raatt else "",
                modell=raatt.modell if raatt else "",
            )
        else:
            resultat = Resultat(
                dokument=navn,
                nivaa=nivaa,
                antall=antall,
                sekunder=time.monotonic() - start,
                sprak_ventet=sprak,
                stoppgrunn=raatt.stoppgrunn,
                modell=utkast.modell,
                utkast=utkast,
            )
        hva = f"tid, runde {runde}: " if runde else ""
        self.stdout.write(
            f"{hva}{navn} / {nivaa} / {antall}: {resultat.resultat}, "
            f"{resultat.sekunder:.1f} s"
        )
        return resultat


def _sjekk_valg(options):
    """Sjekker valgene før noe kall, så et ugyldig valg aldri koster API-kall."""
    antall = options.get("antall", STANDARD_ANTALL)
    if not _er_heltall(antall) or not (
        generering.MIN_ANTALL <= antall <= generering.MAKS_ANTALL
    ):
        raise CommandError(
            f"--antall må være {generering.MIN_ANTALL}–{generering.MAKS_ANTALL}, "
            f"fikk {antall!r}."
        )
    runder = options.get("runder", STANDARD_RUNDER)
    if not _er_heltall(runder) or runder < 1:
        raise CommandError(f"--runder må være minst 1, fikk {runder!r}.")
    effort = options.get("effort")
    if effort is not None and effort not in EFFORT_VALG:
        raise CommandError(
            f"--effort må være én av {', '.join(EFFORT_VALG)}, fikk {effort!r}."
        )
    modell = options.get("modell")
    if modell is not None and (not isinstance(modell, str) or not modell.strip()):
        raise CommandError("--modell kan ikke være tom.")
    ut = options.get("ut")
    ut = Path(ut) if ut else Path(settings.BASE_DIR) / STANDARD_UT
    # Mappen lages nå, så en ugyldig `--ut` oppdages før de betalte kallene.
    try:
        ut.mkdir(parents=True, exist_ok=True)
    except OSError as feil:
        raise CommandError(f"--ut: kan ikke lage mappen {ut} ({feil}).") from feil
    if not ut.is_dir():
        raise CommandError(f"--ut: {ut} er ikke en mappe.")
    return {
        "antall": antall,
        "runder": runder,
        "effort": effort,
        "modell": modell.strip() if modell else None,
        "ut": ut,
    }


def _er_heltall(verdi):
    return isinstance(verdi, int) and not isinstance(verdi, bool)


def _les_testdokumenter():
    """Leser alle testdokumentene før første kall. Gir (navn, innhold, ventet språk)."""
    mappe = Path(settings.BASE_DIR) / "testdokumenter"
    stier = sorted(sti for sti in mappe.iterdir() if sti.suffix.lower() in TYPER)
    if TIDSDOKUMENT not in {sti.name for sti in stier}:
        raise CommandError(f"Fant ikke tidsdokumentet {TIDSDOKUMENT} i {mappe}.")
    dokumenter = []
    for sti in stier:
        try:
            innhold = les_fil(sti)
        except KIFeil as feil:
            raise CommandError(
                f"Kunne ikke lese {sti.name} ({feil.kode}). Ingen kall er gjort."
            ) from feil
        sprak = SPRAK.get(sti.name, STANDARD_SPRAK)
        dokumenter.append((_dokumentnavn(sti.name), innhold, sprak))
    return dokumenter


def _dokumentnavn(filnavn):
    return filnavn.rsplit(".", 1)[0]


def _filnavn(modell):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", modell).strip("-") or "modell"


def _sprak_stemmer(ventet, faatt):
    # «nb-NO» regnes som «nb». Bare hovedkoden sammenlignes.
    return faatt.split("-", 1)[0].casefold() == ventet.casefold()


def _celle(tekst):
    """Gjør tekst trygg i en Markdown-tabell.

    `<`, `>` og `&` escapes utenfor kodespenn, så en tagg som <nav> ikke forsvinner
    når rapporten vises. Inni `kode` vises de som de er, og blir ikke escapet.
    `|` escapes og linjeskift blir <br>.
    """
    deler = re.split(r"(`[^`\n]*`)", str(tekst))
    tekst = "".join(
        del_
        if del_.startswith("`") and del_.endswith("`") and len(del_) > 1
        else html.escape(del_, quote=False)
        for del_ in deler
    )
    tekst = tekst.replace("|", "\\|")
    return re.sub(r"\r\n|\r|\n", "<br>", tekst).strip()


def _rad(*celler):
    return "| " + " | ".join(_celle(c) for c in celler) + " |"


def _sek(sekunder):
    return f"{sekunder:.1f} s"


def _rapport(*, naa, modell_valgt, effort, valg, kvalitet, tider):
    alle = [*kvalitet, *tider]
    modeller = sorted({r.modell for r in alle if r.modell})
    linjer = [
        "# KI-kvalitet og genereringstid",
        "",
        (
            "Laget av `uv run python manage.py maal_ki_kvalitet` (story 6.4). "
            "Resultatet føres i `ki-kvalitet-6-4.md`."
        ),
        "",
        "| | |",
        "|---|---|",
        _rad("Dato", f"{naa:%d.%m.%Y %H:%M}"),
        _rad("Modell valgt (`KI_MODELL`)", f"`{modell_valgt}`"),
        _rad(
            "Modell i svarene",
            ", ".join(f"`{m}`" for m in modeller) if modeller else "ingen svar",
        ),
        _rad("`PROMPT_VERSJON`", generering.PROMPT_VERSJON),
        _rad("`effort`", effort),
        _rad("`MAKS_TOKENS`", generering.MAKS_TOKENS),
        _rad("Timeout per kall", _sek(TIMEOUT)),
        _rad(
            "Valg",
            f"--antall {valg['antall']}, --runder {valg['runder']}, "
            f"--modell {valg['modell'] or '(KI_MODELL)'}, "
            f"--effort {valg['effort'] or '(EFFORT)'}",
        ),
        "",
        "## SM-4: form og språk",
        "",
        (
            "Sjekket automatisk med `ki.sjekk`: nøyaktig valgt antall, tre ulike "
            "alternativer, ett riktig og ingen like spørsmål. Stoppgrunnen "
            "`max_tokens` betyr at svaret ble kuttet av."
        ),
        "",
        _rad(
            "Dokument",
            "Nivå",
            "Resultat",
            "Detalj",
            "Antall",
            "Språk ventet / fått",
            "Modell",
            "Tid",
            "Stoppgrunn",
        ),
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in kvalitet:
        tid = _sek(r.sekunder) + (f" (over {FRIST} s)" if r.sekunder > FRIST else "")
        linjer.append(
            _rad(
                r.dokument,
                r.nivaa,
                r.resultat,
                r.detalj or "–",
                f"{len(r.utkast.sporsmal)} av {r.antall}"
                if r.ok
                else f"– av {r.antall}",
                _sprak_celle(r),
                r.modell or "–",
                tid,
                r.stoppgrunn or "–",
            )
        )
    ok = sum(r.ok for r in kvalitet)
    avvik = sum(
        r.ok and not _sprak_stemmer(r.sprak_ventet, r.utkast.sprak) for r in kvalitet
    )
    tregeste = max(kvalitet, key=lambda r: r.sekunder)
    linjer += [
        "",
        (
            f"{ok} av {len(kvalitet)} quizer besto formkravene. "
            f"{avvik} hadde et annet språk enn ventet."
        ),
        "",
        (
            f"Lengste kvalitetskall: {tregeste.dokument} / {tregeste.nivaa}, "
            f"{_sek(tregeste.sekunder)} ({tregeste.antall} spørsmål)."
        ),
        "",
        "## Genereringstid",
        "",
        (
            f"`{TIDSDOKUMENT}`, {TIDSNIVAA}, {TIDSANTALL} spørsmål, "
            f"{len(tider)} runder. Kravet er godt under {FRIST} s (FR-15, NFR-7)."
        ),
        "",
        (
            "Tiden er `generer` og `sjekk` for ett kall. Appens frist teller fra "
            "jobben starter og tar også med lesingen av filen og ett nytt forsøk "
            "ved `format`, så den faktiske ventetiden kan bli lengre."
        ),
        "",
        _rad("Runde", "Resultat", "Detalj", "Modell", "Tid", "Stoppgrunn", "Merknad"),
        "|---|---|---|---|---|---|---|",
    ]
    for nr, r in enumerate(tider, start=1):
        merknad = f"over {FRIST} s" if r.sekunder > FRIST else ""
        linjer.append(
            _rad(
                nr,
                r.resultat,
                r.detalj or "–",
                r.modell or "–",
                _sek(r.sekunder),
                r.stoppgrunn or "–",
                merknad,
            )
        )
    ok_tider = [r.sekunder for r in tider if r.ok]
    feilede = len(tider) - len(ok_tider)
    typisk = _sek(statistics.median(ok_tider)) if ok_tider else "–"
    linjer += [
        "",
        f"- Typisk (median): {typisk}",
        f"- Lengste: {_sek(max(r.sekunder for r in tider))}",
        "",
        (
            f"Typisk gjelder de {len(ok_tider)} rundene med OK. "
            "Lengste gjelder alle rundene."
        ),
    ]
    if feilede:
        linjer += ["", f"{feilede} av {len(tider)} runder feilet, se tabellen."]
    linjer += [
        "",
        "## Manuell vurdering (SM-2)",
        "",
        (
            "Skriv «ja» eller «nei» i de tre vurderingskolonnene for hvert spørsmål. "
            "Det riktige alternativet er merket **(riktig)**."
        ),
    ]
    for r in kvalitet:
        linjer += ["", f"### {r.dokument} / {r.nivaa}", ""]
        if not r.ok:
            grunn = f", stoppgrunn {r.stoppgrunn}" if r.stoppgrunn else ""
            linjer.append(f"Ingen spørsmål: {r.resultat}{grunn}.")
            continue
        linjer += [
            _rad(
                "Nr",
                "Spørsmål",
                "Alternativer",
                "Begrunnelse",
                "Relevant",
                "Riktig fasit",
                "Ikke tvetydig",
                "Merknad",
            ),
            "|---|---|---|---|---|---|---|---|",
        ]
        for nr, s in enumerate(r.utkast.sporsmal, start=1):
            alternativer = "\n".join(
                f"{bokstav}) {a.tekst}" + (" **(riktig)**" if a.er_riktig else "")
                for bokstav, a in zip("ABC", s.alternativer, strict=False)
            )
            linjer.append(
                _rad(nr, s.tekst, alternativer, s.begrunnelse, "", "", "", "")
            )
    vurdert = sum(len(r.utkast.sporsmal) for r in kvalitet if r.ok)
    linjer += [
        "",
        "## Slik regner du ut andelen",
        "",
        (
            "Et spørsmål er godt når det er relevant for notatet, har riktig fasit og "
            "ikke er tvetydig, altså «ja» i alle tre kolonnene."
        ),
        "",
        (
            f"Andel gode = antall gode / {vurdert} vurderte spørsmål. "
            "Målet er minst 90 % (SM-2)."
        ),
        "",
        (
            "Før andelen, antall vurderte og eksempler på dårlige spørsmål i "
            "`ki-kvalitet-6-4.md`."
        ),
        "",
    ]
    return "\n".join(linjer)


def _sprak_celle(r):
    if not r.ok:
        return f"{r.sprak_ventet} / –"
    celle = f"{r.sprak_ventet} / {r.utkast.sprak}"
    if not _sprak_stemmer(r.sprak_ventet, r.utkast.sprak):
        celle += " (avvik)"
    return celle
