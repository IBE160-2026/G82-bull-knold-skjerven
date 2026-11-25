"""Tester for «Fortsett der du slapp» (FR-18, UX-DR9, UX-DR14), én per rad i I/O-matrisen i spec 3.5."""

from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from studier.models import Emne, Okt, Svar
from studier.services.notater import last_opp
from studier.services.okter import forste_ubesvarte, lagre_svar
from studier.tests.test_ta_pa_nytt import TaPaNyttTestCase


class FortsetteTestCase(TaPaNyttTestCase):
    def _svar_n(self, okt, antall, nr_liste=None):
        for nr in nr_liste or range(1, antall + 1):
            rad = okt.innhold[nr - 1]
            sporsmal = okt.quiz.sporsmal.get(pk=rad["sporsmal"])
            valgt = sporsmal.alternativer.get(er_riktig=True)
            lagre_svar(okt, sporsmal, valgt)

    def _oversikt(self):
        return self.client.get("/").content.decode()

    def _boks(self, html):
        """Selve boksen «Fortsett der du slapp» (section), eller tom uten boks."""
        start = html.find('<section aria-labelledby="fortsett-overskrift"')
        if start == -1:
            return ""
        return html[start : html.index("</section>", start)]


class QuizkortFremdriftTest(FortsetteTestCase):
    def test_paabegynt_med_fem_av_ti(self):
        quiz = self._quiz(self.notat, antall=10)
        okt = self._okt(quiz)
        self._svar_n(okt, 5)
        html = self.client.get(self.notat_url).content.decode()
        self.assertIn("Påbegynt – spørsmål 5 av 10", html)
        self.assertEqual(self._kortknapp(html, quiz), "Fortsett")

    def test_paabegynt_uten_svar_gir_spoersmaal_1(self):
        html = self.client.get(self.notat_url).content.decode()
        self.assertIn("Påbegynt – spørsmål 1 av 5", html)
        self.assertEqual(self._kortknapp(html), "Fortsett")

    def test_levert_og_paabegynt_gir_fortsett(self):
        self._levert()
        self._ta_pa_nytt()
        html = self.client.get(self.notat_url).content.decode()
        self.assertEqual(self._kortknapp(html), "Fortsett")
        self.assertNotIn("Ta på nytt", html)

    def test_bare_levert_gir_ta_pa_nytt_uten_paabegynt(self):
        self._levert()
        html = self.client.get(self.notat_url).content.decode()
        self.assertEqual(self._kortknapp(html), "Ta på nytt")
        self.assertNotIn("Påbegynt", html)

    def test_s11_med_paabegynt_gir_fortsett(self):
        gammel = self._levert()
        self._ta_pa_nytt()
        html = self.client.get(self._resultat_url(gammel)).content.decode()
        skjema = html.index(f'action="{self._start_url()}"')
        slutt = html.index("</form>", skjema)
        self.assertIn(">Fortsett</button>", html[skjema:slutt])
        self.assertNotIn("Ta på nytt", html)


