"""Tester for å melde et spørsmål som feil (FR-31), én per rad i I/O-matrisen i spec 4.3."""

import re
from pathlib import Path

from django.conf import settings
from django.test import TestCase

from studier.models import (
    Feilbankrad,
    Hendelse,
    Okt,
    Okttype,
    Sporsmal,
    Svar,
    Vanskelighetsgrad,
)
from studier.services.okter import lagre_svar, lever_okt, start_eller_fortsett_okt
from studier.services.sporsmal import meld_sporsmal
from studier.tests.test_dekningsgrad import DekningTestCase, _nivaa_html
from studier.tests.test_oving import OvingTestCase


class MeldeTestCase(OvingTestCase):
    def _besvar(self, okt, feil=()):
        """Svarer på alle spørsmålene i økten, feil på numrene i `feil`, ellers riktig."""
        for nr, rad in enumerate(okt.innhold, start=1):
            s = Sporsmal.objects.get(pk=rad["sporsmal"])
            lagre_svar(okt, s, s.alternativer.filter(er_riktig=nr not in feil).first())

    def _levert(self, quiz=None, feil=(2,)):
        okt = self._okt(quiz)
        self._besvar(okt, feil)
        lever_okt(okt)
        return okt

    def _sporsmal(self, okt, nr):
        return Sporsmal.objects.get(pk=okt.innhold[nr - 1]["sporsmal"])

    def _meld_url(self, okt, nr):
        return f"/okter/{okt.pk}/meld/{nr}/"

    def _resultat_url(self, okt):
        return f"/okter/{okt.pk}/resultat/"

    def _resultat(self, okt):
        svar = self.client.get(self._resultat_url(okt))
        self.assertEqual(svar.status_code, 200)
        return svar.content.decode()


