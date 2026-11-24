"""Tester for sidene i story 1.2: én test per rad i I/O-matrisen i spec-en."""

import re
from unittest import mock

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings
from django.urls import path
from django.utils import timezone

from farequiz import feilmeldinger
from farequiz.urls import urlpatterns as farequiz_urlpatterns
from kontoer.forms import RegistrerForm
from kontoer.middleware import VilkarMiddleware


def _beskyttet(request, pk):
    return HttpResponse(f"emne {pk}")


# En beskyttet side i tillegg til de ekte, slik at «utløpt økt» kan testes med
# `/testside/3/` før story 1.4 lager emnesidene.
urlpatterns = [
    *farequiz_urlpatterns,
    path("testside/<int:pk>/", _beskyttet),
]

Bruker = get_user_model()
PASSORD = "hemmelig123"


def lag_bruker(email="ola@eks.no", godtatt=True):
    bruker = Bruker.objects.create_user(email, PASSORD)
    if godtatt:
        bruker.vilkar_godtatt = timezone.now()
        bruker.save(update_fields=["vilkar_godtatt"])
    return bruker


@override_settings(ROOT_URLCONF=__name__)
class RegistrerTest(TestCase):
    url = "/registrer/"

    def test_ny_konto(self):
        svar = self.client.post(self.url, {"email": "Ny@Eks.no", "passord": PASSORD})
        self.assertRedirects(svar, "/", fetch_redirect_response=False)
        bruker = Bruker.objects.get()
        self.assertEqual(bruker.email, "ny@eks.no")
        self.assertNotEqual(bruker.password, PASSORD)
        self.assertTrue(bruker.check_password(PASSORD))
        self.assertEqual(int(self.client.session["_auth_user_id"]), bruker.pk)
        # Startsiden sender videre til S1b, fordi vilkårene ikke er godtatt.
        svar = self.client.get("/")
        self.assertRedirects(svar, "/vilkar/?next=%2F", fetch_redirect_response=False)

    def test_brukt_epost(self):
        lag_bruker("ola@eks.no")
        svar = self.client.post(self.url, {"email": "Ola@Eks.no", "passord": PASSORD})
        self.assertEqual(svar.status_code, 200)
        self.assertContains(svar, feilmeldinger.EPOST_FINNES)
        self.assertContains(svar, 'value="Ola@Eks.no"')
        self.assertEqual(Bruker.objects.count(), 1)

    def test_ugyldig_epost(self):
        svar = self.client.post(self.url, {"email": "ikke-epost", "passord": PASSORD})
        self.assertContains(svar, feilmeldinger.UGYLDIG_EPOST)
        self.assertContains(svar, 'value="ikke-epost"')
        self.assertFalse(Bruker.objects.exists())

    def test_for_kort_passord(self):
        svar = self.client.post(self.url, {"email": "ny@eks.no", "passord": "kort123"})
        self.assertContains(svar, feilmeldinger.FOR_KORT_PASSORD)
        self.assertContains(svar, 'value="ny@eks.no"')
        self.assertFalse(Bruker.objects.exists())

    def test_vanlig_passord_godtas(self):
        # Bare minst 8 tegn (beslutning 23.11), så et vanlig passord er lov.
        svar = self.client.post(self.url, {"email": "ny@eks.no", "passord": "12345678"})
        self.assertEqual(svar.status_code, 302)
        self.assertTrue(Bruker.objects.exists())

    def test_feilmelding_over_skjemaet_med_fokus(self):
        svar = self.client.post(self.url, {"email": "ikke-epost", "passord": "kort"})
        html = svar.content.decode()
        self.assertIn('role="alert"', html)
        self.assertIn('tabindex="-1" autofocus', html)
        self.assertLess(html.index('role="alert"'), html.index("<form"))
        self.assertIn('aria-describedby="feil-epost hint-epost"', html)

    def test_samtidig_registrering_gir_epost_finnes(self):
        # To registreringer med samme e-post samtidig: databasen avviser den ene.
        with mock.patch.object(RegistrerForm, "lagre", side_effect=IntegrityError):
            svar = self.client.post(
                self.url, {"email": "ny@eks.no", "passord": PASSORD}
            )
        self.assertEqual(svar.status_code, 200)
        self.assertContains(svar, feilmeldinger.EPOST_FINNES)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_tom_post_gir_feilmeldinger(self):
        svar = self.client.post(self.url, {})
        self.assertEqual(svar.status_code, 200)
        self.assertContains(svar, feilmeldinger.UGYLDIG_EPOST)
        self.assertContains(svar, feilmeldinger.FOR_KORT_PASSORD)
        self.assertFalse(Bruker.objects.exists())

    def test_innlogget_bruker_sendes_til_startsiden(self):
        self.client.force_login(lag_bruker())
        svar = self.client.get(self.url)
        self.assertRedirects(svar, "/", fetch_redirect_response=False)
        svar = self.client.post(self.url, {"email": "andre@eks.no", "passord": PASSORD})
        self.assertRedirects(svar, "/", fetch_redirect_response=False)
        self.assertEqual(Bruker.objects.count(), 1)


