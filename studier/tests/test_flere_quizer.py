"""Tester for flere quizer per notat (FR-11, FR-16, FR-27, UX-DR26), én per rad i I/O-matrisen i spec 2.6."""

import re
from datetime import timedelta
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.defaultfilters import date as datofilter
from django.test import override_settings
from django.utils import timezone, translation

import ki
from farequiz import feilmeldinger
from studier.models import Emne, Genereringsjobb, Jobbstatus, Quiz
from studier.services.generering import generer_synkront, kjor_steg
from studier.services.notater import last_opp
from studier.tests.fabrikk import lag_bruker
from studier.tests.test_generering import GenereringTestCase, _quiz_json
from studier.tests.test_slett_emne import _innlogget

KORT = re.compile(r'<li class="rounded-lg[^"]*">(.*?)</li>', re.DOTALL)


def _svar(antall=10, modell="claude-sonnet-5-5", forhandslagret=False):
    return ki.RaattSvar(
        tekst=_quiz_json(antall, modell=modell, forhandslagret=forhandslagret),
        forhandslagret=forhandslagret,
        modell=modell,
        prompt_versjon="7",
    )


class FlereQuizerTestCase(GenereringTestCase):
    def _quiz(self, nivaa="middels", antall=10, dager_siden=0, **svar):
        with mock.patch.object(ki, "generer", return_value=_svar(antall, **svar)):
            quiz = generer_synkront(self.notat, nivaa, antall)
        if dager_siden:
            Quiz.objects.filter(pk=quiz.pk).update(
                opprettet=timezone.now() - timedelta(days=dager_siden)
            )
            quiz.refresh_from_db()
        return quiz

    def _html(self):
        svar = self.client.get(self.notat_url)
        self.assertEqual(svar.status_code, 200)
        return svar.content.decode()

    def _kort(self, html):
        return KORT.findall(html)

    def _skjema(self, html):
        return html.index(f'<form method="post" action="{self.notat_url}"')