class OversiktBoksTest(FortsetteTestCase):
    def test_to_rader_sist_endret_oeverst_med_tekst_og_lenke(self):
        quiz2 = self._quiz(self.notat, antall=10)
        eldre = self._okt()
        nyere = self._okt(quiz2)
        self._svar_n(nyere, 3)
        self._svar_n(eldre, 1)
        Okt.objects.filter(pk=eldre.pk).update(
            sist_endret=timezone.now() - timedelta(hours=1)
        )
        html = self._oversikt()
        boks = self._boks(html)
        self.assertIn('<h2 id="fortsett-overskrift"', boks)
        self.assertIn("Fortsett der du slapp</h2>", boks)
        self.assertLess(html.index("Fortsett der du slapp"), html.index("<h1"))
        self.assertLess(
            boks.index("Middels, 10 spørsmål"), boks.index("Middels, 5 spørsmål")
        )
        emne = self.notat.emne.navn
        navn = self.notat.originalnavn
        self.assertIn(f"{emne} · {navn} · spørsmål 3 av 10", boks)
        self.assertIn(f"{emne} · {navn} · spørsmål 1 av 5", boks)
        self.assertIn(f'href="/okter/{nyere.pk}/sporsmal/4/"', boks)
        self.assertIn(f'href="/okter/{eldre.pk}/sporsmal/2/"', boks)
        self.assertEqual(boks.count(">Fortsett quizen</a>"), 2)
        self.assertIn(
            f'aria-describedby="fortsett-{nyere.pk} fortsett-fremdrift-{nyere.pk}"',
            boks,
        )
        self.assertIn(f'id="fortsett-{nyere.pk}"', boks)

    def test_uten_svar_gir_spoersmaal_1_av_m(self):
        okt = self._okt()
        html = self._oversikt()
        self.assertIn("spørsmål 1 av 5", html)
        self.assertIn(f'href="/okter/{okt.pk}/sporsmal/1/"', html)

    def test_lenke_til_foerste_ubesvarte(self):
        okt = self._okt()
        self._svar_n(okt, 0, nr_liste=[2, 3])
        html = self._oversikt()
        self.assertIn(f'href="/okter/{okt.pk}/sporsmal/1/"', html)
        self.assertIn("spørsmål 2 av 5", html)

    def test_lenken_aapner_s9_paa_spoersmaal_6_med_lagrede_svar(self):
        quiz = self._quiz(self.notat, antall=10)
        okt = self._okt(quiz)
        self._svar_n(okt, 5)
        html = self._oversikt()
        self.assertIn(f'href="/okter/{okt.pk}/sporsmal/6/"', html)
        svar = self.client.get(self._url(okt, 6))
        self.assertContains(svar, "Spørsmål 6 av 10")
        self.assertEqual(Svar.objects.filter(okt=okt).count(), 5)

    def test_tom_uten_paabegynte(self):
        self._levert()
        html = self._oversikt()
        self.assertNotIn("Fortsett der du slapp", html)
        self.assertNotIn("Fortsett quizen", html)

    def test_annen_brukers_forsok_vises_ikke(self):
        _, quiz = self._annen_bruker()
        annen_okt = self._okt(quiz)
        self.client.force_login(self.bruker)
        boks = self._boks(self._oversikt())
        self.assertEqual(boks.count(">Fortsett quizen</a>"), 1)
        self.assertIn(f"/okter/{self.okt.pk}/", boks)
        self.assertNotIn(f"/okter/{annen_okt.pk}/", boks)
        self.assertNotIn("hemmelig", boks)

    def test_alle_besvart_men_ikke_levert_gir_5_av_5_og_forste_ubesvarte(self):
        self._svar_n(self.okt, 5)
        boks = self._boks(self._oversikt())
        self.assertIn("spørsmål 5 av 5", boks)
        self.assertEqual(forste_ubesvarte(self.okt), 1)
        self.assertIn(f'href="/okter/{self.okt.pk}/sporsmal/1/"', boks)

    def test_sortert_paa_sist_endret_med_eget_emne_og_notat(self):
        a = self.okt
        emne_b = Emne.objects.create(eier=self.bruker, navn="Databaser")
        notat_b = last_opp(emne_b, SimpleUploadedFile("sql.txt", b"SQL."), self.bruker)
        b = self._okt(self._quiz(notat_b))
        self._svar_n(a, 1)  # A endres sist, men er opprettet først.
        boks = self._boks(self._oversikt())
        tekst_a = f"{self.notat.emne.navn} · {self.notat.originalnavn} · spørsmål"
        tekst_b = f"Databaser · {notat_b.originalnavn} · spørsmål"
        self.assertIn(tekst_a, boks)
        self.assertIn(tekst_b, boks)
        self.assertLess(boks.index(f"/okter/{a.pk}/"), boks.index(f"/okter/{b.pk}/"))
        self.assertLess(boks.index(tekst_a), boks.index(tekst_b))

    def test_antall_sporringer_er_uavhengig_av_antall_rader(self):
        self._svar_n(self.okt, 2)
        with CaptureQueriesContext(connection) as en:
            self._oversikt()
        for _ in range(2):
            self._svar_n(self._okt(self._quiz(self.notat)), 2)
        with CaptureQueriesContext(connection) as tre:
            self._oversikt()
        self.assertEqual(len(en), len(tre))

    def test_samme_fremdrift_fra_annen_klient(self):
        quiz = self._quiz(self.notat, antall=10)
        okt = self._okt(quiz)
        self._svar_n(okt, 4)
        annen = Client()
        annen.force_login(self.bruker)
        s3 = annen.get("/").content.decode()
        s7 = annen.get(self.notat_url).content.decode()
        self.assertIn("spørsmål 4 av 10", s3)
        self.assertIn("Påbegynt – spørsmål 4 av 10", s7)
