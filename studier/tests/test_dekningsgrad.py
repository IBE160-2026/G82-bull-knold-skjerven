"""Tester for dekningsgraden per notat (FR-24, AD-4, UX-DR23, TF-6), én per rad i I/O-matrisen i spec 5.1."""

import re

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import SimpleTestCase
from django.test.utils import CaptureQueriesContext

from studier.models import (
    Alternativ,
    Feilbankrad,
    Genereringsjobb,
    Okt,
    Oktstatus,
    Okttype,
    Quiz,
    Sporsmal,
    Svar,
    Vanskelighetsgrad,
)
from studier.services import dekningsgrad
from studier.services.notater import last_opp
from studier.services.okter import lagre_svar, lever_okt, start_eller_fortsett_okt
from studier.templatetags.dekning import hel_prosent
from studier.tests.test_generering import GenereringTestCase

LETT, MIDDELS, VANSKELIG = (
    Vanskelighetsgrad.LETT,
    Vanskelighetsgrad.MIDDELS,
    Vanskelighetsgrad.VANSKELIG,
)


def _nivaa_html(html, navn):
    """Teksten i `<dd>` etter `<dt>navn</dt>` på S7."""
    treff = re.search(
        rf"<dt[^>]*>{navn}</dt>\s*<dd[^>]*>(.*?)</dd>", html, flags=re.DOTALL
    )
    return treff.group(1) if treff else None


class DekningTestCase(GenereringTestCase):
    def _quiz(self, nivaa, antall, notat=None):
        """En quiz med `antall` spørsmål, laget direkte (`generer_synkront` krever minst 5)."""
        notat = notat or self.notat
        jobb = Genereringsjobb.objects.create(
            notat=notat, vanskelighetsgrad=nivaa, antall=antall
        )
        quiz = Quiz.objects.create(
            notat=notat,
            jobb=jobb,
            vanskelighetsgrad=nivaa,
            sprak="nb",
            modell="claude-test",
            prompt_versjon="7",
        )
        for nr in range(1, antall + 1):
            sporsmal = Sporsmal.objects.create(
                quiz=quiz, tekst=f"Spørsmål {nr}?", begrunnelse="Fordi."
            )
            Alternativ.objects.create(sporsmal=sporsmal, tekst="Riktig", er_riktig=True)
            Alternativ.objects.create(sporsmal=sporsmal, tekst="Feil")
        return quiz

    def _forsok(self, quiz, riktige, status=Oktstatus.LEVERT):
        """En økt med svar på de første `riktige` spørsmålene, alle riktige. Ingen feilbank."""
        okt = Okt.objects.create(
            notat=quiz.notat, quiz=quiz, type=Okttype.FORSOK, status=status
        )
        for sporsmal in quiz.sporsmal.order_by("id")[:riktige]:
            Svar.objects.create(
                okt=okt,
                sporsmal=sporsmal,
                alternativ=sporsmal.alternativer.get(er_riktig=True),
            )
        return okt

    def _lever(self, okt, riktig):
        """Svarer på alle spørsmålene i økten (riktig eller feil) og leverer med tjenestene."""
        for rad in okt.innhold:
            sporsmal = Sporsmal.objects.get(pk=rad["sporsmal"])
            lagre_svar(okt, sporsmal, sporsmal.alternativer.get(er_riktig=riktig))
        lever_okt(okt)

    def _dekning(self, notat=None):
        return dekningsgrad.for_notat(notat or self.notat)

    def _s7(self):
        return self.client.get(self.notat_url).content.decode()


