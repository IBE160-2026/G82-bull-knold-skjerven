"""axe-core mot skjermbildene i tilstandene fra EXPERIENCE.md (SM-7, NFR-1, NFR-2).

Kjøres bare med `uv run python manage.py test --tag nettleser`, og krever
Chromium fra `uv run playwright install chromium`. axe-core kommer fra
`axe-playwright-python` (dev-avhengighet), så testen gjør ingen nettverkskall
utenom den lokale testserveren. Resultatet står i
`_bmad-output/implementation-artifacts/sluttkontroll-6-3.md`.
"""

import importlib.util
import os
import shutil
import sys
import tempfile
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from django.test import override_settings, tag
from django.utils import timezone

from kontoer import testbruker
from studier.models import (
    Alternativ,
    Emne,
    Feilkode,
    Genereringsjobb,
    Jobbstatus,
    Notat,
    Okt,
    Oktstatus,
    Okttype,
    Svar,
)
from studier.services.emner import opprett_emne
from studier.services.generering import generer_synkront
from studier.services.okter import start_eller_fortsett_okt

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # Uten dev-avhengighetene, for eksempel med requirements.txt.
    sync_playwright = None

AXE_TAGGER = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]
PASSORD = "hemmelig-passord"

HTML = "html-struktur-og-semantikk.pdf"
DOCX = "universell-utforming.docx"
TXT = "javascript-og-dom.txt"


def _axe_skript():
    """axe.min.js fra `axe-playwright-python`. Bare filen leses, pakken importeres ikke."""
    pakke = importlib.util.find_spec("axe_playwright_python")
    if pakke is None:
        raise RuntimeError("axe-playwright-python er ikke installert. Kjør `uv sync`.")
    return (Path(pakke.origin).parent / "axe.min.js").read_text(encoding="utf-8")