class MatriseTest(MeldeTestCase):
    def test_melde(self):
        okt = self._levert(feil=(2, 3))
        s2 = self._sporsmal(okt, 2)
        html = self._resultat(okt)
        self.assertIn("Øv på feil (2)", html)
        self.assertIn(f'href="{self._meld_url(okt, 2)}"', html)

        self.assertEqual(self.client.get(self._meld_url(okt, 2)).status_code, 200)
        self.assertIsNone(Sporsmal.objects.get(pk=s2.pk).meldt_tidspunkt)
        svar = self.client.post(self._meld_url(okt, 2))
        self.assertRedirects(svar, self._resultat_url(okt))
        self.assertIsNotNone(Sporsmal.objects.get(pk=s2.pk).meldt_tidspunkt)

        html = self._resultat(okt)
        self.assertEqual(html.count("Meldt som feil"), 1)
        rad2 = re.search(
            r"<li[^>]*>(?:(?!</li>).)*2\. Spørsmål 2\?.*?</li>", html, re.DOTALL
        )
        self.assertIn("Meldt som feil", rad2.group())
        self.assertNotIn(f'href="{self._meld_url(okt, 2)}"', html)
        self.assertIn(f'href="{self._meld_url(okt, 3)}"', html)
        self.assertIn("Øv på feil (1)", html)
        # Feilbankraden slettes aldri (AD-3).
        self.assertTrue(Feilbankrad.objects.filter(sporsmal=s2).exists())

    def test_allerede_meldt(self):
        okt = self._levert()
        self.client.post(self._meld_url(okt, 2))
        tidspunkt = self._sporsmal(okt, 2).meldt_tidspunkt
        svar = self.client.post(self._meld_url(okt, 2))
        self.assertRedirects(svar, self._resultat_url(okt))
        self.assertEqual(self._sporsmal(okt, 2).meldt_tidspunkt, tidspunkt)
        svar = self.client.get(self._meld_url(okt, 2))
        self.assertRedirects(svar, self._resultat_url(okt))

    def test_riktig_rad(self):
        okt = self._levert()
        self.assertEqual(self.client.get(self._meld_url(okt, 1)).status_code, 404)
        self.assertEqual(self.client.post(self._meld_url(okt, 1)).status_code, 404)
        self.assertFalse(
            Sporsmal.objects.filter(meldt_tidspunkt__isnull=False).exists()
        )
        self.assertNotIn(f'href="{self._meld_url(okt, 1)}"', self._resultat(okt))

    def test_pabegynt_okt(self):
        okt = self._okt()
        self._besvar(okt, feil=(2,))
        self.assertEqual(self.client.get(self._meld_url(okt, 2)).status_code, 404)
        self.assertEqual(self.client.post(self._meld_url(okt, 2)).status_code, 404)
        self.assertFalse(
            Sporsmal.objects.filter(meldt_tidspunkt__isnull=False).exists()
        )

    def test_ugyldig_nr(self):
        okt = self._levert()
        for nr in (0, 6):
            with self.subTest(nr=nr):
                self.assertEqual(
                    self.client.get(self._meld_url(okt, nr)).status_code, 404
                )
                self.assertEqual(
                    self.client.post(self._meld_url(okt, nr)).status_code, 404
                )
        self.assertFalse(
            Sporsmal.objects.filter(meldt_tidspunkt__isnull=False).exists()
        )

    def test_andres_okt(self):
        _annen, annens_quiz = self._annen_bruker()
        annens = start_eller_fortsett_okt(annens_quiz)
        for rad in annens.innhold:
            s = Sporsmal.objects.get(pk=rad["sporsmal"])
            lagre_svar(annens, s, s.alternativer.filter(er_riktig=False).first())
        lever_okt(annens)
        self.assertEqual(self.client.get(self._meld_url(annens, 1)).status_code, 404)
        self.assertEqual(self.client.post(self._meld_url(annens, 1)).status_code, 404)
        self.assertFalse(
            Sporsmal.objects.filter(meldt_tidspunkt__isnull=False).exists()
        )

    def test_ny_oving(self):
        aapne = self._rader(3, 0)
        meld_sporsmal(aapne[0])
        self.assertIn(
            "Øv på feil (2)", self.client.get(self.notat_url).content.decode()
        )
        _, okt = self._start()
        self.assertEqual(
            [r["sporsmal"] for r in okt.innhold], [s.pk for s in aapne[1:]]
        )

    def test_nytt_forsok(self):
        forste = self.quiz.sporsmal.order_by("id").first()
        meld_sporsmal(forste)
        okt = self._okt()
        self.assertEqual(len(okt.innhold), 4)
        self.assertNotIn(forste.pk, [r["sporsmal"] for r in okt.innhold])

    def test_alle_meldt(self):
        for s in self.quiz.sporsmal.all():
            meld_sporsmal(s)
        html = self.client.get(self.notat_url).content.decode()
        tekst = f'<p id="meldt-{self.quiz.pk}" class="mb-2 text-sm text-ink-secondary">Alle spørsmålene er meldt som feil</p>'
        self.assertIn(tekst, html)
        skjema = re.search(
            rf'<form method="post" action="/quizer/{self.quiz.pk}/start/".*?</form>',
            html,
            re.DOTALL,
        ).group()
        self.assertIn('aria-disabled="true"', skjema)
        self.assertIn(
            f'aria-describedby="quiz-{self.quiz.pk} meldt-{self.quiz.pk}"', skjema
        )
        # Den andre quizen er ikke låst.
        andre = re.search(
            rf'<form method="post" action="/quizer/{self.quiz2.pk}/start/".*?</form>',
            html,
            re.DOTALL,
        ).group()
        self.assertNotIn("aria-disabled", andre)

        svar = self.client.post(f"/quizer/{self.quiz.pk}/start/")
        self.assertRedirects(svar, self.notat_url)
        self.assertFalse(Okt.objects.exists())
        self.assertIsNone(start_eller_fortsett_okt(self.quiz))

    def test_alle_meldt_med_pabegynt(self):
        okt = self._okt()
        self._besvar(okt, feil=())
        Svar.objects.filter(okt=okt).exclude(
            sporsmal_id=okt.innhold[0]["sporsmal"]
        ).delete()
        for s in self.quiz.sporsmal.all():
            meld_sporsmal(s)
        html = self.client.get(self.notat_url).content.decode()
        skjema = re.search(
            rf'<form method="post" action="/quizer/{self.quiz.pk}/start/".*?</form>',
            html,
            re.DOTALL,
        ).group()
        self.assertIn(">Fortsett<", skjema)
        self.assertIn(
            f'aria-describedby="quiz-{self.quiz.pk} fremdrift-{self.quiz.pk}"', skjema
        )
        self.assertNotIn("aria-disabled", skjema)
        self.assertNotIn("Alle spørsmålene er meldt som feil", html)
        svar = self.client.post(f"/quizer/{self.quiz.pk}/start/")
        self.assertRedirects(svar, self._url(okt, 2), fetch_redirect_response=False)
        self.assertEqual(Okt.objects.count(), 1)

    def test_pabegynt_med_meldt(self):
        okt = self._okt()
        s1 = self._sporsmal(okt, 1)
        Feilbankrad.objects.create(sporsmal=s1, riktige_pa_rad=1)
        self._besvar(okt, feil=(1,))
        meld_sporsmal(s1)
        # Spørsmålet vises fortsatt i den påbegynte økten (AD-16).
        side = self.client.get(self._url(okt, 1)).content.decode()
        self.assertIn(s1.tekst, side)
        svar = self.client.post(f"/okter/{okt.pk}/lever/")
        self.assertRedirects(svar, self._resultat_url(okt))
        okt.refresh_from_db()
        self.assertEqual(okt.poengsum, 4)
        self.assertEqual(okt.antall, 5)
        self.assertEqual(
            Svar.objects.get(okt=okt, sporsmal=s1).hendelse, Hendelse.INGEN
        )
        rad = Feilbankrad.objects.get(sporsmal=s1)
        self.assertEqual(rad.riktige_pa_rad, 1)
        self.assertIsNone(rad.laert_tidspunkt)


