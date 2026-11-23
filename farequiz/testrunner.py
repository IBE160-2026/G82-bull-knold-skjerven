"""Testkjører som alltid tvinger testmodus på (AD-12)."""

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


class TestmodusRunner(DiscoverRunner):
    parallel_test_suite = TestmodusParallelSuite

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        _forbered_testprosess()
