"""Tester `maal_ki_kvalitet` med falsk `generer`. Ingen nettverkskall."""

import json
import re
import shutil
import tempfile
from collections import Counter
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from django.conf import settings
from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, override_settings

import ki
from ki import KIFeil, RaattSvar, generering
from ki.management.commands import maal_ki_kvalitet
from ki.tests_generering import modellsvar

TESTDOKUMENTER = Path(settings.BASE_DIR) / "testdokumenter"
NOKKEL = "sk-ant-hemmelig-testnokkel"
TIDSDOKUMENT = "html-struktur-og-semantikk"
MODELL = "claude-sonnet-5-5"


def quiz(antall, merke, sprak):
    return {
        "sprak": sprak,
        "modell": settings.KI_MODELL,
        "prompt_versjon": generering.PROMPT_VERSJON,
        "forhandslagret": False,
        "sporsmal": [
            {
                "tekst": f"{merke} spørsmål {nr} med | strek\nog linjeskift?",
                "begrunnelse": f"Fordi {nr}.",
                "alternativer": [
                    {"tekst": f"Feil A {nr}", "er_riktig": False},
                    {"tekst": f"Riktig {nr}", "er_riktig": True},
                    {"tekst": f"Feil B {nr}", "er_riktig": False},
                ],
            }
            for nr in range(1, antall + 1)
        ],
    }


class Klokke:
    """Erstatter `time` i kommandoen. Den falske `generer` flytter tiden."""

    def __init__(self):
        self.naa = 1000.0

    def monotonic(self):
        return self.naa


