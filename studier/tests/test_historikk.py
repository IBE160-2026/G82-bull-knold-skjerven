"""Tester for historikken på S7 (FR-26, AD-6, UX-DR23, UX-DR29), spec 5.3."""

import re
from datetime import UTC, datetime, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test.utils import CaptureQueriesContext

from studier.models import Alternativ, Okt, Oktstatus, Okttype, Sporsmal
from studier.services.notater import last_opp
from studier.services.okter import lagre_svar
from studier.tests.test_levering import LeveringTestCase

TOM = "Ingen forsøk ennå. Ta en quiz for å se historikken."
TABELL = re.compile(r"<table.*?</table>", re.DOTALL)
KORT = re.compile(r'<ul class="[^"]*md:hidden[^"]*">.*?</ul>', re.DOTALL)


class HistorikkTestCase(LeveringTestCase):
    def _levert(self, riktige=(), tidspunkt=None, quiz=None):
        """Leverer et forsøk på quizen (standard `self.quiz`) med de gitte riktige numrene."""
        okt = self._okt(quiz)
        for nr, rad in enumerate(okt.innhold, start=1):
            sporsmal = Sporsmal.objects.get(pk=rad["sporsmal"])
            valgt = Alternativ.objects.filter(
                pk__in=rad["alternativer"], er_riktig=nr in riktige
            ).first()
            lagre_svar(okt, sporsmal, valgt)
        self._lever(okt)
        okt.refresh_from_db()
        self.assertEqual(okt.status, Oktstatus.LEVERT)
        if tidspunkt is not None:
            Okt.objects.filter(pk=okt.pk).update(levert_tidspunkt=tidspunkt)
        return okt

    def _html(self):
        return self.client.get(self.notat_url).content.decode()

    def _historikk(self, html):
        start = html.index('id="historikk-overskrift"')
        return html[start:]


class TomTilstandTest(HistorikkTestCase):
    def test_uten_leverte_forsok_star_tomteksten_og_ingen_tabell(self):
        html = self._historikk(self._html())
        self.assertIn(">Historikk</h2>", html)
        self.assertIn(TOM, html)
        self.assertNotIn("<table", html)
        self.assertIsNone(KORT.search(html))

    def test_pabegynt_forsok_og_ovingsokt_vises_ikke(self):
        # self.okt er påbegynt. En levert øvingsøkt legges til direkte.
        self._besvar(1, True)
        Okt.objects.create(
            notat=self.notat,
            type=Okttype.OVING,
            status=Oktstatus.LEVERT,
            levert_tidspunkt=datetime(2026, 11, 20, 10, 0, tzinfo=UTC),
            poengsum=1,
            antall=1,
        )
        html = self._historikk(self._html())
        self.assertIn(TOM, html)
        self.assertNotIn("<table", html)
        self.assertIsNone(KORT.search(html))
        self.assertNotIn("1 av 1", html)


class RadTest(HistorikkTestCase):
    def test_rad_har_dato_i_oslo_quiz_poengsum_og_lenke(self):
        okt = self._levert(
            riktige={1, 2, 3}, tidspunkt=datetime(2026, 11, 26, 13, 5, tzinfo=UTC)
        )
        html = self._historikk(self._html())
        self.assertNotIn(TOM, html)
        url = f'href="/okter/{okt.pk}/resultat/"'
        for del_ in (TABELL.search(html).group(), KORT.search(html).group()):
            self.assertIn("26. november 2026 kl. 14:05", del_)
            self.assertIn("Middels, 5 spørsmål", del_)
            self.assertIn("3 av 5", del_)
            self.assertIn(url, del_)

    def test_tabellen_har_caption_og_kolonneoverskrifter(self):
        self._levert(riktige={1})
        tabell = TABELL.search(self._historikk(self._html())).group()
        self.assertIn("<caption", tabell)
        self.assertIn("Forsøk, nyeste først", tabell)
        self.assertEqual(
            re.findall(r'<th scope="col"[^>]*>([^<]+)</th>', tabell),
            ["Dato", "Quiz", "Poengsum"],
        )
        self.assertIn("md:table", re.search(r"<table[^>]*>", tabell).group())

    def test_kortet_er_en_lenke_med_skilletegn_for_skjermleser(self):
        okt = self._levert(riktige={1, 2})
        kort = KORT.search(self._historikk(self._html())).group()
        lenke = re.search(
            rf'<a href="/okter/{okt.pk}/resultat/"[^>]*>(.*?)</a>', kort, re.DOTALL
        ).group(1)
        self.assertEqual(lenke.count('<span class="sr-only">, </span>'), 2)
        self.assertIn("2 av 5", lenke)

    def test_datoen_er_radoverskrift(self):
        okt = self._levert(riktige={1})
        tabell = TABELL.search(self._historikk(self._html())).group()
        self.assertRegex(
            tabell, rf'<th scope="row"[^>]*><a href="/okter/{okt.pk}/resultat/"'
        )

    def test_likt_tidspunkt_gir_nyeste_pk_forst(self):
        tid = datetime(2026, 11, 20, 9, 0, tzinfo=UTC)
        forst = self._levert(riktige={1}, tidspunkt=tid)
        sist = self._levert(riktige={1, 2}, tidspunkt=tid)
        tabell = TABELL.search(self._historikk(self._html())).group()
        rekkefolge = [
            int(pk) for pk in re.findall(r'href="/okter/(\d+)/resultat/"', tabell)
        ]
        self.assertEqual(rekkefolge, [sist.pk, forst.pk])

    def test_nyeste_forst(self):
        tid = datetime(2026, 11, 20, 9, 0, tzinfo=UTC)
        eldst = self._levert(riktige={1}, tidspunkt=tid)
        nyest = self._levert(riktige={1, 2}, tidspunkt=tid + timedelta(days=2))
        midt = self._levert(riktige={1, 2, 3}, tidspunkt=tid + timedelta(days=1))
        tabell = TABELL.search(self._historikk(self._html())).group()
        rekkefolge = [
            int(pk) for pk in re.findall(r'href="/okter/(\d+)/resultat/"', tabell)
        ]
        self.assertEqual(rekkefolge, [nyest.pk, midt.pk, eldst.pk])

    def test_alle_quizer_pa_notatet_men_ikke_andre_notater(self):
        lett = self._quiz(self.notat, antall=6)
        lett.vanskelighetsgrad = "lett"
        lett.save()
        self._levert(riktige={1})
        self._levert(riktige={1, 2}, quiz=lett)
        annet_notat = last_opp(
            self.emne, SimpleUploadedFile("annet.txt", b"Annet notat."), self.bruker
        )
        annen = self._levert(riktige={1}, quiz=self._quiz(annet_notat, antall=7))
        tabell = TABELL.search(self._historikk(self._html())).group()
        self.assertIn("Middels, 5 spørsmål", tabell)
        self.assertIn("Lett, 6 spørsmål", tabell)
        self.assertEqual(tabell.count("<tr class"), 3)  # overskrift + 2 rader
        self.assertNotIn(f"/okter/{annen.pk}/", tabell)
        self.assertNotIn("7 spørsmål", tabell)


class SporringerTest(HistorikkTestCase):
    def test_samme_antall_sporringer_for_ett_og_tre_forsok(self):
        self._levert(riktige={1})
        with CaptureQueriesContext(connection) as en:
            self._html()
        self._levert(riktige={1, 2})
        self._levert(riktige={1, 2, 3})
        with CaptureQueriesContext(connection) as tre:
            self._html()
        self.assertEqual(len(en), len(tre))
