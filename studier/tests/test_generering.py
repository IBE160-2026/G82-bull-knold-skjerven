"""Tester for å lage quiz med fremdrift (FR-11–FR-14, AD-9, AD-19), én per rad i I/O-matrisen i spec 2.4."""

import json
import re
import shutil
import tempfile
from datetime import timedelta
from pathlib import Path
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import TransactionTestCase, override_settings
from django.utils import timezone

import ki
from farequiz import feilmeldinger
from ki.tests_generering import MockMappe
from studier.models import (
    Alternativ,
    Emne,
    Genereringsjobb,
    Jobbstatus,
    Quiz,
    Sporsmal,
)
from studier.services import generering
from studier.services.generering import (
    aktiv_jobb,
    generer_synkront,
    kjor_steg,
    opprett_jobb,
)
from studier.services.notater import last_opp
from studier.tests.fabrikk import lag_bruker
from studier.tests.test_slett_emne import MedFilerTestCase, _innlogget

FILINNHOLD = "Hemmelig notatinnhold om HTML og CSS."


def _quiz_json(antall, **ekstra):
    data = {
        "sprak": "nb",
        "modell": "claude-test",
        "prompt_versjon": "7",
        "forhandslagret": False,
        "sporsmal": [
            {
                "tekst": f"Spørsmål {nr}?",
                "begrunnelse": f"Fordi {nr}.",
                "alternativer": [
                    {"tekst": f"Riktig {nr}", "er_riktig": True},
                    {"tekst": f"Feil A {nr}", "er_riktig": False},
                    {"tekst": f"Feil B {nr}", "er_riktig": False},
                ],
            }
            for nr in range(1, antall + 1)
        ],
    }
    data.update(ekstra)
    return json.dumps(data, ensure_ascii=False)


def _raatt(antall=10, tekst=None):
    return ki.RaattSvar(
        tekst=_quiz_json(antall) if tekst is None else tekst,
        forhandslagret=False,
        modell="claude-test",
        prompt_versjon="7",
    )


UGYLDIG = _raatt(tekst='{"sprak": "nb", "sporsmal": []}')


class GenereringTestCase(MedFilerTestCase):
    def setUp(self):
        super().setUp()
        self.emne = Emne.objects.create(eier=self.bruker, navn="Webutvikling")
        self.notat = last_opp(
            self.emne,
            SimpleUploadedFile("notat.txt", FILINNHOLD.encode()),
            self.bruker,
        )
        self.notat_url = f"/notater/{self.notat.pk}/"

    def _jobb(self, **felter):
        return Genereringsjobb.objects.create(
            notat=self.notat,
            vanskelighetsgrad=felter.pop("vanskelighetsgrad", "middels"),
            antall=felter.pop("antall", 10),
            **felter,
        )

    def _steg(self, jobb):
        return self.client.post(f"/jobber/{jobb.pk}/steg/")


