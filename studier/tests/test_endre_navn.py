"""Tester for å gi emne nytt navn (FR-5), én per rad i I/O-matrisen i spec 1.5."""

from django.test import TestCase
from django.utils import timezone

from farequiz import feilmeldinger
from studier.models import Emne, Notat
from studier.tests.fabrikk import lag_bruker, lag_kjede


def _innlogget(bruker):
    bruker.vilkar_godtatt = timezone.now()
    bruker.save(update_fields=["vilkar_godtatt"])
    return bruker


class EndreNavnTest(TestCase):
    def setUp(self):
        self.bruker = _innlogget(lag_bruker())
        self.client.force_login(self.bruker)
        self.emne = Emne.objects.create(eier=self.bruker, navn="Kjemi")

    def _url(self, emne=None):
        return f"/emner/{(emne or self.emne).pk}/navn/"

    def test_s4_viser_skjema_med_dagens_navn(self):
        html = self.client.get(f"/emner/{self.emne.pk}/").content.decode()
        self.assertIn('value="Kjemi"', html)
        self.assertIn("Lagre navn", html)

    def test_nytt_navn_lagres_og_sender_til_s4(self):
        svar = self.client.post(self._url(), {"navn": "  Biologi "})
        self.emne.refresh_from_db()
        self.assertEqual(self.emne.navn, "Biologi")
        self.assertRedirects(
            svar, f"/emner/{self.emne.pk}/", fetch_redirect_response=False
        )

    def test_ny_skrivemate_av_eget_navn_er_lov(self):
        Emne.objects.filter(pk=self.emne.pk).update(navn="html")
        self.client.post(self._url(), {"navn": "HTML"})
        self.emne.refresh_from_db()
        self.assertEqual(self.emne.navn, "HTML")

    def test_tomt_navn_beholder_gammelt_navn(self):
        svar = self.client.post(self._url(), {"navn": "   "})
        self.emne.refresh_from_db()
        self.assertEqual(self.emne.navn, "Kjemi")
        self.assertContains(svar, feilmeldinger.NAVN_TOMT)

    def test_navn_tatt_av_annet_emne(self):
        Emne.objects.create(eier=self.bruker, navn="Biologi")
        svar = self.client.post(self._url(), {"navn": "biologi"})
        self.emne.refresh_from_db()
        self.assertEqual(self.emne.navn, "Kjemi")
        self.assertContains(svar, feilmeldinger.NAVN_TATT)

    def test_for_langt_navn(self):
        svar = self.client.post(self._url(), {"navn": "x" * 101})
        self.emne.refresh_from_db()
        self.assertEqual(self.emne.navn, "Kjemi")
        self.assertContains(svar, feilmeldinger.NAVN_FOR_LANGT)

    def test_feil_har_aria_og_fokus_ved_feltet(self):
        svar = self.client.post(self._url(), {"navn": ""})
        html = svar.content.decode()
        self.assertIn('aria-describedby="feil-endre-navn"', html)
        self.assertIn('id="feil-endre-navn" role="alert" tabindex="-1" autofocus', html)

    def test_notater_og_quizer_er_uendret(self):
        lag_kjede(self.bruker, "Fysikk")
        emne = Emne.objects.get(eier=self.bruker, navn="Fysikk")
        from studier.models import Feilbankrad, Okt, Quiz, Svar

        far = {
            "notat": Notat.objects.filter(emne=emne).count(),
            "quiz": Quiz.objects.filter(notat__emne=emne).count(),
            "okt": Okt.objects.filter(notat__emne=emne).count(),
            "svar": Svar.objects.filter(okt__notat__emne=emne).count(),
            "feilbank": Feilbankrad.objects.filter(
                sporsmal__quiz__notat__emne=emne
            ).count(),
        }
        self.client.post(f"/emner/{emne.pk}/navn/", {"navn": "Biologi fysikk"})
        etter = {
            "notat": Notat.objects.filter(emne=emne).count(),
            "quiz": Quiz.objects.filter(notat__emne=emne).count(),
            "okt": Okt.objects.filter(notat__emne=emne).count(),
            "svar": Svar.objects.filter(okt__notat__emne=emne).count(),
            "feilbank": Feilbankrad.objects.filter(
                sporsmal__quiz__notat__emne=emne
            ).count(),
        }
        self.assertEqual(etter, far)
        emne.refresh_from_db()
        self.assertEqual(emne.navn, "Biologi fysikk")

    def test_samme_navn_er_lov(self):
        svar = self.client.post(self._url(), {"navn": "Kjemi"})
        self.assertRedirects(
            svar, f"/emner/{self.emne.pk}/", fetch_redirect_response=False
        )

    def test_nytt_navn_vises_pa_oversikt(self):
        self.client.post(self._url(), {"navn": "Biologi"})
        html = self.client.get("/").content.decode()
        self.assertIn('font-semibold">Biologi</span>', html)
        self.assertNotIn('font-semibold">Kjemi</span>', html)

    def test_andres_emne_gir_404(self):
        annens = Emne.objects.create(eier=lag_bruker("annen@eks.no"), navn="Hemmelig")
        svar = self.client.post(self._url(annens), {"navn": "Nytt"})
        self.assertEqual(svar.status_code, 404)
        annens.refresh_from_db()
        self.assertEqual(annens.navn, "Hemmelig")

    def test_utlogget_sendes_til_innlogging(self):
        self.client.logout()
        svar = self.client.post(self._url(), {"navn": "Nytt"})
        self.assertEqual(svar.status_code, 302)
        self.assertIn("/logg-inn/", svar["Location"])

    def test_integrityerror_gir_norsk_melding(self):
        from unittest import mock

        from django.db import IntegrityError

        with mock.patch("studier.views.gi_nytt_navn", side_effect=IntegrityError):
            svar = self.client.post(self._url(), {"navn": "Nytt"})
        self.emne.refresh_from_db()
        self.assertEqual(self.emne.navn, "Kjemi")
        self.assertContains(svar, feilmeldinger.NAVN_TATT)