class MaalKIKvalitetTest(SimpleTestCase):
    def setUp(self):
        self.ut = Path(tempfile.mkdtemp()) / "rapporter"
        self.addCleanup(shutil.rmtree, self.ut.parent, True)
        self.klokke = Klokke()
        self.kall = []

    def falsk_generer(self, svar=None, tider=None):
        """`svar[nr]` er en `KIFeil`, en tekst eller (tekst, stoppgrunn) for kall nr (fra 1).

        `tider[nr]` er sekundene kallet tar (standard 1). Kall 16–18 er tidskallene.
        """
        svar = svar or {}
        tider = tider or {}

        def generer_(innhold_, nivaa, antall, timeout):
            self.kall.append(
                {
                    "type": innhold_.type,
                    "nivaa": nivaa,
                    "antall": antall,
                    "timeout": timeout,
                    "modell": settings.KI_MODELL,
                    "effort": generering.EFFORT,
                }
            )
            nr = len(self.kall)
            self.klokke.naa += tider.get(nr, 1.0)
            dette = svar.get(nr)
            if isinstance(dette, BaseException):
                raise dette
            stoppgrunn = "end_turn"
            if isinstance(dette, tuple):
                dette, stoppgrunn = dette
            if dette is None:
                sprak = "en" if innhold_.type == "txt" else "nb"
                dette = json.dumps(
                    quiz(antall, f"{innhold_.type}-{nivaa}", sprak),
                    ensure_ascii=False,
                )
            return RaattSvar(
                dette,
                False,
                settings.KI_MODELL,
                generering.PROMPT_VERSJON,
                stoppgrunn,
            )

        return generer_

    def kjor(self, generer_=None, **valg):
        ut = StringIO()
        with (
            mock.patch.object(ki, "_tvunget", False),
            override_settings(
                TESTMODUS="0", ANTHROPIC_API_KEY=NOKKEL, KI_MODELL=MODELL
            ),
            mock.patch.object(
                maal_ki_kvalitet,
                "generer",
                side_effect=generer_ or self.falsk_generer(),
            ),
            mock.patch.object(maal_ki_kvalitet, "time", self.klokke),
        ):
            call_command("maal_ki_kvalitet", ut=str(self.ut), stdout=ut, **valg)
        return ut.getvalue()

    def rapport(self):
        filer = list(self.ut.glob("*.md"))
        self.assertEqual(len(filer), 1, filer)
        return filer[0], filer[0].read_text(encoding="utf-8")

    def sm4_rader(self, tekst):
        del_ = tekst.split("## SM-4")[1].split("## Genereringstid")[0]
        return [
            linje
            for linje in del_.splitlines()
            if linje.startswith("| ")
            and not linje.startswith("| Dokument")
            and not linje.startswith("|---")
        ]

    def sm4_rad(self, tekst, dokument, nivaa):
        treff = [
            r
            for r in self.sm4_rader(tekst)
            if r.startswith(f"| {dokument} | {nivaa} |")
        ]
        self.assertEqual(len(treff), 1, treff)
        return treff[0]

    def tidsrader(self, tekst):
        del_ = tekst.split("## Genereringstid")[1].split("## Manuell vurdering")[0]
        return [linje for linje in del_.splitlines() if re.match(r"\| \d+ \|", linje)]

    def vurderingsrader(self, tekst):
        del_ = tekst.split("## Manuell vurdering")[1].split("## Slik regner")[0]
        return [linje for linje in del_.splitlines() if re.match(r"\| \d+ \|", linje)]

    def test_nekter_i_testmodus_uten_kall_og_uten_fil(self):
        with (
            mock.patch.object(ki, "_tvunget", False),
            override_settings(TESTMODUS="", ANTHROPIC_API_KEY=""),
            mock.patch.object(maal_ki_kvalitet, "generer") as falsk,
            self.assertRaises(CommandError) as fanget,
        ):
            call_command("maal_ki_kvalitet", ut=str(self.ut), stdout=StringIO())
        self.assertIn("Testmodus", str(fanget.exception))
        falsk.assert_not_called()
        self.assertFalse(self.ut.exists())

    def test_alt_i_orden(self):
        ut = self.kjor(self.falsk_generer(tider={16: 40.0, 17: 100.0, 18: 50.0}))

        self.assertEqual(len(self.kall), 18)
        kvalitet, tid = self.kall[:15], self.kall[15:]
        self.assertTrue(all(k["antall"] == 10 for k in kvalitet))
        # Tre PDF-er, én DOCX og én TXT, hver på alle tre nivåer.
        self.assertEqual(
            Counter((k["type"], k["nivaa"]) for k in kvalitet),
            Counter(
                (t, n)
                for t in ("pdf", "pdf", "pdf", "docx", "txt")
                for n in generering.VANSKELIGHETSGRADER
            ),
        )
        self.assertEqual(
            [(k["type"], k["nivaa"], k["antall"]) for k in tid],
            [("pdf", "middels", 30)] * 3,
        )
        self.assertTrue(all(k["timeout"] == 300 for k in self.kall))
        self.assertTrue(all(k["effort"] == "medium" for k in self.kall))

        sti, tekst = self.rapport()
        self.assertRegex(
            sti.name,
            r"^ki-kvalitet-\d{4}(-\d\d){5}-claude-sonnet-5-5-"
            + re.escape(generering.EFFORT)
            + r"\.md$",
        )
        for felt in ("Dato", "`PROMPT_VERSJON`", "`effort`", "`MAKS_TOKENS`", "Valg"):
            self.assertIn(f"| {felt} |", tekst)
        self.assertIn("| Modell i svarene | `claude-sonnet-5-5` |", tekst)
        self.assertIn(f"| `PROMPT_VERSJON` | {generering.PROMPT_VERSJON} |", tekst)
        self.assertIn(f"| `MAKS_TOKENS` | {generering.MAKS_TOKENS} |", tekst)
        self.assertIn(f"| `effort` | {generering.EFFORT} |", tekst)
        self.assertIn(f"| Modell valgt (`KI_MODELL`) | `{MODELL}` |", tekst)
        self.assertIn(
            "| Dokument | Nivå | Resultat | Detalj | Antall | Språk ventet / fått "
            "| Modell | Tid | Stoppgrunn |",
            tekst,
        )

        rader = self.sm4_rader(tekst)
        self.assertEqual(len(rader), 15)
        self.assertTrue(all("| OK | – | 10 av 10 |" in r for r in rader), rader)
        self.assertTrue(all(f"| {MODELL} | 1.0 s |" in r for r in rader), rader)
        self.assertIn(
            "Lengste kvalitetskall: css-layout-lysbilder / lett, 1.0 s", tekst
        )
        self.assertNotIn("avvik", "".join(rader))
        self.assertIn("| en / en |", self.sm4_rad(tekst, "javascript-og-dom", "lett"))
        self.assertIn(
            "| nb / nb |", self.sm4_rad(tekst, "universell-utforming", "vanskelig")
        )
        self.assertIn("15 av 15 quizer besto formkravene", tekst)

        tidsrader = self.tidsrader(tekst)
        self.assertEqual(len(tidsrader), 3)
        self.assertIn(f"| 2 | OK | – | {MODELL} | 100.0 s | end_turn |", tidsrader[1])
        self.assertNotIn("over 120 s", tekst)
        self.assertIn("- Typisk (median): 50.0 s", tekst)
        self.assertIn("- Lengste: 100.0 s", tekst)
        self.assertNotIn("runder feilet", tekst)
        self.assertIn("ett nytt forsøk", tekst)

        vurdering = self.vurderingsrader(tekst)
        self.assertEqual(len(vurdering), 150)
        self.assertIn(
            "| Nr | Spørsmål | Alternativer | Begrunnelse | Relevant | Riktig fasit "
            "| Ikke tvetydig | Merknad |",
            tekst,
        )
        # `|` og linjeskift i teksten ødelegger ikke tabellen, og vurderingen er tom.
        rad = vurdering[0]
        self.assertIn(r"spørsmål 1 med \| strek<br>og linjeskift?", rad)
        self.assertIn("A) Feil A 1<br>B) Riktig 1 **(riktig)**<br>C) Feil B 1", rad)
        self.assertTrue(rad.endswith("| Fordi 1. |  |  |  |  |"), rad)
        self.assertIn("150 vurderte spørsmål", tekst)
        self.assertIn("90 %", tekst)

        # Rapporten er LF og UTF-8, og har aldri nøkkelen eller filinnholdet.
        self.assertNotIn(b"\r\n", sti.read_bytes())
        self.assertNotIn(NOKKEL, tekst)
        notat = (TESTDOKUMENTER / "javascript-og-dom.txt").read_text(encoding="utf-8")
        forste_linje = next(linje for linje in notat.splitlines() if linje.strip())
        self.assertNotIn(forste_linje.strip(), tekst)

        # Utskriften har én linje per kall og stien, aldri innhold.
        linjer = ut.strip().splitlines()
        self.assertEqual(len(linjer), 19)
        self.assertNotIn("spørsmål", ut)
        self.assertNotIn(NOKKEL, ut)
        self.assertIn("javascript-og-dom / lett / 10: OK, 1.0 s", ut)
        self.assertIn(f"tid, runde 2: {TIDSDOKUMENT} / middels / 30: OK, 100.0 s", ut)
        self.assertIn(str(sti), linjer[-1])

    def test_formatfeil_fores_med_stoppgrunn_og_kjoringen_gar_videre(self):
        self.kjor(self.falsk_generer(svar={1: ("ikke json", "end_turn")}))
        self.assertEqual(len(self.kall), 18)
        _, tekst = self.rapport()
        rad = self.sm4_rader(tekst)[0]
        self.assertIn("| feil: format | svaret er ikke gyldig JSON | – av 10 |", rad)
        self.assertIn("| end_turn |", rad)
        self.assertIn("14 av 15 quizer besto formkravene", tekst)
        self.assertIn("Ingen spørsmål: feil: format, stoppgrunn end_turn.", tekst)
        self.assertEqual(len(self.vurderingsrader(tekst)), 140)

    def test_avkuttet_svar_viser_max_tokens(self):
        avkuttet = '{"sprak": "nb", "sporsmal": [{"tekst": "Halv'
        self.kjor(self.falsk_generer(svar={2: (avkuttet, "max_tokens")}))
        _, tekst = self.rapport()
        rad = self.sm4_rader(tekst)[1]
        self.assertIn("| feil: format |", rad)
        self.assertTrue(rad.endswith("| max_tokens |"), rad)
        self.assertNotIn("Halv", tekst)

    def test_kifeil_fra_kallet_fores_med_feilkode_detalj_og_tid(self):
        self.kjor(
            self.falsk_generer(
                svar={3: KIFeil("api_feil", "modellen avslo forespørselen")},
                tider={3: 300.0},
            )
        )
        self.assertEqual(len(self.kall), 18)
        _, tekst = self.rapport()
        rad = self.sm4_rader(tekst)[2]
        self.assertIn("| feil: api_feil | modellen avslo forespørselen |", rad)
        self.assertIn("| – | 300.0 s (over 120 s) | – |", rad)
        self.assertIn(
            "Lengste kvalitetskall: css-layout-lysbilder / vanskelig, 300.0 s", tekst
        )

    def test_feil_sprak_er_ok_men_vises_som_avvik(self):
        def svar_med_feil_sprak(innhold_, nivaa, antall, timeout):
            raatt = vanlig(innhold_, nivaa, antall, timeout)
            if innhold_.type != "txt":
                return raatt
            data = json.loads(raatt.tekst)
            data["sprak"] = "nb"
            return RaattSvar(json.dumps(data), False, raatt.modell, "1", "end_turn")

        vanlig = self.falsk_generer()
        self.kjor(svar_med_feil_sprak)
        _, tekst = self.rapport()
        rad = self.sm4_rad(tekst, "javascript-og-dom", "middels")
        self.assertIn("| OK |", rad)
        self.assertIn("| en / nb (avvik) |", rad)
        self.assertIn("3 hadde et annet språk enn ventet", tekst)

    def test_region_og_store_bokstaver_i_sprak_er_ikke_avvik(self):
        def svar_med_region(innhold_, nivaa, antall, timeout):
            raatt = vanlig(innhold_, nivaa, antall, timeout)
            data = json.loads(raatt.tekst)
            data["sprak"] = "EN-us" if innhold_.type == "txt" else "nb-NO"
            return RaattSvar(json.dumps(data), False, raatt.modell, "1", "end_turn")

        vanlig = self.falsk_generer()
        self.kjor(svar_med_region)
        _, tekst = self.rapport()
        self.assertIn(
            "| nb / nb-NO |", self.sm4_rad(tekst, "universell-utforming", "lett")
        )
        self.assertNotIn("(avvik)", tekst)
        self.assertIn("0 hadde et annet språk enn ventet", tekst)

    def test_html_i_sporsmal_escapes_utenfor_kode(self):
        def svar_med_html(innhold_, nivaa, antall, timeout):
            raatt = vanlig(innhold_, nivaa, antall, timeout)
            data = json.loads(raatt.tekst)
            data["sporsmal"][0]["tekst"] = "Hva gjør <nav> & `<main>`?"
            return RaattSvar(json.dumps(data), False, raatt.modell, "1", "end_turn")

        vanlig = self.falsk_generer()
        self.kjor(svar_med_html)
        _, tekst = self.rapport()
        self.assertIn("| 1 | Hva gjør &lt;nav&gt; &amp; `<main>`? |", tekst)

    def test_tidskall_over_120_s_merkes(self):
        self.kjor(self.falsk_generer(tider={16: 60.0, 17: 130.0, 18: 70.0}))
        _, tekst = self.rapport()
        rader = self.tidsrader(tekst)
        self.assertIn("| 130.0 s |", rader[1])
        self.assertTrue(rader[1].endswith("| over 120 s |"), rader[1])
        self.assertNotIn("over 120 s", rader[0] + rader[2])
        self.assertIn("- Typisk (median): 70.0 s", tekst)
        self.assertIn("- Lengste: 130.0 s", tekst)

    def test_feilet_tidskall_teller_i_lengste_men_ikke_i_median(self):
        self.kjor(
            self.falsk_generer(
                svar={17: KIFeil("timeout", "APITimeoutError")},
                tider={16: 40.0, 17: 300.0, 18: 60.0},
            )
        )
        _, tekst = self.rapport()
        self.assertIn(
            "| 2 | feil: timeout | APITimeoutError | – | 300.0 s |",
            self.tidsrader(tekst)[1],
        )
        self.assertIn("- Typisk (median): 50.0 s", tekst)
        self.assertIn("- Lengste: 300.0 s", tekst)
        self.assertIn("1 av 3 runder feilet", tekst)

    def test_valgene_brukes_og_star_i_toppen(self):
        effort_for, modell_for = generering.EFFORT, settings.KI_MODELL
        self.kjor(modell="claude-haiku-5-5", effort="low", antall=5, runder=2)

        self.assertEqual(len(self.kall), 17)
        self.assertTrue(all(k["antall"] == 5 for k in self.kall[:15]))
        self.assertTrue(all(k["antall"] == 30 for k in self.kall[15:]))
        self.assertTrue(all(k["modell"] == "claude-haiku-5-5" for k in self.kall))
        self.assertTrue(all(k["effort"] == "low" for k in self.kall))
        # Verdiene settes tilbake etter kjøringen.
        self.assertEqual(generering.EFFORT, effort_for)
        self.assertEqual(settings.KI_MODELL, modell_for)

        sti, tekst = self.rapport()
        self.assertTrue(sti.name.endswith("-claude-haiku-5-5-low.md"), sti.name)
        self.assertIn("| Modell valgt (`KI_MODELL`) | `claude-haiku-5-5` |", tekst)
        self.assertIn("| Modell i svarene | `claude-haiku-5-5` |", tekst)
        self.assertIn("| `effort` | low |", tekst)
        self.assertIn(
            "--antall 5, --runder 2, --modell claude-haiku-5-5, --effort low", tekst
        )
        self.assertEqual(len(self.tidsrader(tekst)), 2)
        self.assertEqual(len(self.vurderingsrader(tekst)), 75)

    def test_ugyldige_valg_gir_commanderror_for_kall(self):
        for valg in (
            {"effort": "max"},
            {"effort": ""},
            {"antall": 0},
            {"antall": 31},
            {"antall": "10"},
            {"antall": True},
            {"runder": 0},
            {"modell": " "},
        ):
            with self.subTest(valg=valg):
                with self.assertRaises(CommandError) as fanget:
                    self.kjor(**valg)
                self.assertIn(f"--{next(iter(valg))}", str(fanget.exception))
                self.assertEqual(self.kall, [])
                self.assertFalse(self.ut.exists())

    def test_ugyldige_valg_fra_kommandolinjen(self):
        for argv in (["--effort", "max"], ["--antall", "ti"]):
            with (
                self.subTest(argv=argv),
                mock.patch.object(ki, "_tvunget", False),
                override_settings(TESTMODUS="0", ANTHROPIC_API_KEY=NOKKEL),
                mock.patch.object(maal_ki_kvalitet, "generer") as falsk,
                self.assertRaises(CommandError) as fanget,
            ):
                call_command(
                    "maal_ki_kvalitet", *argv, "--ut", str(self.ut), stdout=StringIO()
                )
            self.assertIn(argv[0], str(fanget.exception))
            falsk.assert_not_called()

    def test_ugyldig_ut_gir_commanderror_for_kall(self):
        self.ut.parent.mkdir(parents=True, exist_ok=True)
        self.ut.write_text("en fil, ikke en mappe", encoding="utf-8")
        with self.assertRaises(CommandError) as fanget:
            self.kjor()
        self.assertIn("--ut", str(fanget.exception))
        self.assertEqual(self.kall, [])

    def test_uventet_feil_gir_ingen_rapport_og_effort_settes_tilbake(self):
        effort_for = generering.EFFORT
        generer_ = self.falsk_generer(svar={5: RuntimeError("uventet")})
        with self.assertRaises(RuntimeError):
            self.kjor(generer_, effort="high")
        self.assertEqual(len(self.kall), 5)
        self.assertEqual(self.kall[-1]["effort"], "high")
        self.assertEqual(generering.EFFORT, effort_for)
        self.assertEqual(list(self.ut.glob("*")), [])


