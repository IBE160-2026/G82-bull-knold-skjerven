import hashlib
import json
import shutil
import socket
import tempfile
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import anthropic
import httpx2 as httpx
from django.conf import settings
from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, override_settings

import ki
from ki import (
    PROMPT_VERSJON,
    Innhold,
    KIFeil,
    RaattSvar,
    generer,
    generering,
    les_fil,
    sjekk,
    visningsnavn,
)
from ki.fil import TYPER
from ki.management.commands import lag_mocksvar

NIVAER = ("lett", "middels", "vanskelig")
EKTE_MOCK = Path(generering.__file__).resolve().parent / "mock"
TESTDOKUMENTER = Path(settings.BASE_DIR) / "testdokumenter"


def lag_quiz(antall, merke="", **ekstra):
    return {
        "sprak": "nb",
        "sporsmal": [
            {
                "tekst": f"{merke}Spørsmål {nr}?",
                "begrunnelse": f"Fordi {nr}.",
                "alternativer": [
                    {"tekst": f"Riktig {nr}", "er_riktig": True},
                    {"tekst": f"Feil A {nr}", "er_riktig": False},
                    {"tekst": f"Feil B {nr}", "er_riktig": False},
                ],
            }
            for nr in range(1, antall + 1)
        ],
        **ekstra,
    }


