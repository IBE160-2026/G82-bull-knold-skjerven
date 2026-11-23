from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import TestCase

from studier.tests.fabrikk import lag_bruker, lag_kjede
from studier.tilgang import EIERVEI, egne, hent_egen


class TilgangTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ola = lag_bruker("ola@eks.no")
        cls.kari = lag_bruker("kari@eks.no")
        cls.olas = lag_kjede(cls.ola)
        cls.karis = lag_kjede(cls.kari)

    def test_eiervei_dekker_alle_modellene_i_studier(self):
        self.assertEqual(set(EIERVEI), set(apps.get_app_config("studier").get_models()))

    def test_hent_egen_gir_eget_objekt(self):
        for modell, objekt in self.olas.items():
            with self.subTest(modell=modell.__name__):
                self.assertEqual(hent_egen(modell, objekt.pk, self.ola), objekt)

    def test_hent_egen_gir_404_for_andres_rad(self):
        for modell, objekt in self.karis.items():
            with self.subTest(modell=modell.__name__), self.assertRaises(Http404):
                hent_egen(modell, objekt.pk, self.ola)

    def test_hent_egen_gir_404_for_pk_som_ikke_finnes(self):
        for modell in EIERVEI:
            with self.subTest(modell=modell.__name__), self.assertRaises(Http404):
                hent_egen(modell, 999_999, self.ola)

    def test_hent_egen_gir_404_for_ugyldig_pk(self):
        for modell in EIERVEI:
            for pk in ("abc", None, "", "1; DROP"):
                with (
                    self.subTest(modell=modell.__name__, pk=pk),
                    self.assertRaises(Http404),
                ):
                    hent_egen(modell, pk, self.ola)

    def test_egne_gir_bare_brukerens_rader(self):
        for modell in EIERVEI:
            with self.subTest(modell=modell.__name__):
                olas = set(egne(modell, self.ola).values_list("pk", flat=True))
                karis = set(egne(modell, self.kari).values_list("pk", flat=True))
                alle = set(modell.objects.values_list("pk", flat=True))
                self.assertIn(self.olas[modell].pk, olas)
                self.assertIn(self.karis[modell].pk, karis)
                self.assertTrue(olas.isdisjoint(karis))
                self.assertEqual(olas | karis, alle)

    def test_ikke_innlogget_far_ingenting(self):
        anonym = AnonymousUser()
        for modell, objekt in self.olas.items():
            with self.subTest(modell=modell.__name__):
                self.assertFalse(egne(modell, anonym).exists())
                with self.assertRaises(Http404):
                    hent_egen(modell, objekt.pk, anonym)

    def test_ukjent_modell_gir_tydelig_feil(self):
        bruker_modell = get_user_model()
        with self.assertRaisesMessage(ValueError, "Bruker har ingen eiervei"):
            hent_egen(bruker_modell, self.ola.pk, self.ola)
        with self.assertRaisesMessage(ValueError, "EIERVEI"):
            egne(bruker_modell, self.ola)