@tag("nettleser")
class AxeTest(StaticLiveServerTestCase):
    """Én test per skjermbilde og tilstand. Feiler med regel, selector og URL."""

    versjoner = {}

    @classmethod
    def setUpClass(cls):
        if sync_playwright is None:
            raise RuntimeError("Playwright er ikke installert. Kjør `uv sync`.")
        cls.axe = _axe_skript()
        cls._media = tempfile.mkdtemp()
        cls._innstillinger = override_settings(MEDIA_ROOT=cls._media)
        cls._innstillinger.enable()
        # Playwrights synkrone API har en hendelsesløkke i testtråden, og da nekter
        # Django ORM-kall der. Testene kaller ORM-en mellom nettleserkallene.
        cls._async_unsafe = os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE")
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        cls._playwright = sync_playwright().start()
        try:
            cls.nettleser = cls._playwright.chromium.launch()
        except Exception:
            # Typisk mangler Chromium: `uv run playwright install chromium`.
            cls._playwright.stop()
            cls._rydd()
            raise
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.nettleser.close()
        cls._playwright.stop()
        super().tearDownClass()
        cls._rydd()
        if cls.versjoner:
            versjoner = ", ".join(f"{k} {v}" for k, v in cls.versjoner.items())
            sys.stderr.write(f"\naxe-testen kjørte med {versjoner}.\n")

    @classmethod
    def _rydd(cls):
        if cls._async_unsafe is None:
            os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE", None)
        else:
            os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = cls._async_unsafe
        cls._innstillinger.disable()
        shutil.rmtree(cls._media, ignore_errors=True)

    def setUp(self):
        super().setUp()
        self.kontekst = self.nettleser.new_context(locale="nb-NO")
        self.side = self.kontekst.new_page()

    def tearDown(self):
        self.kontekst.close()
        super().tearDown()

    # Hjelpere

    def gaa_til(self, sti):
        self.side.goto(self.live_server_url + sti)

    def sjekk(self, tilstand):
        """Kjører axe på siden slik den er nå, og feiler med hvert brudd.

        Kartet bak siden er et bakgrunnsbilde, og over et bilde kan ikke axe
        regne ut kontrasten (resultatet blir «incomplete»). Kartet er dekorativt
        og tas bort før axe kjører, så kontrasten måles mot sidefargen. Linjene
        i kartet er sjekket for seg (se sluttkontroll-6-3.md).
        """
        self.side.add_style_tag(
            content=".kart-bakgrunn { background-image: none !important; }"
        )
        self.side.add_script_tag(content=self.axe)
        resultat = self.side.evaluate(
            """tagger => axe.run(document, {
                runOnly: {type: "tag", values: tagger},
                resultTypes: ["violations"],
            })""",
            AXE_TAGGER,
        )
        type(self).versjoner = {
            "axe-core": resultat["testEngine"]["version"],
            "Chromium": self.nettleser.version,
        }
        brudd = resultat["violations"]
        if not brudd:
            return
        antall = sum(len(regel["nodes"]) for regel in brudd)
        linjer = [f"{tilstand}: {antall} axe-brudd på {self.side.url}"]
        for regel in brudd:
            for node in regel["nodes"]:
                selector = " ".join(str(del_) for del_ in node["target"])
                sammendrag = (node.get("failureSummary") or "").replace("\n", " ")
                linjer.append(
                    f"- {regel['id']} ({regel['impact']}) {selector}: {sammendrag}"
                )
        self.fail("\n".join(linjer))

    def bruker(self, epost="ny@eks.no", godtatt=True):
        bruker = get_user_model().objects.create_user(epost, PASSORD)
        if godtatt:
            bruker.vilkar_godtatt = timezone.now()
            bruker.save(update_fields=["vilkar_godtatt"])
        return bruker

    def logg_inn(self, bruker):
        """Sesjonen fra testklienten legges i nettleseren, så innloggingen ikke tar tid."""
        self.client.force_login(bruker)
        informasjonskapsel = self.client.cookies[settings.SESSION_COOKIE_NAME]
        self.kontekst.add_cookies(
            [
                {
                    "name": settings.SESSION_COOKIE_NAME,
                    "value": informasjonskapsel.value,
                    "url": self.live_server_url,
                }
            ]
        )

    def seed(self, logg_inn=True):
        """Testbrukerens data fra `seed_testdata`, med mock-svarene i ki/mock/."""
        call_command("seed_testdata", stdout=StringIO())
        bruker = get_user_model().objects.get(email=testbruker.EPOST)
        if logg_inn:
            self.logg_inn(bruker)
        return bruker

    def notat(self, navn):
        return Notat.objects.get(emne__navn="Webutvikling", originalnavn=navn)

    def emne_uten_notater(self):
        bruker = self.bruker()
        self.logg_inn(bruker)
        return opprett_emne(bruker, "Databaser")

    def pabegynt_forsok(self):
        return Okt.objects.get(
            notat=self.notat(HTML), type=Okttype.FORSOK, status=Oktstatus.PABEGYNT
        )

    # S1, S1b og S2

    def test_s1_tom(self):
        self.gaa_til("/logg-inn/")
        self.sjekk("S1 tom")

    def test_s1_feil_innlogging(self):
        self.bruker("ola@eks.no")
        self.gaa_til("/logg-inn/")
        self.side.fill("#epost", "ola@eks.no")
        self.side.fill("#passord", "feil-passord")
        self.side.locator("main form button[type=submit]").click()
        self.side.wait_for_selector("#feil-innlogging")
        self.sjekk("S1 feil innlogging")

    def test_s1_okt_utlopt(self):
        self.gaa_til("/logg-inn/?next=/emner/1/")
        self.side.wait_for_selector("main [role=status]")
        self.sjekk("S1 økt utløpt")

    def test_s1b_vilkar(self):
        self.logg_inn(self.bruker(godtatt=False))
        self.gaa_til("/")
        self.assertIn("/vilkar/", self.side.url)
        self.sjekk("S1b")

    def test_s2_tom(self):
        self.gaa_til("/registrer/")
        self.sjekk("S2 tom")

    def test_s2_feil(self):
        self.gaa_til("/registrer/")
        self.side.fill("#epost", "ny@eks.no")
        self.side.fill("#passord", "kort")
        self.side.locator("main form button[type=submit]").click()
        self.side.wait_for_selector("[aria-invalid=true]")
        self.sjekk("S2 feil")

    # S3 og S4

    def test_s3_ny_bruker(self):
        self.logg_inn(self.bruker())
        self.gaa_til("/")
        self.sjekk("S3 ny bruker")

    def test_s3_testbrukeren(self):
        self.seed()
        self.gaa_til("/")
        self.sjekk("S3 testbrukeren")

    def test_s4_uten_notater(self):
        emne = self.emne_uten_notater()
        self.gaa_til(f"/emner/{emne.pk}/")
        self.sjekk("S4 uten notater")

    def test_s4_med_notater(self):
        self.seed()
        emne = Emne.objects.get(navn="Webutvikling")
        self.gaa_til(f"/emner/{emne.pk}/")
        self.sjekk("S4 med notater")

    def test_s4_feil_navn(self):
        emne = self.emne_uten_notater()
        self.gaa_til(f"/emner/{emne.pk}/")
        self.side.locator("details summary").filter(has_text="Gi nytt navn").click()
        self.side.fill("#id_navn", "")
        self.side.get_by_role("button", name="Lagre navn").click()
        self.side.wait_for_selector("#feil-endre-navn")
        self.sjekk("S4 tomt navn")

    # S5, S6, S6b og S6c

    def test_s5_forste_opplasting(self):
        emne = self.emne_uten_notater()
        self.gaa_til(f"/emner/{emne.pk}/last-opp/")
        self.sjekk("S5")

    def test_s6_tom(self):
        emne = self.emne_uten_notater()
        self.gaa_til(f"/emner/{emne.pk}/last-opp/?videre=1")
        self.sjekk("S6 tom")

    def _last_opp(self, navn, innhold):
        self.side.set_input_files(
            "#id_fil",
            files=[
                {
                    "name": navn,
                    "mimeType": "application/octet-stream",
                    "buffer": innhold,
                }
            ],
        )
        self.side.locator("#opplasting-knapp").click()

    def test_s6_avvist_fil_i_nettleseren(self):
        emne = self.emne_uten_notater()
        self.gaa_til(f"/emner/{emne.pk}/last-opp/?videre=1")
        self._last_opp("program.exe", b"MZ")
        self.side.wait_for_selector("#feil-fil")
        self.sjekk("S6 avvist fil (nettleseren)")

    def test_s6_avvist_fil_paa_serveren(self):
        emne = self.emne_uten_notater()
        self.gaa_til(f"/emner/{emne.pk}/last-opp/?videre=1")
        self._last_opp("notat.pdf", b"ikke en pdf")
        self.side.wait_for_selector("#feil-fil")
        self.assertFalse(Notat.objects.exists())
        self.sjekk("S6 avvist fil (serveren)")

    def test_s6b_opplasting_pagar(self):
        emne = self.emne_uten_notater()
        self.gaa_til(f"/emner/{emne.pk}/last-opp/?videre=1")
        # Svaret holdes tilbake, så siden blir stående i S6b.
        self.side.route("**/last-opp/", lambda route: None)
        self._last_opp("notat.txt", b"Et notat om HTML. " * 20)
        self.side.wait_for_selector("#opplasting-fremdrift", state="visible")
        self.sjekk("S6b")

    def test_s6c_opplasting_avbrutt(self):
        emne = self.emne_uten_notater()
        self.gaa_til(f"/emner/{emne.pk}/last-opp/?videre=1")
        self.side.route("**/last-opp/", lambda route: route.abort())
        self._last_opp("notat.txt", b"Et notat om HTML. " * 20)
        self.side.wait_for_selector("#opplasting-avbrutt", state="visible")
        self.sjekk("S6c")

    # S7 og S8

    def test_s7_uten_quiz(self):
        self.seed()
        self.gaa_til(f"/notater/{self.notat(TXT).pk}/")
        self.sjekk("S7 uten quiz")

    def test_s7_med_quizer_og_pabegynt(self):
        self.seed()
        self.gaa_til(f"/notater/{self.notat(HTML).pk}/")
        self.side.wait_for_selector("text=Påbegynt")
        self.sjekk("S7 med quizer og påbegynt forsøk")

    def _jobb(self, **felt):
        self.seed()
        return Genereringsjobb.objects.create(
            notat=self.notat(TXT), vanskelighetsgrad="lett", antall=5, **felt
        )

    def test_s8_pagar(self):
        jobb = self._jobb()
        # Steget holdes tilbake, så stegene blir stående som de er.
        self.side.route("**/steg/", lambda route: None)
        self.gaa_til(f"/jobber/{jobb.pk}/")
        self.side.wait_for_selector("#fremdrift li")
        self.sjekk("S8 pågår")

    def test_s8_timeout(self):
        jobb = self._jobb(status=Jobbstatus.FEILET, feilkode=Feilkode.TIMEOUT)
        self.gaa_til(f"/jobber/{jobb.pk}/")
        self.side.wait_for_selector("#fremdrift [role=alert]")
        self.sjekk("S8 timeout")

    def test_s8_feil_format(self):
        jobb = self._jobb(status=Jobbstatus.FEILET, feilkode=Feilkode.FORMAT)
        self.gaa_til(f"/jobber/{jobb.pk}/")
        self.side.wait_for_selector("#fremdrift [role=alert]")
        self.sjekk("S8 feil format")

    def test_s8_ingen_serverkontakt(self):
        jobb = self._jobb()
        self.side.route("**/steg/", lambda route: route.fulfill(status=500))
        self.gaa_til(f"/jobber/{jobb.pk}/")
        self.side.wait_for_selector("#fremdrift [role=alert]")
        self.sjekk("S8 ingen serverkontakt")

    # S9, S10 og S11

    def test_s9_sporsmal(self):
        self.seed()
        okt = self.pabegynt_forsok()
        self.gaa_til(f"/okter/{okt.pk}/sporsmal/5/")
        self.sjekk("S9 spørsmål")

    def test_s9_sporsmal_pa_engelsk(self):
        """Quiz fra javascript-og-dom.txt, som er på engelsk, så `lang="en"` er med."""
        self.seed()
        quiz = generer_synkront(self.notat(TXT), "lett", 5)
        okt = start_eller_fortsett_okt(quiz)
        self.gaa_til(f"/okter/{okt.pk}/sporsmal/1/")
        self.assertEqual(self.side.locator("legend").get_attribute("lang"), "en")
        self.sjekk("S9 spørsmål på engelsk")

    def test_s9_svar_ikke_lagret(self):
        self.seed()
        okt = self.pabegynt_forsok()
        rad = okt.innhold[4]
        fremmed = (
            Alternativ.objects.filter(sporsmal__quiz=okt.quiz)
            .exclude(pk__in=rad["alternativer"])
            .first()
        )
        self.gaa_til(f"/okter/{okt.pk}/sporsmal/5/")
        # Et alternativ som ikke hører til spørsmålet, gir «Svaret ble ikke lagret».
        radio = self.side.locator("input[name=alternativ]").first
        radio.evaluate("(el, verdi) => { el.value = verdi; }", str(fremmed.pk))
        radio.check()
        self.side.get_by_role("button", name="Neste").click()
        self.side.wait_for_selector("#feil-svar")
        self.sjekk("S9 svaret ble ikke lagret")

    def test_s10_ikke_alle_besvart(self):
        self.seed()
        okt = self.pabegynt_forsok()
        self.gaa_til(f"/okter/{okt.pk}/lever/")
        self.sjekk("S10 ikke alle besvart")

    def test_s10_lever_med_manglende_svar(self):
        self.seed()
        okt = self.pabegynt_forsok()
        self.gaa_til(f"/okter/{okt.pk}/lever/")
        self.side.get_by_role("button", name="Lever").click(force=True)
        self.side.wait_for_selector("[role=alert]")
        self.sjekk("S10 lever med manglende svar")

    def _levert_med_feil(self):
        svar = (
            Svar.objects.filter(
                okt__type=Okttype.FORSOK,
                okt__status=Oktstatus.LEVERT,
                alternativ__er_riktig=False,
            )
            .select_related("okt")
            .first()
        )
        okt = svar.okt
        nr = next(
            nr
            for nr, rad in enumerate(okt.innhold, start=1)
            if rad["sporsmal"] == svar.sporsmal_id
        )
        return okt, nr

    def test_s11_resultat(self):
        self.seed()
        okt, _ = self._levert_med_feil()
        self.gaa_til(f"/okter/{okt.pk}/resultat/")
        self.sjekk("S11 resultat")

    def test_meld_som_feil(self):
        self.seed()
        okt, nr = self._levert_med_feil()
        self.gaa_til(f"/okter/{okt.pk}/meld/{nr}/")
        self.sjekk("Meld som feil")

    # S12

    def test_s12_sporsmal(self):
        self.seed()
        okt = start_eller_fortsett_okt(notat=self.notat(DOCX))
        self.gaa_til(f"/okter/{okt.pk}/sporsmal/1/")
        self.sjekk("S12 spørsmål")

    def test_s12_resultat(self):
        self.seed()
        okt = Okt.objects.get(type=Okttype.OVING, status=Oktstatus.LEVERT)
        self.gaa_til(f"/okter/{okt.pk}/resultat/")
        self.sjekk("S12 resultat")

    # S13–S16

    def test_s13_slett_emne(self):
        self.seed()
        emne = Emne.objects.get(navn="Webutvikling")
        self.gaa_til(f"/emner/{emne.pk}/slett/")
        self.sjekk("S13")

    def test_s14_fant_ikke_siden(self):
        self.logg_inn(self.bruker())
        self.gaa_til("/emner/999999/")
        self.sjekk("S14")

    def test_s15_personvern_utlogget(self):
        self.gaa_til("/personvern/")
        self.sjekk("S15 utlogget")

    def test_s15_personvern_innlogget(self):
        self.logg_inn(self.bruker())
        self.gaa_til("/personvern/")
        self.sjekk("S15 innlogget")

    def test_s16_tom(self):
        self.logg_inn(self.bruker())
        self.gaa_til("/emner/ny/")
        self.sjekk("S16 tom")

    def test_s16_feil(self):
        self.logg_inn(self.bruker())
        self.gaa_til("/emner/ny/")
        self.side.get_by_role("button", name="Opprett emne").click()
        self.side.wait_for_selector("[aria-invalid=true]")
        self.sjekk("S16 tomt navn")

    # Menyen åpen, så lenkene i den også sjekkes.

    def test_meny_apen(self):
        self.logg_inn(self.bruker())
        self.gaa_til("/")
        self.side.locator("details.meny summary").click()
        self.side.wait_for_selector("nav[aria-label=Hovedmeny]", state="visible")
        self.sjekk("Menyen åpen")

    # Mobil: 320 px bredde, så target-size og mobiloppsettet også sjekkes.

    def mobil(self):
        self.side.set_viewport_size({"width": 320, "height": 640})

    def test_mobil_s1(self):
        self.mobil()
        self.gaa_til("/logg-inn/")
        self.sjekk("S1 på 320 px")

    def test_mobil_s3_testbrukeren_meny_apen(self):
        self.seed()
        self.mobil()
        self.gaa_til("/")
        self.side.locator("details.meny summary").click()
        self.side.wait_for_selector("nav[aria-label=Hovedmeny]", state="visible")
        self.sjekk("S3 testbrukeren med menyen åpen på 320 px")

    def test_mobil_s7_med_quizer(self):
        self.seed()
        self.mobil()
        self.gaa_til(f"/notater/{self.notat(HTML).pk}/")
        self.sjekk("S7 med quizer på 320 px")

    def test_mobil_s9_sporsmal(self):
        self.seed()
        okt = self.pabegynt_forsok()
        self.mobil()
        self.gaa_til(f"/okter/{okt.pk}/sporsmal/5/")
        self.sjekk("S9 spørsmål på 320 px")

    def test_mobil_s11_resultat(self):
        self.seed()
        okt, _ = self._levert_med_feil()
        self.mobil()
        self.gaa_til(f"/okter/{okt.pk}/resultat/")
        self.sjekk("S11 resultat på 320 px")

    # Testen selv: et brudd gir feil med regel, selector og URL.

    def test_brudd_gir_feil_med_regel_selector_og_url(self):
        self.gaa_til("/logg-inn/")
        self.side.evaluate(
            """() => {
                const bilde = document.createElement("img");
                bilde.id = "uten-alt";
                bilde.src = "/static/img/favicon.svg";
                document.querySelector("main").append(bilde);
            }"""
        )
        with self.assertRaises(AssertionError) as feil:
            self.sjekk("Med brudd")
        melding = str(feil.exception)
        self.assertIn("image-alt", melding)
        self.assertIn("#uten-alt", melding)
        self.assertIn(f"{self.live_server_url}/logg-inn/", melding)