@override_settings(ROOT_URLCONF=__name__)
class LoggInnTest(TestCase):
    url = "/logg-inn/"

    def setUp(self):
        self.bruker = lag_bruker()

    def test_innlogging_uten_neste(self):
        svar = self.client.post(
            self.url, {"username": "OLA@eks.no", "password": PASSORD}
        )
        self.assertRedirects(svar, "/", fetch_redirect_response=False)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.bruker.pk)

    def test_innlogging_med_neste(self):
        svar = self.client.post(
            self.url,
            {"username": "ola@eks.no", "password": PASSORD, "next": "/testside/3/"},
        )
        self.assertRedirects(svar, "/testside/3/", fetch_redirect_response=False)

    def test_usikker_neste_folges_ikke(self):
        svar = self.client.post(
            self.url,
            {"username": "ola@eks.no", "password": PASSORD, "next": "https://ond.no/"},
        )
        self.assertRedirects(svar, "/", fetch_redirect_response=False)

    def test_feil_passord_og_ukjent_epost_gir_samme_melding(self):
        feil_passord = self.client.post(
            self.url, {"username": "ola@eks.no", "password": "feil-passord"}
        )
        ukjent = self.client.post(
            self.url, {"username": "ingen@eks.no", "password": PASSORD}
        )
        for svar in (feil_passord, ukjent):
            self.assertEqual(svar.status_code, 200)
            self.assertContains(svar, feilmeldinger.FEIL_INNLOGGING, count=1)
            self.assertNotIn("_auth_user_id", self.client.session)

    def test_utlopt_okt(self):
        svar = self.client.get("/testside/3/")
        self.assertRedirects(
            svar, "/logg-inn/?next=/testside/3/", fetch_redirect_response=False
        )
        side = self.client.get(svar.url)
        self.assertContains(side, feilmeldinger.OKT_UTLOPT)
        svar = self.client.post(
            "/logg-inn/",
            {"username": "ola@eks.no", "password": PASSORD, "next": "/testside/3/"},
        )
        self.assertRedirects(svar, "/testside/3/", fetch_redirect_response=False)
        self.assertContains(self.client.get("/testside/3/"), "emne 3")

    def test_ny_besokende_paa_startsiden_far_ingen_melding(self):
        svar = self.client.get("/", follow=True)
        self.assertEqual(svar.request["PATH_INFO"], "/logg-inn/")
        self.assertNotContains(svar, feilmeldinger.OKT_UTLOPT)

    def test_neste_til_utlogging_folges_ikke(self):
        side = self.client.get("/logg-inn/?next=/logg-ut/")
        self.assertNotContains(side, feilmeldinger.OKT_UTLOPT)
        self.assertNotContains(side, 'name="next"')
        for neste in (
            "/logg-ut/",
            "/logg-ut/?x=1",
            "/logg-ut",
            "http://testserver/logg-ut/",
        ):
            with self.subTest(neste=neste):
                self.client.logout()
                svar = self.client.post(
                    self.url,
                    {"username": "ola@eks.no", "password": PASSORD, "next": neste},
                )
                self.assertRedirects(svar, "/", fetch_redirect_response=False)

    def test_utlopt_melding_ogsa_etter_feil_innlogging(self):
        svar = self.client.post(
            self.url,
            {
                "username": "ola@eks.no",
                "password": "feil-passord",
                "next": "/testside/3/",
            },
        )
        self.assertContains(svar, feilmeldinger.FEIL_INNLOGGING)
        self.assertContains(svar, feilmeldinger.OKT_UTLOPT)
        self.assertContains(svar, 'name="next" value="/testside/3/"')

    def test_innlogget_bruker_sendes_fra_innloggingen(self):
        self.client.force_login(self.bruker)
        svar = self.client.get(self.url)
        self.assertRedirects(svar, "/", fetch_redirect_response=False)