class LagQuizTest(GenereringTestCase):
    def test_post_middels_10_lager_jobb_og_sender_til_s8(self):
        svar = self.client.post(
            self.notat_url, {"vanskelighetsgrad": "middels", "antall": "10"}
        )
        jobb = Genereringsjobb.objects.get()
        self.assertRedirects(svar, f"/jobber/{jobb.pk}/")
        self.assertEqual(jobb.notat, self.notat)
        self.assertEqual(jobb.status, Jobbstatus.LESER)
        self.assertEqual(jobb.runde, 1)
        self.assertEqual(jobb.vanskelighetsgrad, "middels")
        self.assertEqual(jobb.antall, 10)
        self.assertIs(jobb.i_gang, False)

    def test_ugyldig_antall_gir_feil_ved_feltet_og_ingen_jobb(self):
        for antall in ("4", "31", "abc", ""):
            with self.subTest(antall=antall):
                svar = self.client.post(
                    self.notat_url, {"vanskelighetsgrad": "lett", "antall": antall}
                )
                self.assertEqual(svar.status_code, 200)
                html = svar.content.decode()
                self.assertRegex(
                    html,
                    r'<p id="feil-antall" role="alert" tabindex="-1" autofocus[^>]*>'
                    + re.escape(feilmeldinger.ANTALL_UGYLDIG)
                    + "</p>",
                )
                self.assertIn('aria-describedby="hjelp-antall feil-antall"', html)
                self.assertIn('aria-invalid="true"', html)
                # Valget av nivå beholdes.
                self.assertRegex(html, r'value="lett" checked')
                self.assertFalse(Genereringsjobb.objects.exists())

    def test_aktiv_jobb_gir_ingen_ny_jobb_og_sender_til_den(self):
        data = {"vanskelighetsgrad": "middels", "antall": "10"}
        forste = self.client.post(self.notat_url, data)
        andre = self.client.post(
            self.notat_url, {"vanskelighetsgrad": "lett", "antall": "5"}
        )
        jobb = Genereringsjobb.objects.get()
        self.assertRedirects(forste, f"/jobber/{jobb.pk}/")
        self.assertRedirects(andre, f"/jobber/{jobb.pk}/")
        self.assertEqual(opprett_jobb(self.notat, "vanskelig", 30), jobb)
        self.assertEqual(Genereringsjobb.objects.count(), 1)

    def test_ferdig_eller_feilet_jobb_er_ikke_aktiv(self):
        self._jobb(status=Jobbstatus.FERDIG)
        self._jobb(status=Jobbstatus.FEILET, feilkode="api_feil")
        self.assertIsNone(aktiv_jobb(self.notat))
        ny = opprett_jobb(self.notat, "lett", 5)
        self.assertEqual(ny.status, Jobbstatus.LESER)
        self.assertEqual(Genereringsjobb.objects.count(), 3)

    def test_opprett_jobb_avviser_ugyldig_valg(self):
        for nivaa, antall in (
            ("ukjent", 10),
            ("lett", 4),
            ("lett", 31),
            ("lett", "10"),
        ):
            with (
                self.subTest(nivaa=nivaa, antall=antall),
                self.assertRaises(ValueError),
            ):
                opprett_jobb(self.notat, nivaa, antall)
        self.assertFalse(Genereringsjobb.objects.exists())


class HeleKjedenTest(GenereringTestCase):
    def setUp(self):
        super().setUp()
        self.mock = MockMappe().__enter__()
        self.addCleanup(self.mock.__exit__)

    def test_tre_steg_kall_gir_ferdig_quiz_og_hx_redirect(self):
        jobb = opprett_jobb(self.notat, "vanskelig", 7)

        svar = self._steg(jobb)
        jobb.refresh_from_db()
        self.assertEqual(jobb.status, Jobbstatus.LAGER)
        self.assertIs(jobb.i_gang, False)
        html = svar.content.decode()
        self.assertIn("Leser filen (ferdig)", html)
        self.assertIn("Lager spørsmål (pågår)", html)
        self.assertIn("Sjekker quizen (venter)", html)
        # Et fullført steg gir ny spørring med en gang.
        self.assertIn(f'hx-post="/jobber/{jobb.pk}/steg/" hx-trigger="load"', html)
        self.assertNotIn("HX-Redirect", svar.headers)

        self._steg(jobb)
        jobb.refresh_from_db()
        self.assertEqual(jobb.status, Jobbstatus.SJEKKER)
        self.assertNotIn(FILINNHOLD, jobb.raatt_svar)
        self.assertIs(jobb.forhandslagret, True)  # Ukjent fil i mock-mappen.
        self.assertEqual(jobb.modell, "claude-test-standard")
        self.assertEqual(jobb.prompt_versjon, "v-vanskelig")

        svar = self._steg(jobb)
        jobb.refresh_from_db()
        self.assertEqual(jobb.status, Jobbstatus.FERDIG)
        self.assertEqual(svar["HX-Redirect"], self.notat_url)

        quiz = Quiz.objects.get()
        self.assertEqual(quiz.jobb, jobb)
        self.assertEqual(quiz.notat, self.notat)
        self.assertEqual(quiz.vanskelighetsgrad, "vanskelig")
        self.assertEqual(quiz.sprak, "nb")
        self.assertEqual(quiz.modell, "claude-test-standard")
        self.assertEqual(quiz.prompt_versjon, "v-vanskelig")
        self.assertIs(quiz.forhandslagret, True)
        self.assertEqual(quiz.sporsmal.count(), 7)
        for sporsmal in quiz.sporsmal.all():
            self.assertTrue(sporsmal.begrunnelse)
            self.assertEqual(sporsmal.alternativer.count(), 3)
            self.assertEqual(sporsmal.alternativer.filter(er_riktig=True).count(), 1)

        # Et nytt kall på en ferdig jobb gjør ingenting.
        self.assertIs(kjor_steg(jobb.pk), False)
        self.assertEqual(Quiz.objects.count(), 1)

    def test_s8_for_ferdig_jobb_sender_til_s7(self):
        quiz = generer_synkront(self.notat, "middels", 10)
        svar = self.client.get(f"/jobber/{quiz.jobb.pk}/")
        self.assertRedirects(svar, self.notat_url)


