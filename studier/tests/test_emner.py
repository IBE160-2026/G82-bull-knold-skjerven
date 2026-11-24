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
        for navn in ("webutvikling", "Databaser", "Algoritmer"):
            Emne.objects.create(eier=self.bruker, navn=navn)
        html = self.client.get("/").content.decode()
        posisjoner = [
            html.index(n) for n in ("Algoritmer", "Databaser", "webutvikling")
        ]
        self.assertEqual(posisjoner, sorted(posisjoner))
        self.assertLess(html.index('href="/emner/ny/"'), posisjoner[0])

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
        self.assertIn('aria-disabled="true"', html)

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
