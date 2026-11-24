"""Tester for `studier.services.vilkar` (AD-1, AD-23)."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from studier.services.vilkar import godta_vilkar


class GodtaVilkarTest(TestCase):
    def setUp(self):
        self.bruker = get_user_model().objects.create_user("ola@eks.no", "hemmelig123")

    def test_setter_tidspunktet(self):
        for_ = timezone.now()
        godta_vilkar(self.bruker)
        self.bruker.refresh_from_db()
        self.assertGreaterEqual(self.bruker.vilkar_godtatt, for_)

    def test_overskriver_ikke_et_tidspunkt_som_finnes(self):
        tidligere = timezone.now() - timedelta(days=1)
        self.bruker.vilkar_godtatt = tidligere
        self.bruker.save(update_fields=["vilkar_godtatt"])
        godta_vilkar(self.bruker)
        self.bruker.refresh_from_db()
        self.assertEqual(self.bruker.vilkar_godtatt, tidligere)

    def test_utdatert_objekt_overskriver_ikke(self):
        # En annen forespørsel har alt godtatt, men objektet i minnet vet det ikke.
        tidligere = timezone.now() - timedelta(days=1)
        type(self.bruker).objects.filter(pk=self.bruker.pk).update(
            vilkar_godtatt=tidligere
        )
        godta_vilkar(self.bruker)
        self.assertEqual(self.bruker.vilkar_godtatt, tidligere)
        self.bruker.refresh_from_db()
        self.assertEqual(self.bruker.vilkar_godtatt, tidligere)