class StubbetGenereringTestCase(GenereringTestCase):
    def _kjor_alle(self, jobb, maks=5):
        for _ in range(maks):
            kjor_steg(jobb.pk)
            jobb.refresh_from_db()
            if jobb.status in (Jobbstatus.FERDIG, Jobbstatus.FEILET):
                break
        return jobb


class FormatfeilTest(StubbetGenereringTestCase):
    def test_formatfeil_en_gang_gir_runde_2_og_quiz(self):
        jobb = opprett_jobb(self.notat, "middels", 10)
        with mock.patch.object(
            ki, "generer", side_effect=[UGYLDIG, _raatt(10)]
        ) as generer:
            kjor_steg(jobb.pk)  # leser
            kjor_steg(jobb.pk)  # lager
            kjor_steg(jobb.pk)  # sjekker, feil format
            jobb.refresh_from_db()
            self.assertEqual(jobb.status, Jobbstatus.LAGER)
            self.assertEqual(jobb.runde, 2)
            self.assertFalse(Quiz.objects.exists())
            jobb = self._kjor_alle(jobb)
        self.assertEqual(generer.call_count, 2)
        self.assertEqual(jobb.status, Jobbstatus.FERDIG)
        self.assertEqual(Quiz.objects.get().sporsmal.count(), 10)

    def test_formatfeil_to_ganger_gir_feilet_format_og_ingen_quiz(self):
        jobb = opprett_jobb(self.notat, "middels", 10)
        with (
            mock.patch.object(ki, "generer", return_value=UGYLDIG) as generer,
            self.assertLogs("studier.services.generering", "WARNING") as logg,
        ):
            jobb = self._kjor_alle(jobb)
        self.assertEqual(generer.call_count, 2)
        self.assertEqual(jobb.status, Jobbstatus.FEILET)
        self.assertEqual(jobb.feilkode, "format")
        self.assertEqual(jobb.runde, 2)
        self.assertFalse(Quiz.objects.exists())
        self.assertFalse(Sporsmal.objects.exists())
        self.assertTrue(
            any(str(jobb.pk) in linje and "format" in linje for linje in logg.output)
        )

        svar = self._steg(jobb)
        html = svar.content.decode()
        self.assertIn(
            f'<p role="alert" class="mb-2 font-semibold text-error">'
            f"{feilmeldinger.GENERERING_FEIL['format']}</p>",
            html,
        )
        self.assertIn(f'href="{self.notat_url}"', html)
        self.assertNotIn("hx-post", html)
        self.assertIn("Prøv igjen</button>", html)