class DekningMeldtTest(DekningTestCase):
    def test_dekningsgrad(self):
        quiz = self._quiz(Vanskelighetsgrad.MIDDELS, 3)
        forste = quiz.sporsmal.order_by("id").first()
        # Bare de to siste er besvart riktig. Det første har en åpen feilbankrad.
        okt = self._forsok(quiz, riktige=3)
        Svar.objects.filter(okt=okt, sporsmal=forste).delete()
        Feilbankrad.objects.create(sporsmal=forste)
        self.assertAlmostEqual(self._dekning().nivaer[Vanskelighetsgrad.MIDDELS], 2 / 3)
        meld_sporsmal(forste)
        dekning = self._dekning()
        self.assertEqual(dekning.nivaer[Vanskelighetsgrad.MIDDELS], 1.0)
        self.assertEqual(dekning.total, 0.3)
        self.assertEqual(_nivaa_html(self._s7(), "Middels"), "100 %")

    def test_niva_alle_meldt(self):
        lett = self._quiz(Vanskelighetsgrad.LETT, 2)
        self._forsok(lett, riktige=2)
        self._forsok(self._quiz(Vanskelighetsgrad.VANSKELIG, 2), riktige=2)
        for s in lett.sporsmal.all():
            meld_sporsmal(s)
        dekning = self._dekning()
        self.assertIsNone(dekning.nivaer[Vanskelighetsgrad.LETT])
        self.assertEqual(dekning.total, 0.5)
        self.assertEqual(_nivaa_html(self._s7(), "Lett"), "Ingen quiz")


