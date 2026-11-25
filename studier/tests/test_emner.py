"""Tester for emner i story 1.4: Oversikt, Nytt emne og emnesiden. Én test per rad i I/O-matrisen."""

from django.test import TestCase
from django.utils import timezone

from farequiz import feilmeldinger
from studier.models import Emne
from studier.services.emner import opprett_emne
from studier.tests.fabrikk import lag_bruker


def _innlogget(bruker):
    bruker.vilkar_godtatt = timezone.now()
    bruker.save(update_fields=["vilkar_godtatt"])
    return bruker


class OversiktTest(TestCase):
    def setUp(self):
        self.bruker = _innlogget(lag_bruker())
        self.client.force_login(self.bruker)

    def test_tom_oversikt(self):
        html = self.client.get("/").content.decode()
        self.assertIn("Ingen emner ennå. Opprett ditt første emne.", html)
        self.assertIn('href="/emner/ny/"', html)

    def test_emner_alfabetisk_uten_a_skille_store_og_sma(self):
        for navn in ("Beta", "alfa", "webutvikling", "Databaser", "Algoritmer"):
            Emne.objects.create(eier=self.bruker, navn=navn)
        html = self.client.get("/").content.decode()
        kort = [
            html.index(f'font-semibold">{navn}</span>')
            for navn in ("alfa", "Algoritmer", "Beta", "Databaser", "webutvikling")
        ]
        self.assertEqual(kort, sorted(kort))
        self.assertLess(html.index('href="/emner/ny/"'), kort[0])

    def test_antall_notater_pa_kortet(self):
        from studier.tests.fabrikk import lag_kjede

        tomt = Emne.objects.create(eier=self.bruker, navn="Tomt")
        lag_kjede(self.bruker, "Med notat")
        html = self.client.get("/").content.decode()
        self.assertIn("0 notater", html[html.index("Tomt") :])
        self.assertIn("1 notat<", html[html.index("Med notat") :])
        self.assertTrue(tomt.pk)

    def test_utlogget_pa_oversikt_sendes_til_innlogging(self):
        self.client.logout()
        svar = self.client.get("/")
        self.assertEqual(svar.status_code, 302)
        self.assertIn("/logg-inn/", svar["Location"])

    def test_andres_emner_vises_ikke(self):
        Emne.objects.create(eier=lag_bruker("annen@eks.no"), navn="Hemmelig")
        self.assertNotIn("Hemmelig", self.client.get("/").content.decode())


class OpprettEmneTest(TestCase):
    def setUp(self):
        self.bruker = _innlogget(lag_bruker())
        self.client.force_login(self.bruker)

    def test_navnet_trimmes_og_brukeren_sendes_til_emnesiden(self):
        svar = self.client.post("/emner/ny/", {"navn": "  HTML  "})
        emne = Emne.objects.get(eier=self.bruker)
        self.assertEqual(emne.navn, "HTML")
        self.assertRedirects(svar, f"/emner/{emne.pk}/", fetch_redirect_response=False)

    def test_tomt_navn_gir_feilmelding_og_ingen_emne(self):
        svar = self.client.post("/emner/ny/", {"navn": "   "})
        self.assertContains(svar, feilmeldinger.NAVN_TOMT)
        self.assertFalse(Emne.objects.exists())

    def test_navn_tatt_uten_a_skille_store_og_sma(self):
        Emne.objects.create(eier=self.bruker, navn="HTML")
        svar = self.client.post("/emner/ny/", {"navn": "html"})
        self.assertContains(svar, feilmeldinger.NAVN_TATT)
        self.assertEqual(Emne.objects.count(), 1)

    def test_for_langt_navn(self):
        svar = self.client.post("/emner/ny/", {"navn": "x" * 101})
        self.assertContains(svar, feilmeldinger.NAVN_FOR_LANGT)
        self.assertFalse(Emne.objects.exists())

    def test_samme_navn_hos_ulike_brukere_er_lov(self):
        Emne.objects.create(eier=lag_bruker("annen@eks.no"), navn="HTML")
        self.client.post("/emner/ny/", {"navn": "HTML"})
        self.assertEqual(Emne.objects.filter(navn="HTML").count(), 2)

    def test_opprett_emne_lagrer_for_eier(self):
        emne = opprett_emne(self.bruker, "  Kjemi ")
        self.assertEqual((emne.eier, emne.navn), (self.bruker, "Kjemi"))