class KIFeilTest(StubbetGenereringTestCase):
    def test_kifeil_i_lager_gir_feilet_med_koden_og_logg_uten_innhold(self):
        jobb = opprett_jobb(self.notat, "lett", 5)
        with (
            mock.patch.object(ki, "generer", side_effect=ki.KIFeil("api_feil", "nede")),
            self.assertLogs("studier.services.generering", "INFO") as logg,
        ):
            jobb = self._kjor_alle(jobb)
        self.assertEqual(jobb.status, Jobbstatus.FEILET)
        self.assertEqual(jobb.feilkode, "api_feil")
        self.assertIs(jobb.i_gang, False)
        self.assertFalse(Quiz.objects.exists())
        self.assertIn(
            f"Genereringsjobb {jobb.pk} feilet med koden api_feil.", logg.output[-1]
        )
        self.assertFalse(any(FILINNHOLD in linje for linje in logg.output))

        html = self._steg(jobb).content.decode()
        self.assertIn('role="alert"', html)
        self.assertIn(feilmeldinger.GENERERING_FEIL["api_feil"], html)

    def test_uventet_feil_i_steg_gir_feilet_api_feil(self):
        jobb = opprett_jobb(self.notat, "lett", 5)
        with (
            mock.patch.object(ki, "generer", side_effect=RuntimeError("x")),
            self.assertLogs("studier.services.generering", "WARNING") as logg,
        ):
            jobb = self._kjor_alle(jobb)
        self.assertEqual(jobb.status, Jobbstatus.FEILET)
        self.assertEqual(jobb.feilkode, "api_feil")
        self.assertIs(jobb.i_gang, False)
        self.assertFalse(Quiz.objects.exists())
        self.assertTrue(any(str(jobb.pk) in linje for linje in logg.output))
        self.assertFalse(any(FILINNHOLD in linje for linje in logg.output))
        html = self._steg(jobb).content.decode()
        self.assertIn(feilmeldinger.GENERERING_FEIL["api_feil"], html)

    def test_kifeil_i_leser_gir_feilet_med_koden(self):
        jobb = opprett_jobb(self.notat, "lett", 5)
        (self.media / self.notat.fil.name).unlink()
        with (
            mock.patch.object(ki, "generer") as generer,
            self.assertLogs("studier.services.generering", "WARNING"),
        ):
            kjor_steg(jobb.pk)
        jobb.refresh_from_db()
        self.assertEqual(jobb.status, Jobbstatus.FEILET)
        self.assertEqual(jobb.feilkode, "api_feil")
        generer.assert_not_called()

    def test_lager_far_gjenstaende_tid_som_timeout(self):
        jobb = opprett_jobb(self.notat, "lett", 5)
        Genereringsjobb.objects.filter(pk=jobb.pk).update(
            status=Jobbstatus.LAGER, startet=timezone.now() - timedelta(seconds=30)
        )
        with mock.patch.object(ki, "generer", return_value=_raatt(5)) as generer:
            kjor_steg(jobb.pk)
        timeout = generer.call_args.kwargs["timeout"]
        self.assertGreater(timeout, 0)
        self.assertLessEqual(timeout, 90)


class SamtidigeKallTest(StubbetGenereringTestCase):
    def test_jobb_i_gang_kjores_ikke_og_gir_gjeldende_fragment_med_forsinkelse(self):
        jobb = self._jobb(status=Jobbstatus.LAGER, i_gang=True)
        with mock.patch.object(ki, "generer") as generer:
            svar = self._steg(jobb)
        generer.assert_not_called()
        jobb.refresh_from_db()
        self.assertEqual(jobb.status, Jobbstatus.LAGER)
        self.assertIs(jobb.i_gang, True)
        html = svar.content.decode()
        self.assertIn("Lager spørsmål (pågår)", html)
        self.assertIn('hx-trigger="load delay:1s"', html)

    def test_uendret_status_bytter_ikke_fremdrift(self):
        jobb = self._jobb(status=Jobbstatus.LAGER, i_gang=True)
        svar = self.client.post(f"/jobber/{jobb.pk}/steg/", {"vist": "lager"})
        html = svar.content.decode()
        self.assertNotIn('id="fremdrift"', html)
        self.assertNotIn("<ol", html)
        self.assertIn(
            f'<div id="spor" hx-post="/jobber/{jobb.pk}/steg/" '
            'hx-trigger="load delay:1s" hx-vals=\'{"vist": "lager"}\'',
            html,
        )

    def test_endret_status_bytter_fremdrift(self):
        jobb = opprett_jobb(self.notat, "middels", 10)
        svar = self.client.post(f"/jobber/{jobb.pk}/steg/", {"vist": "leser"})
        html = svar.content.decode()
        self.assertIn('<div id="fremdrift" hx-swap-oob="innerHTML">', html)
        self.assertIn("Leser filen (ferdig)", html)
        self.assertIn("Lager spørsmål (pågår)", html)
        # Et fullført steg gir ny spørring med en gang, med den nye statusen.
        self.assertIn(
            f'<div id="spor" hx-post="/jobber/{jobb.pk}/steg/" '
            'hx-trigger="load" hx-vals=\'{"vist": "lager"}\'',
            html,
        )

    def test_to_samtidige_kall_gir_ett_ki_kall_og_en_quiz(self):
        jobb = opprett_jobb(self.notat, "middels", 10)
        kjor_steg(jobb.pk)  # leser
        andre_kall = []

        def generer(*args, **kwargs):
            # Det andre kallet kommer mens det første holder på.
            andre_kall.append(kjor_steg(jobb.pk))
            return _raatt(10)

        with mock.patch.object(ki, "generer", side_effect=generer) as stubb:
            self.assertIs(kjor_steg(jobb.pk), True)
            jobb = self._kjor_alle(jobb)
        self.assertEqual(andre_kall, [False])
        self.assertEqual(stubb.call_count, 1)
        self.assertEqual(jobb.status, Jobbstatus.FERDIG)
        self.assertEqual(Quiz.objects.count(), 1)


