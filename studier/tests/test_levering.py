"""Tester for å levere og se resultatet (FR-17, FR-19, FR-21, AD-18, AD-20), én per rad i I/O-matrisen i spec 3.3."""

import re
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import TestCase

import ki
from farequiz import feilmeldinger
from studier.models import (
    Alternativ,
    Feilbankrad,
    Hendelse,
    Jobbstatus,
    Okt,
    Oktstatus,
    Quiz,
    Sporsmal,
    Svar,
)
from studier.services import okter
from studier.services.feilbank import fasit_synlig
from studier.services.generering import kjor_steg, opprett_jobb
from studier.services.okter import (
    OktErLevert,
    UbesvarteSporsmal,
    lagre_svar,
    lever_okt,
)
from studier.tests.test_generering import _raatt
from studier.tests.test_okter import OktTestCase


class LeveringTestCase(OktTestCase):
    def setUp(self):
        super().setUp()
        self.okt = self._okt()

    def _besvar(self, nr, riktig, okt=None):
        okt = okt or self.okt
        sporsmal, alternativer = self._rad(okt, nr)
        valgt = next(a for a in alternativer if a.er_riktig == riktig)
        lagre_svar(okt, sporsmal, valgt)
        return sporsmal, valgt

    def _besvar_alle(self, riktige=(), okt=None):
        okt = okt or self.okt
        for nr in range(1, len(okt.innhold) + 1):
            self._besvar(nr, nr in riktige, okt)

    def _lever(self, okt=None):
        return self.client.post(f"/okter/{(okt or self.okt).pk}/lever/")

    def _resultat_url(self, okt=None):
        return f"/okter/{(okt or self.okt).pk}/resultat/"

    def _lever_url(self, okt=None):
        return f"/okter/{(okt or self.okt).pk}/lever/"


class S10Test(LeveringTestCase):
    def test_alle_besvart_gir_lever_uten_aria_disabled(self):
        self._besvar_alle(riktige={1, 2, 3, 4, 5})
        html = self.client.get(self._lever_url()).content.decode()
        self.assertEqual(html.count("– besvart</a>"), 5)
        self.assertNotIn("ikke besvart", html)
        self.assertIn(">Lever</button>", html)
        self.assertNotIn("aria-disabled", html)
        self.assertNotIn("Du har ikke svart", html)

    def test_ubesvarte_gir_aria_disabled_og_tekst_med_hjelp(self):
        for nr in (1, 3, 5):
            self._besvar(nr, True)
        html = self.client.get(self._lever_url()).content.decode()
        self.assertIn('aria-disabled="true"', html)
        self.assertIn("Du har ikke svart på spørsmål 2 og 4.", html)
        self.assertIn(feilmeldinger.LEVER_HJELP, html)
        self.assertRegex(html, r'aria-describedby="[^"]*lever-hjelp')
        self.assertIn('id="lever-hjelp"', html)
        self.assertNotIn('role="alert"', html)
        self.assertEqual(html.count("ikke besvart</a>"), 2)

    def test_oppramsingen(self):
        tekst = feilmeldinger.ubesvarte_tekst
        self.assertEqual(tekst([4]), "Du har ikke svart på spørsmål 4.")
        self.assertEqual(tekst([4, 7]), "Du har ikke svart på spørsmål 4 og 7.")
        self.assertEqual(tekst([2, 4, 7]), "Du har ikke svart på spørsmål 2, 4 og 7.")

    def test_post_med_ubesvarte_leverer_ikke_og_viser_s10_med_alert(self):
        for nr in (1, 3, 4, 5):
            self._besvar(nr, False)
        svar = self._lever()
        self.assertEqual(svar.status_code, 200)
        html = svar.content.decode()
        self.assertRegex(
            html,
            r'<p id="lever-ubesvarte" role="alert"[^>]*>Du har ikke svart på spørsmål 2\.',
        )
        self.assertIn("Spørsmål 2 – ikke besvart</a>", html)
        self.okt.refresh_from_db()
        self.assertEqual(self.okt.status, Oktstatus.PABEGYNT)
        self.assertIsNone(self.okt.levert_tidspunkt)
        self.assertIsNone(self.okt.poengsum)
        self.assertFalse(Feilbankrad.objects.exists())
        self.assertFalse(Svar.objects.exclude(hendelse="").exists())

    def test_get_for_levert_okt_sender_til_s11(self):
        self._besvar_alle()
        lever_okt(self.okt)
        self.assertRedirects(self.client.get(self._lever_url()), self._resultat_url())


