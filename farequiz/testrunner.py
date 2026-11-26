"""Testkjører som alltid tvinger testmodus på (AD-12)."""

import sys

from django.conf import settings
from django.test.runner import DiscoverRunner, ParallelTestSuite

import ki


def _forbered_testprosess():
    """Testmodus på og rask hashing i tester. Produksjonsoppsettet er uendret."""
    from django.contrib.auth.hashers import get_hashers

    ki.tving_testmodus()
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
    get_hashers.cache_clear()


class TestmodusParallelSuite(ParallelTestSuite):
    """Gjør det samme i arbeidsprosessene ved `--parallel`."""

    def process_setup(*args):
        _forbered_testprosess()


NETTLESER = "nettleser"


class TestmodusRunner(DiscoverRunner):
    """Utelater nettlesertestene (taggen `nettleser`) med mindre `--tag nettleser` er gitt.

    Da kan `manage.py test` kjøres uten Playwright og Chromium.
    """

    parallel_test_suite = TestmodusParallelSuite

    def __init__(self, *args, tags=None, exclude_tags=None, **kwargs):
        self.nettleser_utelatt = NETTLESER not in (tags or ())
        if self.nettleser_utelatt:
            exclude_tags = {*(exclude_tags or ()), NETTLESER}
        super().__init__(*args, tags=tags, exclude_tags=exclude_tags, **kwargs)

    def build_suite(self, test_labels=None, **kwargs):
        # Med egne testnavn kan det se ut som nettlesertesten kjørte, når den ble utelatt.
        if self.nettleser_utelatt and test_labels:
            sys.stderr.write(
                "Nettlesertestene er utelatt. Kjør med `--tag nettleser` for å ta dem med.\n"
            )
        return super().build_suite(test_labels, **kwargs)

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        _forbered_testprosess()