class FlereQuizerTest(FlereQuizerTestCase):
    def test_tre_quizer_gir_tre_kort_nyeste_forst_over_skjemaet(self):
        eldst = self._quiz("lett", 5, dager_siden=2)
        midt = self._quiz("vanskelig", 20, dager_siden=1)
        nyest = self._quiz("middels", 10)
        html = self._html()
        kort = self._kort(html)
        self.assertEqual(len(kort), 3)
        forventet = [
            (nyest, "Middels, 10 spørsmål"),
            (midt, "Vanskelig, 20 spørsmål"),
            (eldst, "Lett, 5 spørsmål"),
        ]
        with translation.override("nb"):
            for innhold, (quiz, tittel) in zip(kort, forventet, strict=True):
                with self.subTest(tittel=tittel):
                    dato = datofilter(timezone.localtime(quiz.opprettet), "j. F Y")
                    self.assertIn(tittel, innhold)
                    self.assertIn("Laget av KI", innhold)
                    self.assertIn(f"{dato} · Claude Sonnet 5.5", innhold)
        self.assertLess(html.index("Lett, 5 spørsmål"), html.index("Lag ny quiz"))
        self.assertLess(html.index("Lag ny quiz"), self._skjema(html))
        self.assertNotIn("Lag en quiz for å komme i gang", html)

    @override_settings(KI_MODELL="claude-sonnet-5-5")
    def test_modellnavnet_kommer_fra_quizen_ikke_fra_innstillingen(self):
        self._quiz(modell="claude-haiku-5-5")
        (kort,) = self._kort(self._html())
        self.assertIn("Claude Haiku 5.5", kort)
        self.assertNotIn("Sonnet", kort)

    def test_samme_valg_igjen_gir_eget_kort_og_forste_quiz_er_uendret(self):
        forste = self._quiz("middels", 10, dager_siden=1)
        for_ = {
            "opprettet": forste.opprettet,
            "jobb": forste.jobb_id,
            "sporsmal": list(forste.sporsmal.values_list("pk", "tekst")),
        }
        svar = self.client.post(
            self.notat_url, {"vanskelighetsgrad": "middels", "antall": "10"}
        )
        jobb = Genereringsjobb.objects.exclude(pk=forste.jobb_id).get()
        self.assertRedirects(svar, f"/jobber/{jobb.pk}/")
        with mock.patch.object(ki, "generer", return_value=_svar(10)):
            for _ in range(5):
                kjor_steg(jobb.pk)
                jobb.refresh_from_db()
                if jobb.status == Jobbstatus.FERDIG:
                    break
        self.assertEqual(jobb.status, Jobbstatus.FERDIG)

        self.assertEqual(Quiz.objects.count(), 2)
        forste.refresh_from_db()
        self.assertEqual(forste.opprettet, for_["opprettet"])
        self.assertEqual(forste.jobb_id, for_["jobb"])
        self.assertEqual(
            list(forste.sporsmal.values_list("pk", "tekst")), for_["sporsmal"]
        )
        kort = self._kort(self._html())
        self.assertEqual(len(kort), 2)
        for innhold in kort:
            self.assertIn("Middels, 10 spørsmål", innhold)

    def test_merknaden_star_bare_pa_det_forhandslagrede_kortet(self):
        self._quiz("lett", 5, dager_siden=1, forhandslagret=False)
        self._quiz("middels", 10, forhandslagret=True)
        html = self._html()
        nyest, eldst = self._kort(html)
        merknad = feilmeldinger.TESTMODUS_FORHANDSLAGRET
        self.assertIn(merknad, nyest)
        self.assertNotIn(merknad, eldst)
        self.assertEqual(html.count(merknad), 1)
        # Som tekst under datoen, ikke bare som ikon.
        self.assertRegex(
            nyest, r"· Claude Sonnet 5\.5</p>\s*<p[^>]*>" + re.escape(merknad) + "</p>"
        )
        # «Lag ny quiz» står under begge kortene.
        self.assertLess(html.index("Lett, 5 spørsmål"), html.index("Lag ny quiz"))
        self.assertLess(html.index("Middels, 10 spørsmål"), html.index("Lag ny quiz"))

    def test_merknaden_folger_quizen_ogsa_nar_testmodus_er_av(self):
        self._quiz(forhandslagret=True)
        with mock.patch("farequiz.context_processors.er_testmodus", return_value=False):
            html = self._html()
        self.assertNotIn("Testmodus: quizene bruker mock-svar", html)
        self.assertIn(feilmeldinger.TESTMODUS_FORHANDSLAGRET, html)

    def test_ingen_merknad_uten_forhandslagret(self):
        self._quiz(forhandslagret=False)
        html = self._html()
        self.assertNotIn(feilmeldinger.TESTMODUS_FORHANDSLAGRET, html)
        # Banneret for testmodus står i sidemalen, men ingen merknad på kortet.
        (kort,) = self._kort(html)
        self.assertNotIn("Testmodus", kort)

    def test_ingen_sletting_av_en_enkelt_quiz(self):
        quiz = self._quiz()
        html = self._html()
        self.assertNotIn("Slett", html)
        self.assertNotIn("slett", html)
        # Skjemaene i innholdet er «Ta quiz» (story 3.1) og «Lag ny quiz».
        innhold = re.search(r"<main .*?</main>", html, re.DOTALL).group()
        self.assertEqual(
            re.findall(r'<form[^>]*action="([^"]*)"', innhold),
            [f"/quizer/{quiz.pk}/start/", self.notat_url],
        )
        for metode in (self.client.get, self.client.post):
            with self.subTest(metode=metode.__name__):
                svar = metode(f"/quizer/{quiz.pk}/slett/")
                self.assertEqual(svar.status_code, 404)
        self.assertTrue(Quiz.objects.filter(pk=quiz.pk).exists())

    def test_brodsmulene_viser_oversikt_emne_notat(self):
        html = self._html()
        nav = re.search(
            r'<nav aria-label="Brødsmuler".*?</nav>', html, re.DOTALL
        ).group()
        steg = re.findall(r"<li>(.*?)</li>", nav, re.DOTALL)
        self.assertEqual(len(steg), 3)
        self.assertIn('<a href="/" class="underline">Oversikt</a>', steg[0])
        self.assertIn(
            f'<a href="/emner/{self.emne.pk}/" class="underline">Webutvikling</a>',
            steg[1],
        )
        self.assertIn(
            f'<span aria-current="page">{self.notat.originalnavn}</span>', steg[2]
        )


class AnnensNotatTest(GenereringTestCase):
    def test_annens_notat_gir_404_ved_get_og_post_og_ingen_jobb(self):
        annen = _innlogget(lag_bruker("annen@eks.no"))
        annens_emne = Emne.objects.create(eier=annen, navn="Annet")
        annens_notat = last_opp(
            annens_emne, SimpleUploadedFile("hemmelig.txt", b"Hemmelig."), annen
        )
        url = f"/notater/{annens_notat.pk}/"
        svar_get = self.client.get(url)
        svar_post = self.client.post(
            url, {"vanskelighetsgrad": "middels", "antall": "10"}
        )
        for svar in (svar_get, svar_post):
            self.assertContains(svar, "Fant ikke siden", status_code=404)
            self.assertNotContains(svar, "hemmelig.txt", status_code=404)
        self.assertFalse(Genereringsjobb.objects.exists())
