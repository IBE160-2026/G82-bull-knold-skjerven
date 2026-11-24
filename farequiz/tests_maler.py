"""Tester for toppfelt, brødsmuler, testmodus-banner, fotlinje og 404 i story 1.3."""

import re

from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.test import TestCase, override_settings
from django.urls import path
from django.utils import timezone

from farequiz.urls import urlpatterns as farequiz_urlpatterns

Bruker = get_user_model()


def _underside(request, pk):
    """Testside for en underside med Tilbake til Oversikt. Emnesiden lages i story 1.4."""
    return render(
        request,
        "startside.html",
        {
            "tilbake_url": "/",
            "tilbake_tekst": "Tilbake til Oversikt",
            "brodsmuler_oversikt": [
                {"tekst": "Oversikt", "url": "/"},
                {"tekst": f"Emne {pk}"},
            ],
        },
    )


urlpatterns = [*farequiz_urlpatterns, path("emner/<int:pk>/", _underside)]


def lag_bruker(email="ola@eks.no"):
    bruker = Bruker.objects.create_user(email, "hemmelig123")
    bruker.vilkar_godtatt = timezone.now()
    bruker.save(update_fields=["vilkar_godtatt"])
    return bruker


class ToppfeltTest(TestCase):
    def test_utlogget_har_ingen_logg_ut_tilbake_eller_meny(self):
        html = self.client.get("/logg-inn/").content.decode()
        self.assertNotIn("Logg ut", html)
        self.assertNotIn("‹ Tilbake", html)
        self.assertNotIn('aria-label="Hovedmeny"', html)

    def test_innlogget_pa_oversikt_har_logg_ut_og_meny_men_ikke_tilbake(self):
        self.client.force_login(lag_bruker())
        html = self.client.get("/").content.decode()
        self.assertIn("Logg ut", html)
        self.assertIn('aria-label="Hovedmeny"', html)
        self.assertNotIn("‹ Tilbake", html)

    def test_hopp_til_innhold_er_forste_lenke_og_peker_pa_main(self):
        html = self.client.get("/logg-inn/").content.decode()
        forste_lenke = re.search(r"<a href=\"#innhold\"", html)
        self.assertIsNotNone(forste_lenke)
        self.assertIn('<main id="innhold"', html)
        self.assertLess(forste_lenke.start(), html.index("<header"))

    def test_meny_har_riktige_lenker_og_ikke_ovp_pa_feil(self):
        self.client.force_login(lag_bruker())
        html = self.client.get("/").content.decode()
        meny = html[html.index('aria-label="Hovedmeny"') :]
        meny = meny[: meny.index("</nav>")]
        self.assertIn("Oversikt", meny)
        self.assertIn("Nytt emne", meny)
        self.assertIn("Personvernerklæring", meny)
        self.assertNotIn("Øv på feil", meny)


@override_settings(ROOT_URLCONF=__name__)
class UndersideTest(TestCase):
    def test_underside_har_tilbake_til_forelderen_og_brodsmuler_med_lenke(self):
        self.client.force_login(lag_bruker())
        html = self.client.get("/emner/3/").content.decode()
        self.assertIn('href="/" class="inline-flex', html)
        self.assertIn('aria-label="Tilbake til Oversikt"', html)
        self.assertIn('<a href="/" class="underline">Oversikt</a>', html)
        self.assertIn('<span aria-current="page">Emne 3</span>', html)


class TilbakeTest(TestCase):
    def test_tilbake_vises_nar_forelderen_er_satt(self):
        from django.template import loader

        html = loader.get_template("partials/topbar.html").render(
            {
                "user": lag_bruker(),
                "tilbake_url": "/",
                "tilbake_tekst": "Tilbake til Oversikt",
            }
        )
        self.assertIn("‹ Tilbake", html)
        self.assertIn('aria-label="Tilbake til Oversikt"', html)


class BrodsmulerTest(TestCase):
    def test_oversikt_viser_brodsmule_som_gjeldende_side(self):
        self.client.force_login(lag_bruker())
        html = self.client.get("/").content.decode()
        self.assertIn('aria-label="Brødsmuler"', html)
        self.assertIn('<span aria-current="page">Oversikt</span>', html)


class TestmodusBannerTest(TestCase):
    def test_banner_vises_i_testmodus_pa_alle_sider(self):
        html = self.client.get("/logg-inn/").content.decode()
        self.assertIn("Testmodus: quizene bruker mock-svar, ingen KI kalles.", html)
        self.assertLess(html.index("Testmodus:"), html.index("<main"))


class FotlinjeTest(TestCase):
    def test_fotlinje_har_opphavsrett_og_lenke_til_personvern(self):
        html = self.client.get("/logg-inn/").content.decode()
        footer = html[html.index("<footer") : html.index("</footer>")]
        self.assertIn("opphavsrettslig beskyttet", footer)
        self.assertIn('href="/personvern/"', footer)


class FantIkkeSideTest(TestCase):
    def test_ukjent_side_gir_404_med_lenke_til_oversikt(self):
        response = self.client.get("/finnes-ikke/")
        self.assertEqual(response.status_code, 404)
        html = response.content.decode()
        self.assertIn("<h1", html)
        self.assertIn("Fant ikke siden", html)
        self.assertIn('href="/"', html)