class SideTest(MeldeTestCase):
    def test_fasit_vises_ikke_etter_melding(self):
        okt = self._levert()
        self.client.post(self._meld_url(okt, 2))
        html = self._resultat(okt)
        s2 = self._sporsmal(okt, 2)
        self.assertNotIn(s2.alternativer.get(er_riktig=True).tekst, html)
        self.assertNotIn(s2.begrunnelse, html)
        self.assertNotIn("Riktig svar", html)
        self.assertNotIn("Begrunnelse", html)

    def test_lenken_beskrives_av_sporsmalet(self):
        okt = self._levert()
        html = self._resultat(okt)
        self.assertIn('id="sporsmal-2">2. Spørsmål 2?</strong>', html)
        self.assertIn(
            f'<a href="{self._meld_url(okt, 2)}" aria-describedby="sporsmal-2"', html
        )
        self.assertIn(">Meld som feil eller uklart</a>", html)
        self.assertEqual(html.count("Meld som feil eller uklart"), 1)

    def test_bekreftelsessiden(self):
        okt = self._levert()
        svar = self.client.get(self._meld_url(okt, 2))
        self.assertEqual(svar.status_code, 200)
        html = svar.content.decode()
        self.assertIn(
            f"<title>Meld som feil – {self.notat.originalnavn} – FåreQuiz</title>", html
        )
        self.assertIn(">Melde spørsmålet som feil eller uklart?</h1>", html)
        self.assertIn("2. Spørsmål 2?", html)
        self.assertIn(
            "Spørsmålet tas ut av feilbanken og dekningsgraden og kommer ikke med i"
            " nye quizer eller øvinger. Det kan ikke angres.",
            html,
        )
        avbryt = html.index(f'<a href="{self._resultat_url(okt)}"')
        self.assertIn(">Avbryt</a>", html[avbryt : avbryt + 400])
        skjema = html.index(f'<form method="post" action="{self._meld_url(okt, 2)}"')
        knapp = html.index(">Meld som feil</button>")
        self.assertLess(avbryt, skjema)
        self.assertLess(skjema, knapp)
        nav = re.search(
            r'<nav aria-label="Brødsmuler".*?</nav>', html, re.DOTALL
        ).group()
        for tekst in (
            "Oversikt",
            self.emne.navn,
            self.notat.originalnavn,
            "Meld som feil",
        ):
            self.assertIn(tekst, nav)
        self.assertLess(nav.index(self.emne.navn), nav.index(self.notat.originalnavn))
        # Fasiten står ikke på bekreftelsessiden.
        s2 = self._sporsmal(okt, 2)
        self.assertNotIn(s2.alternativer.get(er_riktig=True).tekst, html)
        self.assertNotIn(s2.begrunnelse, html)

    def test_bekreftelsessiden_med_lang(self):
        self.quiz.sprak = "en"
        self.quiz.save()
        okt = self._levert()
        html = self.client.get(self._meld_url(okt, 2)).content.decode()
        self.assertIn('lang="en">2. Spørsmål 2?</p>', html)

    def test_s12_meldt_rad(self):
        self._rader(2, 0)
        _, okt = self._start()
        self._besvar(okt, feil=(1,))
        lever_okt(okt)
        html = self._resultat(okt)
        self.assertEqual(html.count("av 2 riktige på rad"), 2)
        self.assertIn(f'href="{self._meld_url(okt, 1)}"', html)
        svar = self.client.post(self._meld_url(okt, 1))
        self.assertRedirects(svar, self._resultat_url(okt))
        html = self._resultat(okt)
        self.assertIn('<span class="font-semibold">Meldt som feil</span>', html)
        self.assertEqual(html.count("av 2 riktige på rad"), 1)
        self.assertEqual(html.count('class="inline-flex gap-1" aria-hidden="true"'), 1)
        self.assertNotIn("Meld som feil eller uklart", html)

    def test_s7_ov_pa_feil_og_dekning_uten_meldt(self):
        okt = self._levert(feil=(2,))
        html = self.client.get(self.notat_url).content.decode()
        self.assertIn("Øv på feil (1)", html)
        self.client.post(self._meld_url(okt, 2))
        html = self.client.get(self.notat_url).content.decode()
        ov_skjema = re.search(
            rf'<form method="post" action="{self.ov_url}".*?</form>', html, re.DOTALL
        ).group()
        self.assertIn('aria-disabled="true"', ov_skjema)
        self.assertIn("Ingen spørsmål i feilbanken", ov_skjema)
        # Middels: 4 av 9 spørsmål som ikke er meldt, er dekket (quiz2 har ingen svar).
        self.assertEqual(_nivaa_html(html, "Middels"), "44 %")

    def test_ta_bare_get_head_og_post(self):
        okt = self._levert()
        self.assertEqual(self.client.put(self._meld_url(okt, 2)).status_code, 405)
        self.assertEqual(self.client.head(self._meld_url(okt, 2)).status_code, 200)
        self.assertIsNone(self._sporsmal(okt, 2).meldt_tidspunkt)

    def test_laert_for_melding_viser_ikke_fasit(self):
        # Feil i forsøk A, lært i to øvinger, så meldt fra A sin ✕-rad.
        forsok = self._levert(feil=(2,))
        s2 = self._sporsmal(forsok, 2)
        for _ in range(2):
            oving = start_eller_fortsett_okt(notat=self.notat)
            self._besvar(oving)
            lever_okt(oving)
        self.assertIsNotNone(Feilbankrad.objects.get(sporsmal=s2).laert_tidspunkt)
        self.assertEqual(
            Svar.objects.get(okt=oving, sporsmal=s2).hendelse, Hendelse.LAERT
        )
        self.client.post(self._meld_url(forsok, 2))
        riktig = s2.alternativer.get(er_riktig=True).tekst
        for okt in (forsok, oving):
            with self.subTest(okt=okt.type):
                html = self._resultat(okt)
                self.assertIn("Meldt som feil", html)
                self.assertNotIn("Riktig svar", html)
                self.assertNotIn("Begrunnelse", html)
                if okt is forsok:
                    # I øvingen var studentens eget svar det riktige.
                    self.assertNotIn(riktig, html)
                self.assertNotIn(s2.begrunnelse, html)
                self.assertNotIn(">Lært</h2>", html)

    def test_s12_siste_apne_meldt_er_ikke_alt_laert(self):
        self._rader(1, 0)
        _, okt = self._start()
        self._besvar(okt, feil=(1,))
        lever_okt(okt)
        self.client.post(self._meld_url(okt, 1))
        html = self._resultat(okt)
        self.assertIn("Meldt som feil", html)
        self.assertNotIn("Alle spørsmålene er lært", html)

    def test_steg_uten_sporsmal_som_ikke_er_meldt(self):
        for s in self.quiz.sporsmal.all():
            meld_sporsmal(s)
        svar = self.client.post(f"/jobber/{self.quiz.jobb_id}/steg/")
        self.assertEqual(svar.status_code, 200)
        self.assertEqual(svar["HX-Redirect"], self.notat_url)
        self.assertFalse(Okt.objects.exists())

    def test_logger_meldingen(self):
        s = self.quiz.sporsmal.first()
        with self.assertLogs("studier.services.sporsmal", "INFO") as logg:
            self.assertTrue(meld_sporsmal(s))
        self.assertIn(f"Spørsmål {s.pk} i quiz {self.quiz.pk}", logg.output[0])
        self.assertIn(self.quiz.modell, logg.output[0])
        self.assertFalse(meld_sporsmal(Sporsmal.objects.get(pk=s.pk)))
        self.assertIsNotNone(s.meldt_tidspunkt)

    def test_meldt_okt_er_ikke_oving(self):
        # Melding fra S11 lager ingen økt.
        okt = self._levert()
        self.client.post(self._meld_url(okt, 2))
        self.assertEqual(Okt.objects.count(), 1)
        self.assertFalse(Okt.objects.filter(type=Okttype.OVING).exists())


