import importlib
import os
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings

import farequiz.settings as innstillinger
import ki
from farequiz.testrunner import TestmodusRunner

ENV_NAVN = (
    "SECRET_KEY",
    "DEBUG",
    "ALLOWED_HOSTS",
    "TESTMODUS",
    "ANTHROPIC_API_KEY",
    "KI_MODELL",
)


def last_innstillinger(**env):
    """Kjører settings.py på nytt med gitt miljø. Tomme verdier overstyrer `.env`."""
    miljo = {navn: "" for navn in ENV_NAVN} | env
    try:
        with mock.patch.dict(os.environ, miljo):
            return vars(importlib.reload(innstillinger)).copy()
    finally:
        # Gjenopprett modulen med det ekte miljøet.
        importlib.reload(innstillinger)


class StandardverdierTest(SimpleTestCase):
    def test_uten_env_gjelder_standardverdiene(self):
        verdier = last_innstillinger()
        self.assertIs(verdier["DEBUG"], True)
        self.assertIn("insecure", verdier["SECRET_KEY"])
        self.assertEqual(verdier["ALLOWED_HOSTS"], ["localhost", "127.0.0.1"])
        self.assertEqual(verdier["KI_MODELL"], "claude-sonnet-5-5")
        self.assertEqual(verdier["ANTHROPIC_API_KEY"], "")
        with (
            mock.patch.object(ki, "_tvunget", False),
            override_settings(
                TESTMODUS=verdier["TESTMODUS"],
                ANTHROPIC_API_KEY=verdier["ANTHROPIC_API_KEY"],
            ),
        ):
            self.assertTrue(ki.er_testmodus())

    def test_env_overstyrer_standardverdiene(self):
        verdier = last_innstillinger(
            DEBUG="False", ALLOWED_HOSTS="localhost, 192.168.1.10", SECRET_KEY="x"
        )
        self.assertIs(verdier["DEBUG"], False)
        self.assertEqual(verdier["ALLOWED_HOSTS"], ["localhost", "192.168.1.10"])
        self.assertEqual(verdier["SECRET_KEY"], "x")

    def test_faste_innstillinger(self):
        self.assertNotIn("django.contrib.admin", settings.INSTALLED_APPS)
        self.assertIn(
            "django.contrib.auth.middleware.LoginRequiredMiddleware",
            settings.MIDDLEWARE,
        )
        self.assertEqual(settings.AUTH_USER_MODEL, "kontoer.Bruker")
        self.assertFalse(settings.DATABASES["default"]["ATOMIC_REQUESTS"])
        self.assertEqual(
            settings.DATABASES["default"]["OPTIONS"],
            {"transaction_mode": "IMMEDIATE", "timeout": 20},
        )
        self.assertEqual(settings.TIME_ZONE, "Europe/Oslo")
        self.assertEqual(settings.LANGUAGE_CODE, "nb")
        self.assertTrue(settings.USE_TZ)


class UrlTest(TestCase):
    def test_admin_finnes_ikke(self):
        self.assertEqual(self.client.get("/admin/").status_code, 404)


class TestmodusRunnerTaggTest(SimpleTestCase):
    """Nettlesertestene kjøres bare med `--tag nettleser`."""

    def test_nettleser_er_utelatt_som_standard(self):
        self.assertIn("nettleser", TestmodusRunner().exclude_tags)

    def test_nettleser_er_med_med_tag(self):
        self.assertNotIn("nettleser", TestmodusRunner(tags=["nettleser"]).exclude_tags)