class LeverTest(LeveringTestCase):
    def test_lever_lagrer_status_poeng_og_hendelser(self):
        self._besvar_alle(riktige={1, 2})
        svar = self._lever()
        self.assertRedirects(svar, self._resultat_url())
        self.okt.refresh_from_db()
        self.assertEqual(self.okt.status, Oktstatus.LEVERT)
        self.assertIsNotNone(self.okt.levert_tidspunkt)
        self.assertEqual((self.okt.poengsum, self.okt.antall), (2, 5))
        hendelser = [
            Svar.objects.get(okt=self.okt, sporsmal_id=rad["sporsmal"]).hendelse
            for rad in self.okt.innhold
        ]
        self.assertEqual(
            hendelser,
            [Hendelse.INGEN, Hendelse.INGEN] + [Hendelse.LAGT_I] * 3,
        )
        self.assertEqual(Feilbankrad.objects.count(), 3)

    def _tilstand(self):
        return (
            list(Svar.objects.order_by("pk").values_list("hendelse", flat=True)),
            list(
                Feilbankrad.objects.order_by("pk").values_list("pk", "riktige_pa_rad")
            ),
        )

    def test_dobbel_levering_gir_ett_sett_hendelser(self):
        self._besvar_alle(riktige={1})
        forste = self._lever()
        tilstand = self._tilstand()
        andre = self._lever()
        self.assertRedirects(forste, self._resultat_url())
        self.assertRedirects(andre, self._resultat_url())
        self.assertEqual(self._tilstand(), tilstand)
        self.assertFalse(lever_okt(Okt.objects.get(pk=self.okt.pk)))
        self.assertEqual(self._tilstand(), tilstand)

    def test_utdatert_okt_objekt_gir_ikke_ny_levering(self):
        self._besvar_alle(riktige={1})
        utdatert = Okt.objects.get(pk=self.okt.pk)
        lever_okt(self.okt)
        tilstand = self._tilstand()
        self.assertFalse(lever_okt(utdatert))
        self.assertEqual(self._tilstand(), tilstand)

    def test_lever_okt_med_ubesvarte_hever_og_ruller_tilbake(self):
        self._besvar(1, False)
        self._besvar(3, False)
        with self.assertRaises(UbesvarteSporsmal) as ctx:
            lever_okt(self.okt)
        self.assertEqual(ctx.exception.nr, [2, 4, 5])
        self.okt.refresh_from_db()
        self.assertEqual(self.okt.status, Oktstatus.PABEGYNT)
        self.assertFalse(Feilbankrad.objects.exists())

    def test_pabegynt_okt_pavirker_ikke_feilbanken(self):
        self._besvar_alle()
        self.assertFalse(Feilbankrad.objects.exists())
        self.assertFalse(Svar.objects.exclude(hendelse="").exists())

    def test_fasit_synlig_bare_for_laerte(self):
        sporsmal, _ = self._besvar(1, False)
        self.assertFalse(fasit_synlig(sporsmal))
        self._besvar_alle()
        lever_okt(self.okt)
        self.assertFalse(fasit_synlig(sporsmal))
        Feilbankrad.objects.filter(sporsmal=sporsmal).update(
            laert_tidspunkt="2026-11-25T10:00:00Z"
        )
        self.assertTrue(fasit_synlig(sporsmal))