class MaalKIKvalitetMotKlientTest(SimpleTestCase):
    """Kjører kommandoen med den ekte `generer` og en falsk klient, uten nettverk."""

    def test_effort_og_modell_kommer_fram_til_foresporselen(self):
        ut = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, ut, True)
        foresporsler = []

        def create(**kwargs):
            foresporsler.append(kwargs)
            data = quiz(30, f"k{len(foresporsler)}", "nb")
            data["modell"] = kwargs["model"]
            return modellsvar(json.dumps(data), model=kwargs["model"])

        klient = SimpleNamespace(
            beta=SimpleNamespace(messages=SimpleNamespace(create=create))
        )
        effort_for = generering.EFFORT
        with (
            mock.patch.object(ki, "_tvunget", False),
            override_settings(
                TESTMODUS="0", ANTHROPIC_API_KEY=NOKKEL, KI_MODELL=MODELL
            ),
            mock.patch.object(generering, "_klient", return_value=klient),
        ):
            call_command(
                "maal_ki_kvalitet",
                "--effort",
                "low",
                "--modell",
                "claude-haiku-5-5",
                "--antall",
                "30",
                "--runder",
                "1",
                "--ut",
                str(ut),
                stdout=StringIO(),
            )
        self.assertEqual(len(foresporsler), 16)
        for kall in foresporsler:
            self.assertEqual(kall["model"], "claude-haiku-5-5")
            self.assertEqual(kall["output_config"]["effort"], "low")
        self.assertEqual(generering.EFFORT, effort_for)
        tekst = next(ut.glob("*.md")).read_text(encoding="utf-8")
        self.assertIn("| Modell i svarene | `claude-haiku-5-5` |", tekst)
