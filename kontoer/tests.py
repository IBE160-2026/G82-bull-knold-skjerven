from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from kontoer.models import Bruker


class BrukerManagerTest(TestCase):
    def test_auth_user_model_er_bruker(self):
        self.assertIs(get_user_model(), Bruker)

    def test_create_user_lagrer_epost_med_sma_bokstaver(self):
        bruker = Bruker.objects.create_user("Ola@Eks.no", "hemmelig-passord")
        bruker.refresh_from_db()
        self.assertEqual(bruker.email, "ola@eks.no")

    def test_passord_lagres_bare_som_hash(self):
        bruker = Bruker.objects.create_user("ola@eks.no", "hemmelig-passord")
        self.assertNotEqual(bruker.password, "hemmelig-passord")
        self.assertTrue(bruker.check_password("hemmelig-passord"))

    def test_bruker_har_ikke_brukernavn_og_bruker_epost(self):
        self.assertIsNone(Bruker.username)
        self.assertEqual(Bruker.USERNAME_FIELD, "email")
        self.assertEqual(Bruker.REQUIRED_FIELDS, [])

    def test_vilkar_godtatt_er_tomt_som_standard(self):
        bruker = Bruker.objects.create_user("ola@eks.no", "hemmelig-passord")
        self.assertIsNone(bruker.vilkar_godtatt)

    def test_vanlig_bruker_er_ikke_stab(self):
        bruker = Bruker.objects.create_user("ola@eks.no", "hemmelig-passord")
        self.assertFalse(bruker.is_staff)
        self.assertFalse(bruker.is_superuser)

    def test_create_user_uten_epost_gir_feil(self):
        with self.assertRaises(ValueError):
            Bruker.objects.create_user("", "hemmelig-passord")

    def test_samme_epost_med_andre_bokstaver_gir_integrityerror(self):
        Bruker.objects.create_user("ola@eks.no", "hemmelig-passord")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Bruker.objects.create_user("OLA@eks.NO", "annet-passord")

    def test_create_superuser(self):
        bruker = Bruker.objects.create_superuser("Admin@Eks.no", "hemmelig-passord")
        self.assertEqual(bruker.email, "admin@eks.no")
        self.assertTrue(bruker.is_staff)
        self.assertTrue(bruker.is_superuser)

    def test_create_superuser_krever_stab_og_superbruker(self):
        with self.assertRaises(ValueError):
            Bruker.objects.create_superuser("a@eks.no", "passord-1", is_staff=False)
        with self.assertRaises(ValueError):
            Bruker.objects.create_superuser("b@eks.no", "passord-1", is_superuser=False)

    def test_lagring_gir_sma_bokstaver_ogsa_utenom_manageren(self):
        bruker = Bruker(email="Kari@Eks.no")
        bruker.set_password("hemmelig-passord")
        bruker.save()
        self.assertEqual(bruker.email, "kari@eks.no")

    def test_innlogging_godtar_store_bokstaver_i_epost(self):
        bruker = Bruker.objects.create_user("ola@eks.no", "hemmelig-passord")
        self.assertEqual(
            authenticate(email="OLA@Eks.no", password="hemmelig-passord"), bruker
        )

    def test_validering_ser_epost_med_store_bokstaver_som_duplikat(self):
        Bruker.objects.create_user("ola@eks.no", "hemmelig-passord")
        with self.assertRaises(ValidationError) as feil:
            Bruker(email="OLA@Eks.no", password="x").full_clean()
        self.assertIn("email", feil.exception.error_dict)


class HtmxOmdirigeringTest(TestCase):
    """Spec 2.5: utløpt økt under spørringen på S8 gir `HX-Redirect`, ikke innloggingssiden."""

    HTMX = {"HX-Request": "true"}
    S8 = {**HTMX, "HX-Current-URL": "http://testserver/jobber/1/"}

    def test_utlogget_htmx_post_gir_200_og_hx_redirect_til_innlogging_med_next(self):
        svar = self.client.post("/jobber/1/steg/", headers=self.S8)
        self.assertEqual(svar.status_code, 200)
        self.assertEqual(svar.content, b"")
        self.assertEqual(svar["HX-Redirect"], "/logg-inn/?next=%2Fjobber%2F1%2F")
        self.assertNotIn("Location", svar.headers)

    def test_uten_eller_med_ugyldig_hx_current_url_gis_ingen_next(self):
        for verdi in (None, "https://evil.example/jobber/1/", "//evil", "jobber/1/"):
            with self.subTest(verdi=verdi):
                headers = dict(self.HTMX)
                if verdi is not None:
                    headers["HX-Current-URL"] = verdi
                svar = self.client.post("/jobber/1/steg/", headers=headers)
                self.assertEqual(svar.status_code, 200)
                self.assertEqual(svar["HX-Redirect"], "/logg-inn/")

    def test_utlogget_uten_htmx_gir_vanlig_302(self):
        svar = self.client.get("/jobber/1/")
        self.assertRedirects(
            svar, "/logg-inn/?next=/jobber/1/", fetch_redirect_response=False
        )
        self.assertNotIn("HX-Redirect", svar.headers)
        svar = self.client.post("/jobber/1/steg/")
        self.assertEqual(svar.status_code, 302)
        self.assertNotIn("HX-Redirect", svar.headers)

    def test_htmx_uten_godtatte_vilkar_gir_hx_redirect_til_vilkar(self):
        bruker = Bruker.objects.create_user("ola@eks.no", "hemmelig-passord")
        self.client.force_login(bruker)
        svar = self.client.post("/jobber/1/steg/", headers=self.S8)
        self.assertEqual(svar.status_code, 200)
        self.assertEqual(svar.content, b"")
        self.assertEqual(svar["HX-Redirect"], "/vilkar/?next=%2Fjobber%2F1%2F")
        svar = self.client.post("/jobber/1/steg/", headers=self.HTMX)
        self.assertEqual(svar["HX-Redirect"], "/vilkar/")
        # Uten HTMX som før.
        svar = self.client.get("/jobber/1/")
        self.assertRedirects(
            svar, "/vilkar/?next=%2Fjobber%2F1%2F", fetch_redirect_response=False
        )

    def test_andre_omdirigeringer_endres_ikke(self):
        bruker = Bruker.objects.create_user("ola@eks.no", "hemmelig-passord")
        bruker.vilkar_godtatt = timezone.now()
        bruker.save(update_fields=["vilkar_godtatt"])
        self.client.force_login(bruker)
        svar = self.client.get("/emner/ny/", headers=self.HTMX)
        self.assertEqual(svar.status_code, 200)
        self.assertNotIn("HX-Redirect", svar.headers)
        svar = self.client.post(
            "/emner/ny/", {"navn": "Webutvikling"}, headers=self.HTMX
        )
        self.assertEqual(svar.status_code, 302)
        self.assertNotIn("HX-Redirect", svar.headers)

    def test_mellomvaren_ligger_for_login_required(self):
        mellomvare = settings.MIDDLEWARE
        self.assertLess(
            mellomvare.index("kontoer.middleware.HtmxOmdirigeringMiddleware"),
            mellomvare.index("django.contrib.auth.middleware.LoginRequiredMiddleware"),
        )
