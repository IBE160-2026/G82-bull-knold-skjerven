"""Tester for `seed_testdata` og testbrukeren (FR-28, AD-21), én per rad i I/O-matrisen i spec 6.1."""

import json
import re
import shutil
import socket
import tempfile
from io import StringIO
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings

import ki
from ki import generering, les_fil
from ki.tests_generering import lag_quiz
from kontoer import testbruker
from studier.models import (
    Emne,
    Feilbankrad,
    Notat,
    Okt,
    Oktstatus,
    Okttype,
    Quiz,
    Svar,
)
from studier.services.emner import opprett_emne

TESTDOKUMENTER = Path(settings.BASE_DIR) / "testdokumenter"
DOKUMENTER = (
    "html-struktur-og-semantikk.pdf",
    "universell-utforming.docx",
    "javascript-og-dom.txt",
)
NIVAER = ("lett", "middels", "vanskelig")


def lag_mockmappe(mappe):
    """Mock-svar der hvert av de tre testdokumentene peker på sitt eget dokument."""
    manifest = {"standard": "html-struktur-og-semantikk", "filer": {}}
    for filnavn in DOKUMENTER:
        navn = filnavn.rsplit(".", 1)[0]
        manifest["filer"][les_fil(TESTDOKUMENTER / filnavn).sha256] = navn
        (mappe / navn).mkdir()
        for nivaa in NIVAER:
            data = lag_quiz(
                30, merke=f"{navn}-{nivaa} ", modell="claude-test", prompt_versjon="1"
            )
            (mappe / navn / f"{nivaa}.json").write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8"
            )
    (mappe / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def telling():
    """Antall av hver ting i hele databasen. Seed skal gi det samme hver gang."""
    okter = Okt.objects
    return {
        "brukere": get_user_model().objects.count(),
        "emner": Emne.objects.count(),
        "notater": Notat.objects.count(),
        "quizer": Quiz.objects.count(),
        "leverte forsøk": okter.filter(
            type=Okttype.FORSOK, status=Oktstatus.LEVERT
        ).count(),
        "påbegynte forsøk": okter.filter(
            type=Okttype.FORSOK, status=Oktstatus.PABEGYNT
        ).count(),
        "leverte øvinger": okter.filter(
            type=Okttype.OVING, status=Oktstatus.LEVERT
        ).count(),
        "påbegynte øvinger": okter.filter(
            type=Okttype.OVING, status=Oktstatus.PABEGYNT
        ).count(),
        "svar": Svar.objects.count(),
        "feilbankrader": Feilbankrad.objects.count(),
        "lærte": Feilbankrad.objects.filter(laert_tidspunkt__isnull=False).count(),
        "åpne": Feilbankrad.objects.filter(laert_tidspunkt__isnull=True).count(),
    }


FORVENTET = {
    "brukere": 1,
    "emner": 1,
    "notater": 3,
    "quizer": 3,
    "leverte forsøk": 3,
    "påbegynte forsøk": 1,
    "leverte øvinger": 1,
    "påbegynte øvinger": 0,
    # 10 + 10 + 3 levert på HTML, 4 i det påbegynte forsøket, 10 på DOCX.
    "svar": 37,
    "feilbankrader": 7,
    "lærte": 2,
    "åpne": 5,
}


class SeedTestCase(TestCase):
    """Midlertidig `MEDIA_ROOT` og mock-mappe for hver test."""

    def setUp(self):
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        innstillinger = override_settings(MEDIA_ROOT=media)
        innstillinger.enable()
        self.addCleanup(innstillinger.disable)
        self.media = Path(media)

        self.mock = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.mock, ignore_errors=True)
        lag_mockmappe(self.mock)
        patch = mock.patch.object(generering, "MOCK_MAPPE", self.mock)
        patch.start()
        self.addCleanup(patch.stop)

    def seed(self):
        ut = StringIO()
        # `slett_emne` sletter filene etter commit.
        with self.captureOnCommitCallbacks(execute=True):
            call_command("seed_testdata", stdout=ut)
        return ut.getvalue()

    def hent_testbruker(self):
        return get_user_model().objects.get(email=testbruker.EPOST)

    def notat(self, originalnavn):
        return Notat.objects.get(originalnavn=originalnavn)

    def filer_pa_disk(self):
        return sorted(sti for sti in self.media.rglob("*") if sti.is_file())