class GammelJobbTest(GenereringTestCase):
    def test_aktiv_jobb_eldre_enn_120_s_blir_feilet_timeout(self):
        jobb = self._jobb(
            status=Jobbstatus.LAGER, startet=timezone.now() - timedelta(seconds=121)
        )
        with self.assertLogs("studier.services.generering", "WARNING"):
            self.assertIsNone(aktiv_jobb(self.notat))
        jobb.refresh_from_db()
        self.assertEqual(jobb.status, Jobbstatus.FEILET)
        self.assertEqual(jobb.feilkode, "timeout")

    def test_jobb_innenfor_fristen_er_aktiv(self):
        jobb = self._jobb(startet=timezone.now() - timedelta(seconds=100))
        self.assertEqual(aktiv_jobb(self.notat), jobb)

    def test_steg_pa_gammel_jobb_gir_feil_uten_ki_kall(self):
        jobb = self._jobb(
            status=Jobbstatus.LAGER, startet=timezone.now() - timedelta(seconds=121)
        )
        with (
            mock.patch.object(ki, "generer") as generer,
            self.assertLogs("studier.services.generering", "WARNING"),
        ):
            html = self._steg(jobb).content.decode()
        generer.assert_not_called()
        self.assertIn(feilmeldinger.GENERERING_FEIL["timeout"], html)


class AnnensJobbTest(GenereringTestCase):
    def test_annens_jobb_gir_404_og_ingenting_endres(self):
        annen = _innlogget(lag_bruker("annen@eks.no"))
        annens_emne = Emne.objects.create(eier=annen, navn="Annet")
        annens_notat = last_opp(
            annens_emne, SimpleUploadedFile("hemmelig.txt", b"Hemmelig."), annen
        )
        jobb = opprett_jobb(annens_notat, "middels", 10)
        with mock.patch.object(ki, "les_fil") as les_fil:
            svar_s8 = self.client.get(f"/jobber/{jobb.pk}/")
            svar_steg = self._steg(jobb)
            svar_s7 = self.client.post(
                f"/notater/{annens_notat.pk}/",
                {"vanskelighetsgrad": "lett", "antall": "5"},
            )
        self.assertEqual(svar_s8.status_code, 404)
        self.assertEqual(svar_steg.status_code, 404)
        self.assertEqual(svar_s7.status_code, 404)
        les_fil.assert_not_called()
        jobb.refresh_from_db()
        self.assertEqual(jobb.status, Jobbstatus.LESER)
        self.assertIs(jobb.i_gang, False)
        self.assertEqual(Genereringsjobb.objects.count(), 1)

    def test_steg_tar_bare_post(self):
        jobb = opprett_jobb(self.notat, "middels", 10)
        self.assertEqual(self.client.get(f"/jobber/{jobb.pk}/steg/").status_code, 405)


