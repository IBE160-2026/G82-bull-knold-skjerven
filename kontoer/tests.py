from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

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