class ForsteKjoringTest(SeedTestCase):
    def test_tom_database_gir_det_faste_datasettet(self):
        ut = self.seed()
        self.assertEqual(telling(), FORVENTET)
        bruker = self.hent_testbruker()
        self.assertIsNotNone(bruker.vilkar_godtatt)
        self.assertEqual(
            list(bruker.emner.values_list("navn", flat=True)), ["Webutvikling"]
        )
        self.assertEqual(
            sorted(Notat.objects.values_list("originalnavn", flat=True)),
            sorted(DOKUMENTER),
        )
        self.assertEqual(len(self.filer_pa_disk()), 3)
        self.assertIn(testbruker.EPOST, ut)

    def test_quizene_og_de_apne_radene_per_notat(self):
        self.seed()
        html = self.notat("html-struktur-og-semantikk.pdf")
        docx = self.notat("universell-utforming.docx")
        txt = self.notat("javascript-og-dom.txt")
        self.assertEqual(
            sorted(html.quizer.values_list("vanskelighetsgrad", flat=True)),
            ["lett", "middels"],
        )
        self.assertEqual(
            list(docx.quizer.values_list("vanskelighetsgrad", flat=True)),
            ["vanskelig"],
        )
        self.assertFalse(txt.quizer.exists())
        for quiz in Quiz.objects.all():
            self.assertEqual(quiz.sporsmal.count(), 10)
            self.assertIs(quiz.forhandslagret, False)
        apne = Feilbankrad.objects.filter(laert_tidspunkt__isnull=True)
        self.assertEqual(apne.filter(sporsmal__quiz__notat=html).count(), 1)
        self.assertEqual(apne.filter(sporsmal__quiz__notat=docx).count(), 4)
        levert_docx = Okt.objects.get(notat=docx, status=Oktstatus.LEVERT)
        self.assertEqual((levert_docx.poengsum, levert_docx.antall), (6, 10))
        poeng = list(
            Okt.objects.filter(notat=html, type=Okttype.FORSOK, status=Oktstatus.LEVERT)
            .order_by("levert_tidspunkt", "pk")
            .values_list("poengsum", flat=True)
        )
        self.assertEqual(poeng, [7, 10])


class KjoresIgjenTest(SeedTestCase):
    def test_samme_antall_og_gamle_filer_slettet(self):
        self.seed()
        forste = telling()
        gamle_filer = self.filer_pa_disk()
        gamle_emne = self.hent_testbruker().emner.get().pk

        self.seed()
        self.assertEqual(telling(), forste)
        self.assertEqual(telling(), FORVENTET)
        for sti in gamle_filer:
            self.assertFalse(sti.exists(), sti)
        self.assertEqual(len(self.filer_pa_disk()), 3)
        self.assertFalse(Emne.objects.filter(pk=gamle_emne).exists())

    def test_passordet_settes_pa_nytt(self):
        self.seed()
        bruker = self.hent_testbruker()
        bruker.set_password("noe-annet-123")
        bruker.save()
        self.seed()
        self.assertTrue(self.hent_testbruker().check_password(testbruker.PASSORD))


class LaertOgIkkeLaertTest(SeedTestCase):
    def test_8_og_9_er_laert_og_10_er_apen(self):
        self.seed()
        lett = Quiz.objects.get(vanskelighetsgrad="lett")
        sporsmal = list(lett.sporsmal.order_by("id"))
        rader = {
            rad.sporsmal_id: rad
            for rad in Feilbankrad.objects.filter(sporsmal__quiz=lett)
        }
        for nr in range(1, 8):
            self.assertNotIn(sporsmal[nr - 1].pk, rader, f"spørsmål {nr}")
        self.assertIsNotNone(rader[sporsmal[7].pk].laert_tidspunkt)
        self.assertIsNotNone(rader[sporsmal[8].pk].laert_tidspunkt)
        self.assertIsNone(rader[sporsmal[9].pk].laert_tidspunkt)