class S11Test(LeveringTestCase):
    def _levert(self, riktige):
        self._besvar_alle(riktige=riktige)
        lever_okt(self.okt)

    def _html(self):
        svar = self.client.get(self._resultat_url())
        self.assertEqual(svar.status_code, 200)
        return svar.content.decode()

    def test_resultat_viser_poeng_feilbank_og_rader(self):
        self._levert({1, 2})
        html = self._html()
        self.assertIn(">Resultat</h1>", html)
        self.assertRegex(
            html, r'<p role="status"[^>]*tabular-nums[^>]*>2 av 5 riktige</p>'
        )
        self.assertIn("3 spørsmål er lagt i feilbanken.", html)
        self.assertEqual(html.count("Ditt svar:"), 5)
        self.assertEqual(html.count(">Riktig</strong>"), 2)
        self.assertEqual(html.count(">Feil</strong>"), 3)
        self.assertIn('aria-hidden="true">✓</span>', html)
        self.assertIn('aria-hidden="true">✕</span>', html)
        self.assertLess(html.index("1. "), html.index("5. "))
        self.assertIn("Tilbake til notatet", html)
        self.assertIn("Øv på feil (3)", html)
        # «Ta på nytt» kom i 3.4 og testes i test_ta_pa_nytt.py.
        nav = re.search(
            r'<nav aria-label="Brødsmuler".*?</nav>', html, re.DOTALL
        ).group()
        self.assertIn('<span aria-current="page">Resultat</span>', nav)
        self.assertIn(f'href="{self.notat_url}"', nav)

    def test_ingen_feilbanktekst_ved_full_score(self):
        self._levert({1, 2, 3, 4, 5})
        html = self._html()
        self.assertIn("5 av 5 riktige", html)
        self.assertNotIn("feilbanken", html)

    def test_fasit_skjult_for_feil_svar(self):
        self._levert(set())
        html = self._html()
        self.assertNotIn("Riktig svar", html)
        self.assertNotIn("Begrunnelse", html)
        for rad in self.okt.innhold:
            sporsmal = Sporsmal.objects.get(pk=rad["sporsmal"])
            riktig = Alternativ.objects.get(sporsmal=sporsmal, er_riktig=True)
            self.assertNotIn(riktig.tekst, html)
            self.assertNotIn(sporsmal.begrunnelse, html)

    def test_fasit_synlig_for_laert_sporsmal(self):
        self._levert({2, 3, 4, 5})
        sporsmal, _ = self._rad(self.okt, 1)
        Feilbankrad.objects.filter(sporsmal=sporsmal).update(
            laert_tidspunkt="2026-11-25T10:00:00Z"
        )
        html = self._html()
        riktig = sporsmal.alternativer.get(er_riktig=True)
        self.assertIn(f"Riktig svar: <span>{riktig.tekst}</span>", html)
        self.assertIn(f"Begrunnelse: <span>{sporsmal.begrunnelse}</span>", html)
        self.assertEqual(html.count("Riktig svar:"), 1)

    def test_antall_lagt_i_leses_fra_hendelse(self):
        self._levert({1})
        Svar.objects.filter(okt=self.okt).update(hendelse=Hendelse.INGEN)
        self.assertNotIn("feilbanken", self._html())

    def test_pabegynt_okt_sendes_til_s10(self):
        self.assertRedirects(self.client.get(self._resultat_url()), self._lever_url())

    def test_spraak_en_gir_lang(self):
        Quiz.objects.filter(pk=self.quiz.pk).update(sprak="en")
        self._levert({1})
        html = self._html()
        self.assertIn('<strong lang="en">1. ', html)
        self.assertIn('Ditt svar: <span lang="en">', html)


class LevertOktIFlytTest(LeveringTestCase):
    def test_s9_get_og_post_for_levert_okt_sender_til_s11(self):
        self._besvar_alle()
        lever_okt(self.okt)
        antall = Svar.objects.count()
        _, alternativer = self._rad(self.okt, 1)
        self.assertRedirects(
            self.client.get(self._url(self.okt, 1)), self._resultat_url()
        )
        svar = self._svar(self.okt, 1, alternativ=alternativer[0])
        self.assertRedirects(svar, self._resultat_url())
        self.assertEqual(Svar.objects.count(), antall)

    def test_okt_er_levert_i_s9_sender_til_s11(self):
        _, alternativer = self._rad(self.okt, 1)
        with mock.patch("studier.views.lagre_svar", side_effect=OktErLevert("levert")):
            svar = self._svar(self.okt, 1, alternativ=alternativer[0])
        self.assertRedirects(svar, self._resultat_url(), fetch_redirect_response=False)

    def test_gammel_s8_fane_etter_levering_gir_hx_redirect_til_s7(self):
        jobb = opprett_jobb(self.notat, "lett", 5)
        with mock.patch.object(ki, "generer", return_value=_raatt(5)):
            for _ in range(2):
                kjor_steg(jobb.pk)
            steg_url = f"/jobber/{jobb.pk}/steg/"
            self.client.post(steg_url, {"vist": Jobbstatus.SJEKKER})
        jobb.refresh_from_db()
        self.assertEqual(jobb.status, Jobbstatus.FERDIG)
        okt = Okt.objects.get(quiz=jobb.quiz)
        for rad in okt.innhold:
            sporsmal = Sporsmal.objects.get(pk=rad["sporsmal"])
            lagre_svar(okt, sporsmal, sporsmal.alternativer.first())
        lever_okt(okt)
        svar = self.client.post(steg_url, {"vist": Jobbstatus.FERDIG})
        self.assertEqual(svar["HX-Redirect"], self.notat_url)
        self.assertEqual(Okt.objects.filter(quiz=jobb.quiz).count(), 1)

    def test_gammel_s8_fane_med_levert_og_nytt_pabegynt_gir_hx_redirect_til_ny_okt(
        self,
    ):
        jobb = opprett_jobb(self.notat, "lett", 5)
        with mock.patch.object(ki, "generer", return_value=_raatt(5)):
            for _ in range(2):
                kjor_steg(jobb.pk)
            steg_url = f"/jobber/{jobb.pk}/steg/"
            self.client.post(steg_url, {"vist": Jobbstatus.SJEKKER})
        okt = Okt.objects.get(quiz=jobb.quiz)
        for rad in okt.innhold:
            sporsmal = Sporsmal.objects.get(pk=rad["sporsmal"])
            lagre_svar(okt, sporsmal, sporsmal.alternativer.first())
        lever_okt(okt)
        self.client.post(f"/quizer/{jobb.quiz.pk}/start/")
        ny = Okt.objects.get(quiz=jobb.quiz, status=Oktstatus.PABEGYNT)
        svar = self.client.post(steg_url, {"vist": Jobbstatus.FERDIG})
        self.assertEqual(svar["HX-Redirect"], f"/okter/{ny.pk}/sporsmal/1/")
        self.assertEqual(Okt.objects.filter(quiz=jobb.quiz).count(), 2)