class MatriseTest(DekningTestCase):
    def test_fr24_eksempel(self):
        self._forsok(self._quiz(LETT, 2), riktige=2)
        self._forsok(self._quiz(MIDDELS, 2), riktige=1)
        dekning = self._dekning()
        self.assertEqual(dekning.total, 0.35)
        self.assertIsInstance(dekning.total, float)
        self.assertEqual(dekning.nivaer, {LETT: 1.0, MIDDELS: 0.5, VANSKELIG: None})
        html = self._s7()
        self.assertIn('<p class="text-2xl font-semibold tabular-nums">35 %</p>', html)
        self.assertEqual(_nivaa_html(html, "Lett"), "100 %")
        self.assertEqual(_nivaa_html(html, "Middels"), "50 %")
        self.assertEqual(_nivaa_html(html, "Vanskelig"), "Ingen quiz")
        self.assertIn("Vanskelige spørsmål teller mest (50 %).", html)
        self.assertIn(
            "Dekningsgraden kan gå ned når du lager en ny quiz, fordi de nye "
            "spørsmålene ikke er besvart ennå. Uten quiz på vanskelig kommer du "
            "ikke over 50 %.",
            html,
        )

    def test_ny_quiz_senker_dekningsgraden(self):
        self._forsok(self._quiz(MIDDELS, 2), riktige=2)
        for_ = self._dekning()
        self.assertEqual(for_.nivaer[MIDDELS], 1.0)
        self._quiz(MIDDELS, 2)
        etter = self._dekning()
        self.assertEqual(etter.nivaer[MIDDELS], 0.5)
        self.assertLess(etter.total, for_.total)

    def test_uten_vanskelig_aldri_over_halvparten(self):
        self._forsok(self._quiz(LETT, 3), riktige=3)
        self._forsok(self._quiz(MIDDELS, 4), riktige=4)
        dekning = self._dekning()
        self.assertEqual(dekning.nivaer[LETT], 1.0)
        self.assertEqual(dekning.nivaer[MIDDELS], 1.0)
        self.assertEqual(dekning.total, 0.5)

    def test_riktig_svar_bare_i_pabegynt_okt_er_ikke_dekket(self):
        self._forsok(self._quiz(LETT, 2), riktige=2, status=Oktstatus.PABEGYNT)
        dekning = self._dekning()
        self.assertEqual(dekning.nivaer[LETT], 0.0)
        self.assertEqual(dekning.total, 0.0)

    def test_apen_feilbankrad_er_ikke_dekket(self):
        quiz = self._quiz(LETT, 2)
        self._forsok(quiz, riktige=2)
        Feilbankrad.objects.create(sporsmal=quiz.sporsmal.order_by("id").first())
        self.assertEqual(self._dekning().nivaer[LETT], 0.5)

    def test_lagt_i_feilbanken_etterpa_er_ikke_dekket_lenger(self):
        quiz = self._quiz(MIDDELS, 2)
        self._lever(start_eller_fortsett_okt(quiz), riktig=True)
        self.assertEqual(self._dekning().nivaer[MIDDELS], 1.0)
        self._lever(start_eller_fortsett_okt(quiz), riktig=False)
        self.assertEqual(Feilbankrad.objects.filter(laert_tidspunkt=None).count(), 2)
        self.assertEqual(self._dekning().nivaer[MIDDELS], 0.0)

    def test_laert_i_oving_er_dekket(self):
        quiz = self._quiz(MIDDELS, 2)
        self._lever(start_eller_fortsett_okt(quiz), riktig=False)
        # Det trengs to riktige på rad for å bli lært, så to leverte øvinger.
        self._lever(start_eller_fortsett_okt(notat=self.notat), riktig=True)
        self.assertEqual(self._dekning().nivaer[MIDDELS], 0.0)
        self._lever(start_eller_fortsett_okt(notat=self.notat), riktig=True)
        self.assertFalse(Feilbankrad.objects.filter(laert_tidspunkt=None).exists())
        self.assertEqual(self._dekning().nivaer[MIDDELS], 1.0)

    def test_notat_uten_quiz(self):
        dekning = self._dekning()
        self.assertEqual(dekning.total, 0.0)
        self.assertIsInstance(dekning.total, float)
        self.assertEqual(dekning.nivaer, {LETT: None, MIDDELS: None, VANSKELIG: None})
        html = self._s7()
        self.assertIn('<p class="text-2xl font-semibold tabular-nums">0 %</p>', html)
        for navn in ("Lett", "Middels", "Vanskelig"):
            self.assertEqual(_nivaa_html(html, navn), "Ingen quiz")

    def test_andre_notater_pavirker_ikke(self):
        self._quiz(LETT, 2)
        annet = last_opp(
            self.emne,
            SimpleUploadedFile("annet.txt", b"Annet notat."),
            self.bruker,
        )
        self._forsok(self._quiz(LETT, 2, notat=annet), riktige=2)
        self.assertEqual(self._dekning(annet).nivaer[LETT], 1.0)
        dekning = self._dekning()
        self.assertEqual(dekning.nivaer[LETT], 0.0)
        self.assertEqual(dekning.total, 0.0)

    def test_avrunding_pa_s7_ogsa_for_nivaene(self):
        # Lett 1 av 3: totalen 0,0667 gir 7 %, og nivået 0,333 gir 33 %.
        self._forsok(self._quiz(LETT, 3), riktige=1)
        html = self._s7()
        self.assertIn('<p class="text-2xl font-semibold tabular-nums">7 %</p>', html)
        self.assertIn('<span style="width: 7%"></span>', html)
        self.assertIn('style="left: 7%"', html)
        self.assertEqual(_nivaa_html(html, "Lett"), "33 %")


class HelProsentTest(SimpleTestCase):
    def test_avrundingsraden(self):
        for verdi, ventet in [
            (1 / 3, 33),
            (1 / 8, 13),
            (0.9967, 99),
            (0.004, 1),
            (1, 100),
            (1.0, 100),
            (0, 0),
            (0.0, 0),
            # Grensene rundt 100 og 0, og ,5 opp også der partall ville gått ned.
            (0.995, 99),
            (0.005, 1),
            (0.145, 15),
            (0.375, 38),
            (0.35, 35),
            (0.2 / 3, 7),
            # Flyttallsfeil like under ,5 runder likevel opp.
            (0.3 * 0.75, 23),
            (0.3 * (1 / 12), 3),
        ]:
            with self.subTest(verdi=verdi):
                self.assertEqual(hel_prosent(verdi), ventet)