class UtenMockSvarTest(SeedTestCase):
    def _uten_manifest(self):
        (self.mock / "manifest.json").unlink()

    def test_tom_database_gir_commanderror_og_ingen_bruker(self):
        self._uten_manifest()
        with self.assertRaisesMessage(CommandError, "lag_mocksvar"):
            self.seed()
        self.assertFalse(get_user_model().objects.exists())
        self.assertFalse(Emne.objects.exists())

    def _gammel_testbruker(self):
        bruker = get_user_model().objects.create_user(testbruker.EPOST, "gammelt-pass")
        emne = opprett_emne(bruker, "Gammelt emne")
        return bruker, emne

    def _assert_uendret(self, bruker, emne):
        bruker.refresh_from_db()
        self.assertTrue(bruker.check_password("gammelt-pass"))
        self.assertIsNone(bruker.vilkar_godtatt)
        self.assertTrue(Emne.objects.filter(pk=emne.pk, navn="Gammelt emne").exists())
        self.assertEqual(Emne.objects.count(), 1)
        self.assertFalse(Notat.objects.exists())

    def test_eksisterende_testbruker_er_uendret(self):
        bruker, emne = self._gammel_testbruker()
        self._uten_manifest()
        with self.assertRaisesMessage(CommandError, "lag_mocksvar"):
            self.seed()
        self._assert_uendret(bruker, emne)

    def test_ugyldig_manifest_gir_commanderror_og_ingenting_endret(self):
        bruker, emne = self._gammel_testbruker()
        (self.mock / "manifest.json").write_text("{", encoding="utf-8")
        with self.assertRaisesMessage(CommandError, "Ingenting er endret."):
            self.seed()
        self._assert_uendret(bruker, emne)

    def test_testdokument_mangler_i_manifestet(self):
        bruker, emne = self._gammel_testbruker()
        sti = self.mock / "manifest.json"
        manifest = json.loads(sti.read_text(encoding="utf-8"))
        sha = les_fil(TESTDOKUMENTER / "universell-utforming.docx").sha256
        del manifest["filer"][sha]
        sti.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesMessage(CommandError, "universell-utforming.docx"):
            self.seed()
        self._assert_uendret(bruker, emne)

    def test_nivafil_som_trengs_mangler(self):
        bruker, emne = self._gammel_testbruker()
        (self.mock / "html-struktur-og-semantikk" / "middels.json").unlink()
        with self.assertRaisesMessage(CommandError, "Ingenting er endret."):
            self.seed()
        self._assert_uendret(bruker, emne)


class OdelagtNivafilTest(SeedTestCase):
    def test_odelagt_nivafil_gir_commanderror_om_ki_mock(self):
        (self.mock / "universell-utforming" / "vanskelig.json").write_text(
            "{", encoding="utf-8"
        )
        with self.assertRaisesMessage(CommandError, "ki/mock/"):
            self.seed()


class DeaktivertTestbrukerTest(SeedTestCase):
    def test_deaktivert_testbruker_blir_aktiv_og_kan_logge_inn(self):
        get_user_model().objects.create_user(
            testbruker.EPOST, "gammelt-pass", is_active=False
        )
        self.seed()
        self.assertTrue(self.hent_testbruker().is_active)
        self.assertTrue(
            self.client.login(email=testbruker.EPOST, password=testbruker.PASSORD)
        )