class GenererSynkrontTest(StubbetGenereringTestCase):
    def test_gir_quiz(self):
        with mock.patch.object(ki, "generer", return_value=_raatt(12)):
            quiz = generer_synkront(self.notat, "lett", 12)
        self.assertIsInstance(quiz, Quiz)
        self.assertEqual(quiz.jobb.status, Jobbstatus.FERDIG)
        self.assertEqual(quiz.sporsmal.count(), 12)
        self.assertEqual(Alternativ.objects.filter(sporsmal__quiz=quiz).count(), 36)

    def test_hever_kifeil_med_koden_nar_jobben_feiler(self):
        with (
            mock.patch.object(ki, "generer", return_value=UGYLDIG),
            self.assertLogs("studier.services.generering", "WARNING"),
            self.assertRaises(ki.KIFeil) as feil,
        ):
            generer_synkront(self.notat, "lett", 5)
        self.assertEqual(feil.exception.kode, "format")
        self.assertFalse(Quiz.objects.exists())

    def test_hoyst_fem_steg(self):
        with (
            mock.patch.object(generering, "kjor_steg") as steg,
            self.assertRaises(ki.KIFeil),
        ):
            generer_synkront(self.notat, "lett", 5)
        self.assertEqual(steg.call_count, generering.MAKS_STEG)


class SiderTest(GenereringTestCase):
    def test_s7_uten_quiz_har_skjemaet_overst_med_middels_og_10(self):
        html = self.client.get(self.notat_url).content.decode()
        self.assertIn("Lag en quiz for å komme i gang", html)
        self.assertNotIn('<h2 class="mb-3 text-lg font-semibold">Quizer</h2>', html)
        self.assertIn(
            '<legend class="mb-1 font-semibold">Vanskelighetsgrad</legend>', html
        )
        for verdi in ("lett", "middels", "vanskelig"):
            self.assertIn(f'value="{verdi}"', html)
        self.assertIn('value="middels" checked', html)
        self.assertNotIn('value="lett" checked', html)
        self.assertRegex(
            html,
            r'<input id="id_antall" name="antall" type="number" min="5" max="30"'
            r'[^>]*aria-describedby="hjelp-antall"[^>]*value="10">',
        )
        self.assertIn(
            '<p id="hjelp-antall" class="mt-2 text-sm text-ink-secondary">Fra 5 til 30.</p>',
            html,
        )
        self.assertIn(">Lag quiz</button>", html)
        self.assertLess(
            html.index("Lag en quiz for å komme i gang"),
            html.index(f'<form method="post" action="{self.notat_url}"'),
        )

    def test_s7_med_quiz_viser_kortene_nyeste_forst_over_skjemaet(self):
        with mock.patch.object(ki, "generer", return_value=_raatt(10)):
            eldste = generer_synkront(self.notat, "middels", 10)
        with mock.patch.object(ki, "generer", return_value=_raatt(5)):
            nyeste = generer_synkront(self.notat, "lett", 5)
        Quiz.objects.filter(pk=eldste.pk).update(
            opprettet=timezone.now() - timedelta(days=1)
        )
        html = self.client.get(self.notat_url).content.decode()
        self.assertNotIn("Lag en quiz for å komme i gang", html)
        self.assertEqual(html.count("Laget av KI"), 2)
        self.assertLess(
            html.index("Lett, 5 spørsmål"), html.index("Middels, 10 spørsmål")
        )
        self.assertLess(
            html.index("Middels, 10 spørsmål"),
            html.index(f'<form method="post" action="{self.notat_url}"'),
        )
        self.assertIn(timezone.localtime(nyeste.opprettet).strftime("%Y"), html)
        self.assertNotIn("/quizer/", html)
        self.assertNotIn("Testmodus: denne quizen", html)

    def test_s7_med_aktiv_jobb_lenker_til_s8(self):
        jobb = opprett_jobb(self.notat, "middels", 10)
        html = self.client.get(self.notat_url).content.decode()
        self.assertIn("En quiz lages nå.", html)
        self.assertIn(f'href="/jobber/{jobb.pk}/"', html)

    def test_s8_har_steg_live_region_last_knapp_og_htmx(self):
        jobb = opprett_jobb(self.notat, "middels", 10)
        svar = self.client.get(f"/jobber/{jobb.pk}/")
        self.assertEqual(svar.status_code, 200)
        html = svar.content.decode()
        self.assertIn('<h1 class="mb-4 text-2xl font-semibold">Lager quiz</h1>', html)
        self.assertIn(
            f'<a href="/emner/{self.emne.pk}/" class="underline">Webutvikling</a>', html
        )
        self.assertIn(
            f'<a href="{self.notat_url}" class="underline">notat.txt</a>', html
        )
        self.assertIn('<span aria-current="page">Lager quiz</span>', html)
        self.assertIn('aria-label="Tilbake til notat.txt"', html)
        self.assertIn('<div id="fremdrift" aria-live="polite"', html)
        self.assertRegex(html, r"<ol[^>]*>")
        self.assertIn(
            '<span aria-hidden="true" class="font-bold">…</span><span>Leser filen (pågår)</span>',
            html,
        )
        self.assertIn("Lager spørsmål (venter)", html)
        self.assertIn("Sjekker quizen (venter)", html)
        self.assertIn(
            "Dette kan ta opptil to minutter. Hold fanen åpen til quizen er klar.", html
        )
        self.assertRegex(
            html, r'<button type="button" aria-disabled="true"[^>]*>Lag quiz</button>'
        )
        self.assertIn("<noscript>", html)
        self.assertIn('<script src="/static/js/htmx.min.js" defer></script>', html)
        self.assertIn('<script src="/static/js/meny.js" defer></script>', html)
        self.assertIn(f'hx-post="/jobber/{jobb.pk}/steg/" hx-trigger="load"', html)

    def test_body_sender_csrf_tokenet_med_htmx(self):
        html = self.client.get(self.notat_url).content.decode()
        self.assertRegex(
            html, r"<body [^>]*hx-headers='\{\"X-CSRFToken\": \"[^\"]+\"\}'>"
        )

    def test_steg_virker_med_csrf_header(self):
        jobb = opprett_jobb(self.notat, "middels", 10)
        klient = self.client_class(enforce_csrf_checks=True)
        klient.force_login(self.bruker)
        html = klient.get(f"/jobber/{jobb.pk}/").content.decode()
        token = re.search(r'"X-CSRFToken": "([^"]+)"', html).group(1)
        uten = klient.post(f"/jobber/{jobb.pk}/steg/")
        self.assertEqual(uten.status_code, 403)
        med = klient.post(f"/jobber/{jobb.pk}/steg/", headers={"X-CSRFToken": token})
        self.assertEqual(med.status_code, 200)