class EmnesidenTest(TestCase):
    def setUp(self):
        self.bruker = _innlogget(lag_bruker())
        self.client.force_login(self.bruker)

    def test_eget_emne_viser_navn_og_tom_notatliste(self):
        emne = Emne.objects.create(eier=self.bruker, navn="HTML")
        html = self.client.get(f"/emner/{emne.pk}/").content.decode()
        self.assertIn("<h1", html)
        self.assertIn("HTML", html)
        self.assertIn("Ingen notater ennå. Last opp det første.", html)
        knapp = html.index(">Last opp notat</")
        start = html.rindex("<", 0, knapp)
        self.assertTrue(html.startswith("<a ", start))
        self.assertIn(f'href="/emner/{emne.pk}/last-opp/"', html[start:knapp])
        self.assertNotIn("disabled", html[start:knapp])
        self.assertNotIn(">Last opp notat</button>", html)

    def test_andres_emne_gir_404(self):
        annens = Emne.objects.create(eier=lag_bruker("annen@eks.no"), navn="Hemmelig")
        svar = self.client.get(f"/emner/{annens.pk}/")
        self.assertEqual(svar.status_code, 404)
        self.assertNotContains(svar, "Hemmelig", status_code=404)

    def test_ukjent_emne_gir_404(self):
        self.assertEqual(self.client.get("/emner/999999/").status_code, 404)

    def test_utlogget_sendes_til_innlogging(self):
        self.client.logout()
        svar = self.client.get("/emner/ny/")
        self.assertEqual(svar.status_code, 302)
        self.assertIn("/logg-inn/", svar["Location"])


class ValideringTest(TestCase):
    def setUp(self):
        self.bruker = _innlogget(lag_bruker())
        self.client.force_login(self.bruker)

    def test_norske_bokstaver_regnes_likt_ved_duplikat(self):
        Emne.objects.create(eier=self.bruker, navn="Øl")
        svar = self.client.post("/emner/ny/", {"navn": "øl"})
        self.assertContains(svar, feilmeldinger.NAVN_TATT)
        self.assertEqual(Emne.objects.count(), 1)

    def test_for_langt_navn_over_255_tegn_gir_norsk_melding(self):
        svar = self.client.post("/emner/ny/", {"navn": "x" * 300})
        self.assertContains(svar, feilmeldinger.NAVN_FOR_LANGT)
        self.assertNotContains(svar, "Ensure this value")
        self.assertFalse(Emne.objects.exists())

    def test_tom_post_gir_feilmelding(self):
        svar = self.client.post("/emner/ny/", {})
        self.assertContains(svar, feilmeldinger.NAVN_TOMT)

    def test_opprett_emne_avviser_tomt_navn_uten_skjema(self):
        from studier.services.emner import opprett_emne

        with self.assertRaises(ValueError):
            opprett_emne(self.bruker, "   ")
        self.assertFalse(Emne.objects.exists())

    def test_integrityerror_gir_norsk_melding_og_ingen_emne(self):
        from unittest import mock

        from django.db import IntegrityError

        with mock.patch("studier.views.opprett_emne", side_effect=IntegrityError):
            svar = self.client.post("/emner/ny/", {"navn": "Kjemi"})
        self.assertContains(svar, feilmeldinger.NAVN_TATT)
        self.assertFalse(Emne.objects.exists())


class TilbakeOgNavigasjonTest(TestCase):
    def setUp(self):
        self.bruker = _innlogget(lag_bruker())
        self.client.force_login(self.bruker)

    def test_tilbake_til_oversikt_pa_emnesiden(self):
        emne = Emne.objects.create(eier=self.bruker, navn="HTML")
        html = self.client.get(f"/emner/{emne.pk}/").content.decode()
        self.assertIn('aria-label="Tilbake til Oversikt"', html)
        self.assertIn('href="/" class="inline-flex', html)
        self.assertIn('<span aria-current="page">HTML</span>', html)

    def test_tilbake_til_oversikt_pa_nytt_emne(self):
        html = self.client.get("/emner/ny/").content.decode()
        self.assertIn('aria-label="Tilbake til Oversikt"', html)
        self.assertIn('<span aria-current="page">Nytt emne</span>', html)

    def test_andres_emne_gir_404_med_norsk_tekst(self):
        annens = Emne.objects.create(eier=lag_bruker("annen@eks.no"), navn="Hemmelig")
        svar = self.client.get(f"/emner/{annens.pk}/")
        self.assertContains(svar, "Fant ikke siden", status_code=404)