class MockMappe:
    """Lager en mock-mappe med to dokumenter og patcher `ki.generering.MOCK_MAPPE`."""

    KJENT = "a" * 64
    ANNEN = "b" * 64

    def __enter__(self):
        self.mappe = Path(tempfile.mkdtemp())
        manifest = {
            "standard": "standard",
            "filer": {self.KJENT: "kjent", self.ANNEN: "standard"},
        }
        (self.mappe / "manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        for dokument in ("kjent", "standard"):
            (self.mappe / dokument).mkdir()
            for nivaa in NIVAER:
                data = lag_quiz(
                    30,
                    merke=f"{dokument}-{nivaa} ",
                    modell=f"claude-test-{dokument}",
                    prompt_versjon=f"v-{nivaa}",
                )
                (self.mappe / dokument / f"{nivaa}.json").write_text(
                    json.dumps(data, ensure_ascii=False), encoding="utf-8"
                )
        self.patch = mock.patch.object(generering, "MOCK_MAPPE", self.mappe)
        self.patch.start()
        return self

    def __exit__(self, *feil):
        self.patch.stop()
        shutil.rmtree(self.mappe, ignore_errors=True)


def innhold(sha256=MockMappe.KJENT, type="txt", data="Et notat."):
    return Innhold(sha256, type, data)


class MockGenereringTest(SimpleTestCase):
    def setUp(self):
        self.mock = MockMappe().__enter__()
        self.addCleanup(self.mock.__exit__)

    def test_kjent_fil_gir_de_forste_sporsmalene_fra_riktig_fil_og_niva(self):
        raatt = generer(innhold(), "vanskelig", 10, timeout=120)
        self.assertIsInstance(raatt, RaattSvar)
        self.assertIs(raatt.forhandslagret, False)
        self.assertEqual(raatt.modell, "claude-test-kjent")
        self.assertEqual(raatt.prompt_versjon, "v-vanskelig")
        utkast = sjekk(raatt.tekst, 10)
        self.assertEqual(utkast.sporsmal[0].tekst, "kjent-vanskelig Spørsmål 1?")
        self.assertEqual(utkast.sporsmal[-1].tekst, "kjent-vanskelig Spørsmål 10?")
        self.assertIs(utkast.forhandslagret, False)
        self.assertEqual(utkast.modell, "claude-test-kjent")
        self.assertEqual(utkast.prompt_versjon, "v-vanskelig")

    def test_ukjent_fil_gir_standarddokumentet_og_forhandslagret(self):
        raatt = generer(innhold(sha256="c" * 64), "lett", 5, timeout=120)
        self.assertIs(raatt.forhandslagret, True)
        utkast = sjekk(raatt.tekst, 5)
        self.assertIs(utkast.forhandslagret, True)
        self.assertEqual(utkast.sporsmal[0].tekst, "standard-lett Spørsmål 1?")

    def test_kjent_fil_som_peker_pa_standard_er_ikke_forhandslagret(self):
        raatt = generer(innhold(sha256=MockMappe.ANNEN), "lett", 5, timeout=120)
        self.assertIs(raatt.forhandslagret, False)

    def test_30_pa_hvert_dokument_og_niva(self):
        for sha256 in (MockMappe.KJENT, "c" * 64):
            for nivaa in NIVAER:
                with self.subTest(sha256=sha256[:4], nivaa=nivaa):
                    raatt = generer(innhold(sha256=sha256), nivaa, 30, timeout=120)
                    self.assertEqual(len(sjekk(raatt.tekst, 30).sporsmal), 30)

    def test_blokkert_nett_gir_samme_svar_uten_kall(self):
        with mock.patch.object(
            socket.socket, "connect", side_effect=AssertionError("nettverkskall")
        ) as connect:
            raatt = generer(innhold(), "middels", 10, timeout=120)
        connect.assert_not_called()
        self.assertEqual(len(sjekk(raatt.tekst, 10).sporsmal), 10)

    def test_testmodus_lager_aldri_klient(self):
        with mock.patch.object(generering, "_klient") as klient:
            generer(innhold(), "middels", 10, timeout=120)
        klient.assert_not_called()

    def test_manglende_mockfiler_gir_api_feil(self):
        with (
            mock.patch.object(
                generering, "MOCK_MAPPE", self.mock.mappe / "finnes-ikke"
            ),
            self.assertRaises(KIFeil) as fanget,
        ):
            generer(innhold(), "middels", 10, timeout=120)
        self.assertEqual(fanget.exception.kode, "api_feil")

    def test_manifest_med_feil_form_gir_api_feil(self):
        manifest = self.mock.mappe / "manifest.json"
        for innhold_ in ("[]", json.dumps({"filer": {}})):
            manifest.write_text(innhold_, encoding="utf-8")
            with self.subTest(manifest=innhold_), self.assertRaises(KIFeil) as fanget:
                generer(innhold(), "middels", 10, timeout=120)
            self.assertEqual(fanget.exception.kode, "api_feil")

    def test_mockfil_med_feil_form_gir_api_feil(self):
        (self.mock.mappe / "kjent" / "middels.json").write_text("{}", encoding="utf-8")
        with self.assertRaises(KIFeil) as fanget:
            generer(innhold(), "middels", 10, timeout=120)
        self.assertEqual(fanget.exception.kode, "api_feil")


class UgyldigValgTest(SimpleTestCase):
    def test_ugyldig_vanskelighetsgrad_og_antall_gir_valueerror(self):
        for nivaa, antall in (
            ("ekstrem", 10),
            ("", 10),
            ("middels", 0),
            ("middels", 31),
            ("middels", -1),
            ("middels", "10"),
            ("middels", True),
        ):
            with (
                self.subTest(nivaa=nivaa, antall=antall),
                self.assertRaises(ValueError),
            ):
                generer(innhold(), nivaa, antall, timeout=120)


class FalskKlient:
    """Erstatter `anthropic.Anthropic`. Husker kallet og gir `svar` eller hever `feil`."""

    def __init__(self, svar=None, feil=None):
        self.svar = svar
        self.feil = feil
        self.kall = None
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.kall = kwargs
        if self.feil is not None:
            raise self.feil
        return self.svar


def modellsvar(tekst, model="claude-sonnet-5-5", stop_reason="end_turn"):
    return SimpleNamespace(
        model=model,
        stop_reason=stop_reason,
        content=[
            SimpleNamespace(type="thinking", thinking=""),
            SimpleNamespace(type="text", text=tekst),
        ],
    )


_FORESPORSEL = httpx.Request("POST", "https://api.anthropic.com/v1/messages")


def statusfeil(klasse, status, melding="feil"):
    svar = httpx.Response(status, request=_FORESPORSEL)
    return klasse(melding, response=svar, body=None)


@mock.patch.object(ki, "_tvunget", False)
@override_settings(
    TESTMODUS="0", ANTHROPIC_API_KEY="sk-ant-test", KI_MODELL="claude-test-modell"
)
class ModellGenereringTest(SimpleTestCase):
    def kjor(self, klient, innhold_=None, nivaa="middels", antall=10, timeout=120):
        with mock.patch.object(generering, "_klient", return_value=klient) as lag:
            raatt = generer(innhold_ or innhold(), nivaa, antall, timeout=timeout)
        lag.assert_called_once_with(timeout)
        return raatt

    def assertKIFeil(self, kode, feil):
        with self.assertRaises(KIFeil) as fanget:
            self.kjor(FalskKlient(feil=feil))
        self.assertEqual(fanget.exception.kode, kode)

    def test_gyldig_svar_far_modell_prompt_versjon_og_forhandslagret(self):
        klient = FalskKlient(
            svar=modellsvar(json.dumps(lag_quiz(10)), model="claude-sonnet-5")
        )
        raatt = self.kjor(klient)
        self.assertEqual(raatt.modell, "claude-sonnet-5")
        self.assertEqual(raatt.prompt_versjon, PROMPT_VERSJON)
        self.assertIs(raatt.forhandslagret, False)
        self.assertEqual(raatt.stoppgrunn, "end_turn")
        data = json.loads(raatt.tekst)
        self.assertEqual(data["modell"], "claude-sonnet-5")
        self.assertEqual(data["prompt_versjon"], PROMPT_VERSJON)
        self.assertIs(data["forhandslagret"], False)
        self.assertEqual(data["sprak"], "nb")
        utkast = sjekk(raatt.tekst, 10)
        self.assertEqual(utkast.modell, "claude-sonnet-5")

    def test_kallet_har_modell_skjema_effort_og_fallback(self):
        klient = FalskKlient(svar=modellsvar(json.dumps(lag_quiz(7))))
        self.kjor(klient, nivaa="vanskelig", antall=7)
        kall = klient.kall
        self.assertEqual(kall["model"], "claude-test-modell")
        self.assertEqual(kall["output_config"]["effort"], "medium")
        self.assertEqual(kall["output_config"]["format"]["type"], "json_schema")
        skjema = kall["output_config"]["format"]["schema"]
        self.assertEqual(set(skjema["required"]), {"sprak", "sporsmal"})
        self.assertEqual(kall["betas"], ["server-side-fallback-2026-07-01"])
        self.assertEqual(kall["fallbacks"], "default")
        blokker = kall["messages"][0]["content"]
        self.assertEqual(
            blokker[0], {"type": "text", "text": "<notat>\nEt notat.\n</notat>"}
        )
        self.assertIn("nøyaktig 7 spørsmål", blokker[-1]["text"])
        self.assertIn("vanskelig", blokker[-1]["text"])

    def test_pdf_sendes_som_dokumentblokk(self):
        klient = FalskKlient(svar=modellsvar(json.dumps(lag_quiz(10))))
        self.kjor(klient, innhold_=innhold(type="pdf", data=b"%PDF-1.7 test"))
        dokument = klient.kall["messages"][0]["content"][0]
        self.assertEqual(dokument["type"], "document")
        self.assertEqual(dokument["source"]["media_type"], "application/pdf")
        self.assertEqual(dokument["source"]["data"], "JVBERi0xLjcgdGVzdA==")

    def test_docx_og_txt_sendes_som_tekst(self):
        for filtype in ("docx", "txt"):
            klient = FalskKlient(svar=modellsvar(json.dumps(lag_quiz(10))))
            self.kjor(klient, innhold_=innhold(type=filtype, data="Notat om DOM."))
            blokker = klient.kall["messages"][0]["content"]
            with self.subTest(filtype=filtype):
                self.assertTrue(all(b["type"] == "text" for b in blokker))
                self.assertIn("Notat om DOM.", blokker[0]["text"])

    def test_ugyldig_json_returneres_uendret(self):
        raatt = self.kjor(FalskKlient(svar=modellsvar("ikke json")))
        self.assertEqual(raatt.tekst, "ikke json")
        with self.assertRaises(KIFeil) as fanget:
            sjekk(raatt.tekst, 10)
        self.assertEqual(fanget.exception.kode, "format")

    def test_avkuttet_svar_har_stoppgrunn_max_tokens(self):
        avkuttet = '{"sprak": "nb", "sporsmal": [{"tekst": "Halv'
        raatt = self.kjor(
            FalskKlient(svar=modellsvar(avkuttet, stop_reason="max_tokens"))
        )
        self.assertEqual(raatt.stoppgrunn, "max_tokens")
        with self.assertRaises(KIFeil) as fanget:
            sjekk(raatt.tekst, 10)
        self.assertEqual(fanget.exception.kode, "format")

    def test_mock_svar_har_tom_stoppgrunn(self):
        self.assertEqual(RaattSvar("{}", False, "m", "1").stoppgrunn, "")

    def test_json_som_ikke_er_objekt_returneres_uendret(self):
        raatt = self.kjor(FalskKlient(svar=modellsvar("[1, 2]")))
        self.assertEqual(raatt.tekst, "[1, 2]")

    def test_ugyldig_nokkel(self):
        self.assertKIFeil("api_nokkel", statusfeil(anthropic.AuthenticationError, 401))
        self.assertKIFeil(
            "api_nokkel", statusfeil(anthropic.PermissionDeniedError, 403)
        )

    def test_for_stor(self):
        self.assertKIFeil("for_stor", statusfeil(anthropic.ContentTooLargeError, 413))
        self.assertKIFeil(
            "for_stor",
            statusfeil(
                anthropic.BadRequestError,
                400,
                "A maximum of 600 PDF pages may be provided.",
            ),
        )

    def test_annen_bad_request_er_api_feil(self):
        self.assertKIFeil(
            "api_feil", statusfeil(anthropic.BadRequestError, 400, "invalid model")
        )

    def test_timeout(self):
        self.assertKIFeil("timeout", anthropic.APITimeoutError(request=_FORESPORSEL))
        self.assertKIFeil("timeout", statusfeil(anthropic.RequestTimeoutError, 408))
        self.assertKIFeil("timeout", statusfeil(anthropic.GatewayTimeoutError, 504))

    def test_andre_feil_gir_api_feil(self):
        self.assertKIFeil(
            "api_feil", anthropic.APIConnectionError(request=_FORESPORSEL)
        )
        self.assertKIFeil("api_feil", statusfeil(anthropic.InternalServerError, 500))
        self.assertKIFeil("api_feil", statusfeil(anthropic.RateLimitError, 429))
        self.assertKIFeil("api_feil", anthropic.CredentialsError("ingen nøkkel"))

    def test_avslag_gir_api_feil(self):
        klient = FalskKlient(svar=modellsvar("", stop_reason="refusal"))
        with self.assertRaises(KIFeil) as fanget:
            self.kjor(klient)
        self.assertEqual(fanget.exception.kode, "api_feil")

    def test_klienten_far_nokkel_timeout_og_ingen_nye_forsok(self):
        with mock.patch.object(generering.anthropic, "Anthropic") as klasse:
            generering._klient(120)
        klasse.assert_called_once_with(
            api_key="sk-ant-test", timeout=120, max_retries=0
        )


class VisningsnavnTest(SimpleTestCase):
    def test_kjente_former(self):
        for modell, navn in (
            ("claude-sonnet-5-5", "Claude Sonnet 5.5"),
            ("claude-haiku-5-5", "Claude Haiku 5.5"),
            ("claude-opus-5", "Claude Opus 5"),
        ):
            with self.subTest(modell=modell):
                self.assertEqual(visningsnavn(modell), navn)

    def test_ukjent_form_gir_strengen_uendret(self):
        for modell in ("gpt-x", "claude-opus-4-5-20251101", "", "Claude Sonnet 5.5"):
            with self.subTest(modell=modell):
                self.assertEqual(visningsnavn(modell), modell)


# Fingeravtrykket av prompten for hver PROMPT_VERSJON (AD-11). Endres prompten,
# skjemaet, nivåene, effort eller brukerturen, feiler testen til versjonen er økt.
LASTE_FINGERAVTRYKK = {
    "1": "d38d7dc049742498d319ed4175b84817947f5cc7feb3b1e4738dc82777d6f3d2",
}


def prompt_fingeravtrykk():
    deler = [
        generering.SYSTEMPROMPT,
        json.dumps(generering.SKJEMA, sort_keys=True),
        json.dumps(generering._NIVAER, sort_keys=True),
        generering.EFFORT,
        # Brukerturen: oppgaveteksten og `<notat>`-rammen rundt teksten.
        json.dumps(
            generering._innhold_blokker(Innhold("", "txt", "X"), "lett", 1),
            sort_keys=True,
            ensure_ascii=False,
        ),
    ]
    return hashlib.sha256("\0".join(deler).encode("utf-8")).hexdigest()


class PromptVersjonTest(SimpleTestCase):
    def test_prompt_versjon_er_definert_ett_sted(self):
        treff = [
            fil.name
            for fil in Path(generering.__file__).resolve().parent.rglob("*.py")
            if not fil.name.startswith("tests")
            and "PROMPT_VERSJON = " in fil.read_text(encoding="utf-8")
        ]
        self.assertEqual(treff, ["generering.py"])
        self.assertIs(ki.PROMPT_VERSJON, generering.PROMPT_VERSJON)

    def test_prompten_er_last_til_prompt_versjon(self):
        faktisk = prompt_fingeravtrykk()
        self.assertEqual(
            faktisk,
            LASTE_FINGERAVTRYKK.get(generering.PROMPT_VERSJON),
            "SYSTEMPROMPT, SKJEMA, _NIVAER, EFFORT eller _innhold_blokker er endret "
            "uten ny "
            "PROMPT_VERSJON. Øk PROMPT_VERSJON i ki/generering.py, legg "
            f'"<ny versjon>": "{faktisk}" i LASTE_FINGERAVTRYKK i denne testen, og '
            "lag mock-svarene på nytt med `uv run python manage.py lag_mocksvar`.",
        )


class EkteMockfilerTest(SimpleTestCase):
    """Sjekker de committede mock-filene i `ki/mock/`."""

    def test_alle_mockfiler_er_gyldige_med_30_sporsmal(self):
        for fil in sorted(EKTE_MOCK.glob("*/*.json")):
            with self.subTest(fil=f"{fil.parent.name}/{fil.name}"):
                self.assertIn(fil.stem, NIVAER)
                utkast = sjekk(fil.read_text(encoding="utf-8"), 30)
                self.assertIs(utkast.forhandslagret, False)
                self.assertEqual(utkast.prompt_versjon, ki.PROMPT_VERSJON)

    def test_manifestet_dekker_testdokumentene(self):
        manifest = json.loads((EKTE_MOCK / "manifest.json").read_text(encoding="utf-8"))
        dokumenter = {manifest["standard"], *manifest["filer"].values()}
        for dokument in dokumenter:
            for nivaa in NIVAER:
                with self.subTest(dokument=dokument, nivaa=nivaa):
                    self.assertTrue((EKTE_MOCK / dokument / f"{nivaa}.json").is_file())
        for sti in sorted(TESTDOKUMENTER.iterdir()):
            if sti.suffix.lower() in TYPER:
                with self.subTest(testdokument=sti.name):
                    self.assertIn(les_fil(sti).sha256, manifest["filer"])


class LagMocksvarTest(SimpleTestCase):
    def setUp(self):
        self.mappe = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.mappe, True)
        patch = mock.patch.object(generering, "MOCK_MAPPE", self.mappe)
        patch.start()
        self.addCleanup(patch.stop)

    def falsk_generer(self, svar_for_kall=None):
        kall = []

        def generer_(innhold_, nivaa, antall, timeout):
            kall.append((innhold_.sha256, nivaa, antall, timeout))
            tekst = (svar_for_kall or {}).get(len(kall))
            if isinstance(tekst, KIFeil):
                raise tekst
            if tekst is None:
                tekst = json.dumps(
                    lag_quiz(
                        antall,
                        merke=f"{nivaa} ",
                        modell="claude-sonnet-5-5",
                        prompt_versjon="1",
                    )
                )
            return RaattSvar(tekst, False, "claude-sonnet-5-5", "1")

        return generer_, kall

    def kjor(self, generer_):
        ut = StringIO()
        with (
            mock.patch.object(ki, "_tvunget", False),
            override_settings(TESTMODUS="0", ANTHROPIC_API_KEY="sk-ant-test"),
            mock.patch.object(lag_mocksvar, "generer", side_effect=generer_),
        ):
            call_command("lag_mocksvar", stdout=ut)
        return ut.getvalue()

    def test_nekter_i_testmodus(self):
        with (
            mock.patch.object(lag_mocksvar, "generer") as falsk,
            self.assertRaises(CommandError),
        ):
            call_command("lag_mocksvar", stdout=StringIO())
        falsk.assert_not_called()
        self.assertEqual(list(self.mappe.iterdir()), [])

    def test_skriver_mockfiler_og_manifest_som_generer_kan_bruke(self):
        generer_, kall = self.falsk_generer()
        ut = self.kjor(generer_)

        self.assertEqual(len(kall), 15)
        self.assertTrue(all(k[2] == 30 and k[3] == 300 for k in kall))
        manifest = json.loads(
            (self.mappe / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["standard"], "html-struktur-og-semantikk")
        self.assertEqual(len(manifest["filer"]), 5)
        for sti in TESTDOKUMENTER.iterdir():
            if sti.suffix.lower() in TYPER:
                self.assertEqual(manifest["filer"][les_fil(sti).sha256], sti.stem)
        for dokument in manifest["filer"].values():
            for nivaa in NIVAER:
                fil = self.mappe / dokument / f"{nivaa}.json"
                data = json.loads(fil.read_text(encoding="utf-8"))
                self.assertEqual(
                    set(data), {"sprak", "modell", "prompt_versjon", "sporsmal"}
                )
                self.assertEqual(
                    len(sjekk(fil.read_text(encoding="utf-8"), 30).sporsmal), 30
                )
                self.assertNotIn(b"\r\n", fil.read_bytes())

        # Innhold skrives aldri ut, bare varighet.
        self.assertNotIn("Spørsmål", ut)
        self.assertRegex(ut, r"\d+\.\d s")

        # Mock-veien leser filene som ble skrevet.
        txt = les_fil(TESTDOKUMENTER / "javascript-og-dom.txt")
        raatt = generer(txt, "vanskelig", 4, timeout=120)
        self.assertIs(raatt.forhandslagret, False)
        self.assertEqual(
            sjekk(raatt.tekst, 4).sporsmal[0].tekst, "vanskelig Spørsmål 1?"
        )

    def test_formatfeil_gir_ett_nytt_forsok(self):
        generer_, kall = self.falsk_generer({1: "ikke json"})
        ut = self.kjor(generer_)
        self.assertEqual(len(kall), 16)
        self.assertEqual(kall[0][:2], kall[1][:2])
        self.assertIn("format", ut)
        self.assertTrue((self.mappe / "manifest.json").is_file())

    def test_timeout_og_api_feil_gir_ett_nytt_forsok(self):
        for kode in ("timeout", "api_feil"):
            with self.subTest(kode=kode):
                generer_, kall = self.falsk_generer({14: KIFeil(kode)})
                ut = self.kjor(generer_)
                self.assertEqual(len(kall), 16)
                self.assertEqual(kall[13][:2], kall[14][:2])
                self.assertIn(kode, ut)
                self.assertTrue((self.mappe / "manifest.json").is_file())

    def test_to_formatfeil_stopper_uten_a_skrive_filer(self):
        generer_, kall = self.falsk_generer({1: "ikke json", 2: "ikke json"})
        with self.assertRaises(CommandError):
            self.kjor(generer_)
        self.assertEqual(len(kall), 2)
        self.assertEqual(list(self.mappe.iterdir()), [])

    def test_nokkel_og_for_stor_stopper_uten_nytt_forsok(self):
        for kode in ("api_nokkel", "for_stor"):
            with self.subTest(kode=kode):
                generer_, kall = self.falsk_generer({1: KIFeil(kode)})
                with self.assertRaises(CommandError) as fanget:
                    self.kjor(generer_)
                self.assertEqual(len(kall), 1)
                self.assertIn(kode, str(fanget.exception))
                self.assertEqual(list(self.mappe.iterdir()), [])