class IngenTransaksjonUnderKIKallTest(TransactionTestCase):
    """AD-19: ingen `ki`-kall mens en transaksjon er åpen. Trenger ekte commits."""

    def setUp(self):
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        innstillinger = override_settings(MEDIA_ROOT=media)
        innstillinger.enable()
        self.addCleanup(innstillinger.disable)
        self.media = Path(media)
        self.bruker = _innlogget(lag_bruker())
        emne = Emne.objects.create(eier=self.bruker, navn="Webutvikling")
        self.notat = last_opp(
            emne, SimpleUploadedFile("notat.txt", FILINNHOLD.encode()), self.bruker
        )

    def test_les_fil_generer_og_sjekk_kalles_utenfor_transaksjon(self):
        kall = []

        def vakt(navn, original):
            def kontrollert(*args, **kwargs):
                kall.append((navn, connection.in_atomic_block))
                return original(*args, **kwargs)

            return kontrollert

        utkast = [UGYLDIG, _raatt(5)]
        with (
            mock.patch.object(ki, "les_fil", side_effect=vakt("les_fil", ki.les_fil)),
            mock.patch.object(
                ki,
                "generer",
                side_effect=vakt("generer", lambda *a, **k: utkast.pop(0)),
            ),
            mock.patch.object(ki, "sjekk", side_effect=vakt("sjekk", ki.sjekk)),
        ):
            quiz = generer_synkront(self.notat, "middels", 5)
        self.assertEqual(quiz.sporsmal.count(), 5)
        self.assertEqual(
            [navn for navn, _ in kall],
            ["les_fil", "les_fil", "generer", "sjekk", "les_fil", "generer", "sjekk"],
        )
        self.assertEqual([i_transaksjon for _, i_transaksjon in kall], [False] * 7)
