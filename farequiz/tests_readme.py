"""README-en er oppskriften sensor følger (FR-29, FR-30, AD-22, SM-1).

Testene leser navnene fra koden der de finnes, så README-en ikke kan gli fra koden.
"""

import re
import tomllib
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from kontoer import testbruker

ROT = Path(settings.BASE_DIR)

OPPSTART = (
    "manage.py migrate",
    "manage.py seed_testdata",
    "manage.py runserver",
)

# Variablene sensor trenger for ekte modell og mobil på samme nett.
ENV_VARIABLER = ("ANTHROPIC_API_KEY", "TESTMODUS", "KI_MODELL", "ALLOWED_HOSTS")

SEKSJONER = (
    "Hva appen gjør",
    "Hva som trengs",
    "Kom i gang",
    "Testbruker",
    "Testmodus",
    "Ekte modell",
    "Mobil på samme nett",
    "For gruppa",
    "Medlemmer",
)


def les(navn):
    return (ROT / navn).read_text(encoding="utf-8")


def pakkenavn(navn):
    """Normalisert pakkenavn etter PEP 503, uten `[extras]`."""
    navn = re.sub(r"\[.*?\]", "", navn).strip()
    return re.sub(r"[-_.]+", "-", navn).lower()


def banneret():
    """Bannerteksten slik den står i `base.html`, med mellomrom slått sammen."""
    mal = les("templates/base.html")
    treff = re.search(r"\{% if testmodus %\}.*?<div[^>]*>(.*?)</div>", mal, re.DOTALL)
    assert treff, "fant ikke testmodus-banneret i base.html"
    return " ".join(treff.group(1).split())


class ReadmeTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.readme = les("README.md")

    def assert_med(self, tekster):
        mangler = [tekst for tekst in tekster if tekst not in self.readme]
        self.assertEqual(mangler, [], "mangler i README.md")

    def seksjon(self, overskrift):
        """Teksten under `## overskrift`, fram til neste `## `."""
        treff = re.search(
            rf"^## {re.escape(overskrift)}\n(.*?)(?=^## |\Z)",
            self.readme,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(treff, f"mangler seksjonen «{overskrift}»")
        return treff.group(1)

    def assert_rekkefolge(self, tekst, steg):
        plasser = []
        for del_ in steg:
            self.assertIn(del_, tekst)
            plasser.append(tekst.index(del_, plasser[-1] if plasser else 0))
        self.assertEqual(plasser, sorted(plasser), steg)

    def test_seksjonene_i_riktig_rekkefolge(self):
        overskrifter = re.findall(r"^## (.+)$", self.readme, re.MULTILINE)
        self.assertEqual(overskrifter, list(SEKSJONER))

    def test_hva_som_trengs(self):
        krav = tomllib.loads(les("pyproject.toml"))["project"]["requires-python"]
        versjon = re.search(r">=\s*([\d.]+)", krav).group(1)
        trengs = self.seksjon("Hva som trengs")
        for tekst in (f"Python {versjon}", "uv", "pip", "git"):
            self.assertIn(tekst, trengs)

    def test_de_fire_stegene_med_uv_og_pip(self):
        self.assert_med(["uv sync", "pip install -r requirements.txt"])
        self.assert_med([f"uv run python {steg}" for steg in OPPSTART])
        for steg in OPPSTART:
            self.assertRegex(
                self.readme, rf"(?m)^\s+python {re.escape(steg)}$", f"pip: {steg}"
            )
        self.assert_med(["http://127.0.0.1:8000/"])

    def test_stegene_kommer_i_rekkefolge(self):
        kom_i_gang = self.seksjon("Kom i gang")
        self.assert_rekkefolge(
            kom_i_gang, ["uv sync", *(f"uv run python {steg}" for steg in OPPSTART)]
        )
        self.assert_rekkefolge(
            kom_i_gang,
            [
                "pip install -r requirements.txt",
                *(f"\n    python {steg}\n" for steg in OPPSTART),
            ],
        )

    def test_testbrukeren(self):
        self.assert_med([testbruker.EPOST, testbruker.PASSORD, "Webutvikling"])

    def test_banneret_er_det_samme_som_i_base_html(self):
        self.assertIn("Testmodus:", banneret())
        self.assert_med([banneret()])

    def test_env_variablene(self):
        self.assert_med([".env.example", "TESTMODUS=0", *ENV_VARIABLER])
        self.assert_med(["cp .env.example .env", "copy .env.example .env"])

    def test_env_variablene_finnes_i_env_example(self):
        eksempel = les(".env.example")
        for navn in ENV_VARIABLER:
            self.assertRegex(eksempel, rf"(?m)^{navn}=", navn)

    def test_mobil_pa_samme_nett(self):
        self.assert_med(["runserver 0.0.0.0:8000", "ALLOWED_HOSTS=", "ikke hosting"])

    def test_for_gruppa(self):
        self.assert_med(["lag_mocksvar", "ki/mock/"])

    def test_kommandoene_finnes(self):
        for kommando in ("seed_testdata", "lag_mocksvar"):
            self.assertIn(kommando, self.readme)
        self.assertTrue(
            (ROT / "studier/management/commands/seed_testdata.py").is_file()
        )
        self.assertTrue((ROT / "ki/management/commands/lag_mocksvar.py").is_file())

    def test_ingen_utropstegn_utenfor_kode(self):
        uten_kode = re.sub(r"`[^`]*`|^ {4}.*$", "", self.readme, flags=re.MULTILINE)
        self.assertNotIn("!", uten_kode)


class RequirementsTest(SimpleTestCase):
    def test_alle_avhengighetene_fra_pyproject_er_med(self):
        """pip-veien i README-en: requirements.txt har alle avhengighetene i pyproject.toml, inkludert whitenoise."""
        prosjekt = tomllib.loads(les("pyproject.toml"))["project"]["dependencies"]
        navn = {
            pakkenavn(re.split(r"[<>=!~; ]", krav, maxsplit=1)[0]) for krav in prosjekt
        }
        pinnet = {
            pakkenavn(linje.split("==", 1)[0])
            for linje in les("requirements.txt").splitlines()
            if "==" in linje and not linje.lstrip().startswith("#")
        }
        self.assertIn("whitenoise", navn)
        self.assertIn("whitenoise", pinnet)
        self.assertEqual(sorted(navn - pinnet), [])
        # Utviklingsverktøy hører ikke med i det sensor installerer med pip.
        self.assertNotIn("ruff", pinnet)