@override_settings(ROOT_URLCONF=__name__)
class VilkarTest(TestCase):
    def setUp(self):
        self.bruker = lag_bruker(godtatt=False)
        self.client.force_login(self.bruker)

    def test_vilkar_mangler_sender_til_s1b(self):
        svar = self.client.get("/testside/3/?side=2")
        self.assertRedirects(
            svar,
            "/vilkar/?next=%2Ftestside%2F3%2F%3Fside%3D2",
            fetch_redirect_response=False,
        )

    def test_unntatte_sider(self):
        self.assertEqual(self.client.get("/vilkar/").status_code, 200)
        self.assertEqual(self.client.get("/personvern/").status_code, 200)
        # Statiske filer slippes gjennom mellomvaren uten sending til `/vilkar/`.
        foresporsel = RequestFactory().get("/static/css/app.css")
        foresporsel.user = self.bruker
        mellomvare = VilkarMiddleware(lambda request: HttpResponse())
        self.assertIsNone(
            mellomvare.process_view(foresporsel, _beskyttet, (), {"pk": 1})
        )
        # En vanlig side gir derimot en sending.
        foresporsel = RequestFactory().get("/emner/1/")
        foresporsel.user = self.bruker
        self.assertEqual(
            mellomvare.process_view(foresporsel, _beskyttet, (), {"pk": 1}).status_code,
            302,
        )
        svar = self.client.post("/logg-ut/")
        self.assertRedirects(svar, "/logg-inn/", fetch_redirect_response=False)

    def test_godta(self):
        for_ = timezone.now()
        svar = self.client.post("/vilkar/", {"next": "/testside/3/"})
        self.assertRedirects(svar, "/testside/3/", fetch_redirect_response=False)
        self.bruker.refresh_from_db()
        self.assertIsNotNone(self.bruker.vilkar_godtatt)
        self.assertGreaterEqual(self.bruker.vilkar_godtatt, for_)
        # S1b vises ikke igjen.
        self.assertRedirects(
            self.client.get("/vilkar/"), "/", fetch_redirect_response=False
        )
        self.assertContains(self.client.get("/testside/3/"), "emne 3")

    def test_godta_uten_neste(self):
        svar = self.client.post("/vilkar/")
        self.assertRedirects(svar, "/", fetch_redirect_response=False)

    def test_godta_med_usikker_neste(self):
        svar = self.client.post("/vilkar/", {"next": "https://ond.no/"})
        self.assertRedirects(svar, "/", fetch_redirect_response=False)

    def test_s1b_innhold(self):
        svar = self.client.get("/vilkar/?next=/testside/3/")
        for tekst in (
            "Behandling av notater:",
            "Ikke del personopplysninger:",
            "KI-generert innhold:",
            "Vilkår og loggføring:",
            "Jeg har forstått og godtar",
            'href="/personvern/"',
            'name="next" value="/testside/3/"',
            'method="post"',
        ):
            self.assertContains(svar, tekst)
        self.assertNotContains(svar, "<script")

    def test_godta_med_neste_til_utlogging(self):
        svar = self.client.post("/vilkar/", {"next": "/logg-ut/"})
        self.assertRedirects(svar, "/", fetch_redirect_response=False)

    def test_post_uten_vilkar_sendes_uten_neste(self):
        # En POST kan ikke gjentas med GET, så den får ingen `next`.
        svar = self.client.post("/testside/3/")
        self.assertRedirects(svar, "/vilkar/", fetch_redirect_response=False)