class EkstraTest(DekningTestCase):
    def test_antall_sporringer_er_det_samme_for_1_og_3_quizer(self):
        self._forsok(self._quiz(LETT, 2), riktige=1)
        with CaptureQueriesContext(connection) as en:
            self._dekning()
        self._forsok(self._quiz(MIDDELS, 6), riktige=6)
        self._forsok(self._quiz(VANSKELIG, 9), riktige=3)
        with CaptureQueriesContext(connection) as tre:
            self._dekning()
        self.assertEqual(len(en), len(tre))
        self.assertEqual(len(tre), 2)

    def test_flere_riktige_svar_pa_samme_sporsmal_telles_en_gang(self):
        quiz = self._quiz(LETT, 2)
        forste = quiz.sporsmal.order_by("id").first()
        # To leverte forsøk og en levert øving med riktig svar på første spørsmål.
        self._forsok(quiz, riktige=2)
        self._forsok(quiz, riktige=1)
        oving = Okt.objects.create(
            notat=self.notat, type=Okttype.OVING, status=Oktstatus.LEVERT
        )
        Svar.objects.create(
            okt=oving,
            sporsmal=forste,
            alternativ=forste.alternativer.get(er_riktig=True),
        )
        self.assertEqual(self._dekning().nivaer[LETT], 1.0)

    def test_s7_viser_0_prosent_for_niva_med_quiz_uten_svar(self):
        self._quiz(VANSKELIG, 2)
        html = self._s7()
        self.assertEqual(_nivaa_html(html, "Vanskelig"), "0 %")
        self.assertEqual(_nivaa_html(html, "Lett"), "Ingen quiz")

    def test_s7_dekningskortet_overst_med_skjult_reiserute(self):
        html = self._s7()
        dekning = html.index('<h2 id="dekning-overskrift"')
        self.assertLess(html.index("<h1"), dekning)
        self.assertLess(dekning, html.index('<h2 id="ov-overskrift"'))
        kort = html[dekning : html.index('<h2 id="ov-overskrift"')]
        self.assertIn('<div class="reiserute reiserute-faar" aria-hidden="true">', kort)
        self.assertEqual(kort.count("Ingen quiz"), 3)

    def test_total_pa_halv_prosent_runder_opp_pa_s7(self):
        # Middels 3 av 4: 0,3 × 0,75 er 0,22499999999999998 som flyttall, vist som 23 %.
        self._forsok(self._quiz(MIDDELS, 4), riktige=3)
        html = self._s7()
        self.assertIn('<p class="text-2xl font-semibold tabular-nums">23 %</p>', html)
        self.assertIn('<span style="width: 23%"></span>', html)

    def test_vekten_for_vanskelig_i_totalen(self):
        self._forsok(self._quiz(VANSKELIG, 2), riktige=1)
        self.assertEqual(self._dekning().total, 0.25)
        self.assertIn(
            '<p class="text-2xl font-semibold tabular-nums">25 %</p>', self._s7()
        )

    def test_full_dekning_pa_alle_nivaer_gir_100_prosent(self):
        for nivaa in (LETT, MIDDELS, VANSKELIG):
            self._forsok(self._quiz(nivaa, 2), riktige=2)
        self.assertEqual(self._dekning().total, 1.0)
        self.assertIn(
            '<p class="text-2xl font-semibold tabular-nums">100 %</p>', self._s7()
        )

    def test_feil_svar_i_levert_okt_uten_feilbankrad_er_ikke_dekket(self):
        quiz = self._quiz(LETT, 2)
        okt = Okt.objects.create(
            notat=self.notat, quiz=quiz, type=Okttype.FORSOK, status=Oktstatus.LEVERT
        )
        for sporsmal in quiz.sporsmal.all():
            Svar.objects.create(
                okt=okt,
                sporsmal=sporsmal,
                alternativ=sporsmal.alternativer.get(er_riktig=False),
            )
        self.assertFalse(Feilbankrad.objects.exists())
        self.assertEqual(self._dekning().nivaer[LETT], 0.0)

    def test_levert_forsok_oppdaterer_s7(self):
        quiz = self._quiz(MIDDELS, 5)
        self.assertEqual(_nivaa_html(self._s7(), "Middels"), "0 %")
        self._lever(start_eller_fortsett_okt(quiz), riktig=True)
        html = self._s7()
        self.assertIn('<p class="text-2xl font-semibold tabular-nums">30 %</p>', html)
        self.assertEqual(_nivaa_html(html, "Middels"), "100 %")