class EnesteStedTest(TestCase):
    """`meldt_tidspunkt` brukes bare i modellen, i `meld_sporsmal`, i vakten i `registrer_svar` og i visningen av raden."""

    APPER = ("studier", "kontoer", "farequiz", "ki", "templates")
    TILLATT = {
        Path("studier/models.py"),
        Path("studier/services/sporsmal.py"),
        Path("studier/services/feilbank.py"),
        Path("studier/views.py"),
    }

    def test_meldt_tidspunkt_bare_der_det_er_lov(self):
        rot = Path(settings.BASE_DIR)
        treff = {}
        for app in self.APPER:
            self.assertTrue((rot / app).is_dir(), f"Fant ikke {app}.")
            for fil in (rot / app).rglob("*"):
                if fil.suffix not in (".py", ".html"):
                    continue
                relativ = fil.relative_to(rot)
                deler = set(relativ.parts)
                if "migrations" in deler or "tests" in deler:
                    continue
                antall = fil.read_text(encoding="utf-8").count("meldt_tidspunkt")
                if antall:
                    treff[relativ] = antall
        self.assertLessEqual(set(treff), self.TILLATT)
        # Vakten i feilbanken og visningen av raden er én linje hver.
        self.assertEqual(treff.get(Path("studier/services/feilbank.py")), 1)
        self.assertEqual(treff.get(Path("studier/views.py")), 1)

    def test_bare_meld_sporsmal_skriver_feltet(self):
        rot = Path(settings.BASE_DIR)
        skriving = re.compile(r"meldt_tidspunkt\s*=(?!=)")
        treff = []
        for app in ("studier", "kontoer", "farequiz", "ki"):
            for fil in (rot / app).rglob("*.py"):
                relativ = fil.relative_to(rot)
                deler = set(relativ.parts)
                if (
                    "migrations" in deler
                    or "tests" in deler
                    or relativ
                    in (Path("studier/models.py"), Path("studier/services/sporsmal.py"))
                ):
                    continue
                for nr, linje in enumerate(
                    fil.read_text(encoding="utf-8").splitlines(), 1
                ):
                    if skriving.search(linje):
                        treff.append(f"{relativ}:{nr}: {linje.strip()}")
        self.assertEqual(treff, [])