@override_settings(ROOT_URLCONF=__name__)
class UtloggingTest(TestCase):
    def setUp(self):
        self.client.force_login(lag_bruker())

    def test_post_logger_ut(self):
        svar = self.client.post("/logg-ut/")
        self.assertRedirects(svar, "/logg-inn/", fetch_redirect_response=False)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_get_gir_405(self):
        self.assertEqual(self.client.get("/logg-ut/").status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)


@override_settings(ROOT_URLCONF=__name__)
class OffentligeSiderTest(TestCase):
    def test_personvern_uten_innlogging(self):
        svar = self.client.get("/personvern/")
        self.assertEqual(svar.status_code, 200)
        self.assertContains(svar, "Ola Normann")
        self.assertContains(svar, "ola@normann.no")
        self.assertContains(svar, "Sist oppdatert: 23.11.2026")
        self.assertNotContains(svar, "[")

    def test_bare_tre_sider_er_offentlige(self):
        for sti in ("/logg-inn/", "/registrer/", "/personvern/"):
            self.assertEqual(self.client.get(sti).status_code, 200, sti)
        for sti in ("/", "/vilkar/", "/testside/3/"):
            self.assertEqual(self.client.get(sti).status_code, 302, sti)

    def test_s1_innhold(self):
        svar = self.client.get("/logg-inn/")
        html = svar.content.decode()
        for tekst in (
            "Øv på forelesningene dine",
            "Registrer deg",
            "Last opp notatet",
            "Ta quizen",
            "Øv på feilene",
            "Logg inn",
            'href="/registrer/"',
            'href="/personvern/"',
            'autocomplete="email"',
            'autocomplete="current-password"',
        ):
            self.assertIn(tekst, html)
        self.assertRegex(html, r'aria-hidden="true">\s*<div>Hva er HTML\?</div>')
        self.assertNotIn("Logg ut", html)

    def test_registrer_felter(self):
        html = self.client.get("/registrer/").content.decode()
        self.assertIn('autocomplete="email"', html)
        self.assertIn('autocomplete="new-password"', html)
        self.assertNotIn("onpaste", html)


@override_settings(ROOT_URLCONF=__name__)
class SidestrukturTest(TestCase):
    def test_en_h1_main_lang_og_tittel(self):
        bruker = lag_bruker("godtatt@eks.no")
        ny = lag_bruker("ny@eks.no", godtatt=False)
        sider = [
            (None, "/logg-inn/", "Logg inn – FåreQuiz"),
            (None, "/registrer/", "Registrer deg – FåreQuiz"),
            (None, "/personvern/", "Personvernerklæring – FåreQuiz"),
            (ny, "/vilkar/", "Før du tar i bruk tjenesten – FåreQuiz"),
            (bruker, "/", "Oversikt – FåreQuiz"),
        ]
        for innlogget, sti, tittel in sider:
            with self.subTest(sti=sti):
                self.client.logout()
                if innlogget:
                    self.client.force_login(innlogget)
                html = self.client.get(sti).content.decode()
                self.assertEqual(len(re.findall(r"<h1[\s>]", html)), 1)
                self.assertEqual(html.count("<main"), 1)
                self.assertIn('<html lang="nb">', html)
                self.assertIn(f"<title>{tittel}</title>", html)