class TilgangTest(LeveringTestCase):
    def test_annens_okt_gir_404_pa_s10_og_s11(self):
        _, annens_quiz = self._annen_bruker()
        annens_okt = okter.start_eller_fortsett_okt(annens_quiz)
        # Klienten er nå innlogget som den andre. Logg inn som eieren av testen.
        self.client.force_login(self.bruker)
        for metode, url in (
            ("get", f"/okter/{annens_okt.pk}/lever/"),
            ("post", f"/okter/{annens_okt.pk}/lever/"),
            ("get", f"/okter/{annens_okt.pk}/resultat/"),
        ):
            with self.subTest(metode=metode, url=url):
                self.assertEqual(getattr(self.client, metode)(url).status_code, 404)
        annens_okt.refresh_from_db()
        self.assertEqual(annens_okt.status, Oktstatus.PABEGYNT)
        self.assertFalse(Feilbankrad.objects.exists())


class EnesteStedRegistrerSvarTest(TestCase):
    """`lever_okt` er eneste sted som kaller `registrer_svar` (AD-2, AD-18)."""

    APPER = ("studier", "kontoer", "farequiz", "ki")
    TILLATT = {Path("studier/services/okter.py"), Path("studier/services/feilbank.py")}
    MONSTER = re.compile(r"\bregistrer_svar\b")

    def test_monsteret_finner_kall(self):
        self.assertTrue(self.MONSTER.search("h = registrer_svar(s, riktig=True)"))
        self.assertTrue(self.MONSTER.search("feilbank.registrer_svar(s, riktig=x)"))
        self.assertFalse(self.MONSTER.search("lever_okt(okt)"))

    def test_ingen_andre_kaller_registrer_svar(self):
        rot = Path(settings.BASE_DIR)
        treff = []
        for app in self.APPER:
            for fil in (rot / app).rglob("*.py"):
                relativ = fil.relative_to(rot)
                deler = set(relativ.parts)
                if (
                    relativ in self.TILLATT
                    or "migrations" in deler
                    or "tests" in deler
                    or fil.name.startswith("tests")
                ):
                    continue
                for nr, linje in enumerate(
                    fil.read_text(encoding="utf-8").splitlines(), 1
                ):
                    if self.MONSTER.search(linje):
                        treff.append(f"{relativ}:{nr}: {linje.strip()}")
        self.assertEqual(treff, [])

    def test_okter_kaller_registrer_svar_bare_en_gang_i_lever_okt(self):
        kilde = (Path(settings.BASE_DIR) / "studier/services/okter.py").read_text(
            encoding="utf-8"
        )
        kall = [linje for linje in kilde.splitlines() if "registrer_svar(" in linje]
        self.assertEqual(len(kall), 1)