class NettverkTest(SeedTestCase):
    def test_lykkes_uten_klient_og_nettverk_selv_med_testmodus_av(self):
        # Testkjøreren tvinger testmodus. Her er den av, så kommandoen må slå den på selv.
        with (
            mock.patch.object(ki, "_tvunget", False),
            override_settings(TESTMODUS="0", ANTHROPIC_API_KEY="sk-ant-test"),
            mock.patch.object(
                generering, "_klient", side_effect=AssertionError("KI kalt")
            ) as klient,
            mock.patch.object(
                socket.socket, "connect", side_effect=AssertionError("nettverkskall")
            ),
        ):
            self.assertIs(ki.er_testmodus(), False)
            self.seed()
        klient.assert_not_called()
        self.assertEqual(telling(), FORVENTET)
        self.assertFalse(Quiz.objects.filter(forhandslagret=True).exists())


class S1TestmodusTest(TestCase):
    def test_boksen_vises_over_skjemaet_i_testmodus(self):
        html = self.client.get("/logg-inn/").content.decode()
        self.assertIn("Testbruker", html)
        self.assertIn(testbruker.EPOST, html)
        self.assertIn(testbruker.PASSORD, html)
        self.assertLess(html.index("Testbruker"), html.index('id="epost"'))

    def test_boksen_vises_ikke_utenfor_testmodus(self):
        with mock.patch("farequiz.context_processors.er_testmodus", return_value=False):
            html = self.client.get("/logg-inn/").content.decode()
        self.assertNotIn("Testbruker", html)
        self.assertNotIn(testbruker.EPOST, html)
        self.assertNotIn(testbruker.PASSORD, html)


class InnloggingTest(SeedTestCase):
    def test_login_med_konstantene_og_s3_viser_dataene(self):
        self.seed()
        self.assertTrue(
            self.client.login(email=testbruker.EPOST, password=testbruker.PASSORD)
        )
        svar = self.client.get("/")
        self.assertEqual(svar.status_code, 200)
        html = svar.content.decode()
        self.assertIn("Webutvikling", html)
        self.assertRegex(html, r"Dekningsgrad \d+ %")
        self.assertIn("Fortsett der du slapp", html)
        self.assertIn("spørsmål 4 av 10", html)


class S7EtterSeedTest(SeedTestCase):
    def setUp(self):
        super().setUp()
        self.seed()
        self.client.force_login(self.hent_testbruker())

    def _s7(self, originalnavn):
        notat = self.notat(originalnavn)
        svar = self.client.get(f"/notater/{notat.pk}/")
        self.assertEqual(svar.status_code, 200)
        return svar.content.decode()

    def test_html_notatet_har_dekning_ov_pabegynt_og_historikk(self):
        html = self._s7("html-struktur-og-semantikk.pdf")
        nivaer = dict(re.findall(r"<dt[^>]*>(\w+)</dt>\s*<dd[^>]*>([^<]+)</dd>", html))
        self.assertRegex(nivaer["Lett"], r"^\d+ %$")
        self.assertRegex(nivaer["Middels"], r"^\d+ %$")
        self.assertEqual(nivaer["Vanskelig"], "Ingen quiz")
        self.assertIn("Øv på feil (1)", html)
        self.assertIn("Påbegynt – spørsmål 4 av 10", html)
        # Historikken står både som kort og som tabell. Tabellen har én rad per forsøk.
        self.assertEqual(html.count('<th scope="row"'), 2)

    def test_txt_notatet_har_ingen_quiz(self):
        html = self._s7("javascript-og-dom.txt")
        self.assertIn("Lag en quiz for å komme i gang", html)
        emne = self.hent_testbruker().emner.get()
        s4 = self.client.get(f"/emner/{emne.pk}/").content.decode()
        self.assertIn("Ingen quiz", s4)


class ReadmeTest(TestCase):
    def test_readme_har_kommandoen_og_innloggingen(self):
        readme = (Path(settings.BASE_DIR) / "README.md").read_text(encoding="utf-8")
        self.assertIn("seed_testdata", readme)
        self.assertIn(testbruker.EPOST, readme)
        self.assertIn(testbruker.PASSORD, readme)
