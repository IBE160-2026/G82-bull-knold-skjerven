"""Tester for feil, timeout og «Prøv igjen» (FR-13, FR-15, TF-4), én per rad i I/O-matrisen i spec 2.5.

Raden for serverfeil og nettfeil kontrolleres i nettleser. Radene for utløpt økt
og uten HTMX står i kontoer/tests.py.
"""

import re
import socket
from datetime import timedelta
from unittest import mock

import anthropic
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone

import ki
from farequiz import feilmeldinger
from ki import generering as ki_generering
from ki.tests_generering import FalskKlient, statusfeil
from studier.models import Emne, Feilkode, Genereringsjobb, Jobbstatus, Notat, Quiz
from studier.services.emner import slett_emne
from studier.services.generering import opprett_jobb
from studier.services.notater import last_opp
from studier.tests.fabrikk import lag_bruker
from studier.tests.test_generering import FILINNHOLD, GenereringTestCase
from studier.tests.test_slett_emne import _innlogget

KODER = tuple(Feilkode.values)
HTMX = {"HX-Request": "true"}


def _varsel(tekst):
    return f'<p role="alert" class="mb-2 font-semibold text-error">{tekst}</p>'


class FeilTestCase(GenereringTestCase):
    def _steg(self, jobb, **data):
        return self.client.post(f"/jobber/{jobb.pk}/steg/", data, headers=HTMX)

    def _kjor_til_slutt(self, jobb, maks=5):
        """Kaller /steg/ som HTMX til jobben er ferdig eller feilet. Gir siste svar."""
        for _ in range(maks):
            svar = self._steg(jobb)
            jobb.refresh_from_db()
            if jobb.status in (Jobbstatus.FERDIG, Jobbstatus.FEILET):
                return svar
        self.fail(f"Jobben ble ikke ferdig, status {jobb.status}.")

    def assertProvIgjen(self, html, jobb):
        """«Prøv igjen» med autofocus i et vanlig POST-skjema mot S7 med jobbens valg."""
        skjema = re.search(
            rf'<form method="post" action="/notater/{jobb.notat_id}/"[^>]*>(.*?)</form>',
            html,
            re.DOTALL,
        )
        self.assertIsNotNone(skjema, "Fant ikke skjemaet for «Prøv igjen».")
        innhold = skjema.group(1)
        self.assertIn('name="csrfmiddlewaretoken"', innhold)
        self.assertIn(
            '<input type="hidden" name="vanskelighetsgrad" '
            f'value="{jobb.vanskelighetsgrad}">',
            innhold,
        )
        self.assertIn(
            f'<input type="hidden" name="antall" value="{jobb.antall}">', innhold
        )
        self.assertRegex(
            innhold, r'<button type="submit" autofocus[^>]*>Prøv igjen</button>'
        )
        self.assertIn(
            f'<a href="/notater/{jobb.notat_id}/" class="underline">'
            "Tilbake til notatet</a>",
            html,
        )
        self.assertNotIn("hx-post", html)
        self.assertNotIn('aria-disabled="true"', html)
        self.assertNotIn("Dette kan ta opptil to minutter", html)

    def assertFeilside(self, html, jobb, kode):
        self.assertIn(_varsel(feilmeldinger.GENERERING_FEIL[kode]), html)
        self.assertNotIn('<ol class="flex flex-col gap-2">', html)
        if kode in ("format", "api_feil", "api_nokkel"):
            self.assertIn(feilmeldinger.FIL_ER_LAGRET, html)
        else:
            self.assertNotIn(feilmeldinger.FIL_ER_LAGRET, html)
        self.assertProvIgjen(html, jobb)


class TeksterTest(FeilTestCase):
    def test_en_tekst_per_kode_og_api_feil_for_tom_eller_ukjent(self):
        self.assertEqual(set(feilmeldinger.GENERERING_FEIL), set(Feilkode.values))
        self.assertEqual(
            len(set(feilmeldinger.GENERERING_FEIL.values())), len(Feilkode.values)
        )
        for kode in KODER:
            self.assertEqual(
                feilmeldinger.generering_feilet(kode),
                feilmeldinger.GENERERING_FEIL[kode],
            )
        for kode in ("", None, "ukjent"):
            self.assertEqual(
                feilmeldinger.generering_feilet(kode),
                feilmeldinger.GENERERING_FEIL["api_feil"],
            )
        self.assertFalse(hasattr(feilmeldinger, "GENERERING_FEILET"))


class HverFeilkodeTest(FeilTestCase):
    def test_hver_kode_gir_feilet_tekst_prov_igjen_og_logg(self):
        for kode in KODER:
            with self.subTest(kode=kode):
                Genereringsjobb.objects.all().delete()
                jobb = opprett_jobb(self.notat, "lett", 7)
                with (
                    mock.patch.object(ki, "generer", side_effect=ki.KIFeil(kode)),
                    self.assertLogs("studier.services.generering", "INFO") as logg,
                ):
                    svar = self._kjor_til_slutt(jobb)
                self.assertEqual(jobb.status, Jobbstatus.FEILET)
                self.assertEqual(jobb.feilkode, kode)
                self.assertFalse(Quiz.objects.exists())
                self.assertIn(
                    f"Genereringsjobb {jobb.pk} feilet med koden {kode}.",
                    logg.output[-1],
                )
                self.assertFalse(any(FILINNHOLD in linje for linje in logg.output))

                # HTMX-svaret bytter #fremdrift og #handlinger, og har ingen #spor.
                html = svar.content.decode()
                self.assertEqual(svar.status_code, 200)
                self.assertIn('<div id="fremdrift" hx-swap-oob="innerHTML">', html)
                self.assertIn('<div id="handlinger" hx-swap-oob="innerHTML">', html)
                self.assertNotIn('id="spor"', html)
                self.assertFeilside(html, jobb, kode)

                # S8 (GET) viser det samme, med #handlinger utenfor aria-live.
                side = self.client.get(f"/jobber/{jobb.pk}/").content.decode()
                self.assertFeilside(side, jobb, kode)
                fremdrift = side.index('<div id="fremdrift" aria-live="polite"')
                handlinger = side.index('<div id="handlinger">')
                self.assertLess(
                    side.index(feilmeldinger.GENERERING_FEIL[kode]), handlinger
                )
                self.assertLess(fremdrift, handlinger)
                self.assertLess(handlinger, side.index("Prøv igjen</button>"))
                self.assertNotIn("<noscript>", side)

    def test_s8_laster_fremdrift_js_med_tekst_for_serverfeil(self):
        jobb = opprett_jobb(self.notat, "middels", 10)
        html = self.client.get(f"/jobber/{jobb.pk}/").content.decode()
        self.assertIn(
            f'<div id="fremdrift" aria-live="polite" class="mb-4" '
            f'data-feil-server="{feilmeldinger.INGEN_SERVERKONTAKT}">',
            html,
        )
        self.assertIn('<script src="/static/js/fremdrift.js" defer></script>', html)
        self.assertLess(html.index("js/htmx.min.js"), html.index("js/fremdrift.js"))
        # Mens jobben går, står hjelpeteksten og den låste knappen i #handlinger.
        handlinger = html.index('<div id="handlinger">')
        self.assertLess(handlinger, html.index("Dette kan ta opptil to minutter"))
        self.assertLess(handlinger, html.index('aria-disabled="true"'))
        self.assertNotIn("Prøv igjen", html)
        self.assertIn("<noscript>", html)


class TimeoutVedS8Test(FeilTestCase):
    def test_jobb_eldre_enn_120_s_vises_straks_som_timeout(self):
        jobb = self._jobb(
            status=Jobbstatus.LAGER, startet=timezone.now() - timedelta(seconds=121)
        )
        with (
            mock.patch.object(ki, "generer") as generer,
            self.assertLogs("studier.services.generering", "WARNING") as logg,
        ):
            svar = self.client.get(f"/jobber/{jobb.pk}/")
        generer.assert_not_called()
        self.assertEqual(svar.status_code, 200)
        jobb.refresh_from_db()
        self.assertEqual(jobb.status, Jobbstatus.FEILET)
        self.assertEqual(jobb.feilkode, "timeout")
        self.assertTrue(any(str(jobb.pk) in linje for linje in logg.output))
        html = svar.content.decode()
        self.assertFeilside(html, jobb, "timeout")
        self.assertNotIn('id="spor"', html)


class ProvIgjenTest(FeilTestCase):
    def _skjemadata(self, jobb):
        """Feltene i «Prøv igjen»-skjemaet slik S8 viser dem (uten JavaScript)."""
        html = self.client.get(f"/jobber/{jobb.pk}/").content.decode()
        return dict(
            re.findall(
                r'<input type="hidden" name="(vanskelighetsgrad|antall)" value="([^"]*)">',
                html,
            )
        )

    def test_prov_igjen_lager_ny_jobb_med_samme_valg_og_sender_til_s8(self):
        feilet = self._jobb(
            vanskelighetsgrad="lett",
            antall=7,
            status=Jobbstatus.FEILET,
            feilkode="api_feil",
        )
        data = self._skjemadata(feilet)
        self.assertEqual(data, {"vanskelighetsgrad": "lett", "antall": "7"})
        svar = self.client.post(self.notat_url, data)
        ny = Genereringsjobb.objects.exclude(pk=feilet.pk).get()
        self.assertRedirects(svar, f"/jobber/{ny.pk}/")
        self.assertEqual(ny.status, Jobbstatus.LESER)
        self.assertEqual(ny.vanskelighetsgrad, "lett")
        self.assertEqual(ny.antall, 7)
        self.assertEqual(ny.notat, self.notat)
        self.assertEqual(ny.runde, 1)
        feilet.refresh_from_db()
        self.assertEqual(feilet.status, Jobbstatus.FEILET)

    def test_prov_igjen_med_aktiv_jobb_sender_til_den_aktive(self):
        feilet = self._jobb(
            vanskelighetsgrad="lett",
            antall=7,
            status=Jobbstatus.FEILET,
            feilkode="format",
        )
        data = self._skjemadata(feilet)
        aktiv = self._jobb(vanskelighetsgrad="vanskelig", antall=20)
        svar = self.client.post(self.notat_url, data)
        self.assertRedirects(svar, f"/jobber/{aktiv.pk}/")
        self.assertEqual(Genereringsjobb.objects.count(), 2)


class NotatSlettetTest(FeilTestCase):
    def assertSluttfragment(self, svar):
        self.assertEqual(svar.status_code, 200)
        html = svar.content.decode()
        self.assertIn('<div id="fremdrift" hx-swap-oob="innerHTML">', html)
        self.assertIn(_varsel(feilmeldinger.NOTAT_FINNES_IKKE), html)
        self.assertIn('<a href="/" class="underline">Gå til Oversikt</a>', html)
        self.assertIn('<div id="handlinger" hx-swap-oob="innerHTML"></div>', html)
        self.assertNotIn('id="spor"', html)
        self.assertNotIn("hx-post", html)
        self.assertNotIn("HX-Redirect", svar.headers)
        self.assertFalse(Quiz.objects.exists())

    def test_emnet_slettes_mens_steget_kjorer(self):
        jobb = opprett_jobb(self.notat, "middels", 10)
        self._steg(jobb)  # leser
        kall = []

        def generer(*args, **kwargs):
            kall.append(1)
            slett_emne(Emne.objects.get(pk=self.emne.pk))
            return ki.RaattSvar(
                tekst="{}", forhandslagret=False, modell="m", prompt_versjon="1"
            )

        with mock.patch.object(ki, "generer", side_effect=generer):
            svar = self._steg(jobb)
            # Et nytt kall etter sluttfragmentet gir det samme, uten nytt KI-kall.
            igjen = self._steg(jobb)
        self.assertEqual(kall, [1])
        self.assertFalse(Genereringsjobb.objects.exists())
        self.assertFalse(Notat.objects.exists())
        self.assertSluttfragment(svar)
        self.assertSluttfragment(igjen)

    def test_emnet_slettes_mellom_kall(self):
        jobb = opprett_jobb(self.notat, "middels", 10)
        self._steg(jobb)  # leser
        slett_emne(self.emne)
        with mock.patch.object(ki, "les_fil") as les_fil:
            svar = self._steg(jobb, vist="lager")
        les_fil.assert_not_called()
        self.assertSluttfragment(svar)

    def test_jobb_som_aldri_fantes_gir_sluttfragment(self):
        with mock.patch.object(ki, "les_fil") as les_fil:
            svar = self.client.post("/jobber/999999/steg/", headers=HTMX)
        les_fil.assert_not_called()
        self.assertSluttfragment(svar)


class AnnensJobbTest(FeilTestCase):
    def test_annens_jobb_gir_404_ved_steg_og_s8(self):
        annen = _innlogget(lag_bruker("annen@eks.no"))
        annens_emne = Emne.objects.create(eier=annen, navn="Annet")
        annens_notat = last_opp(
            annens_emne, SimpleUploadedFile("hemmelig.txt", b"Hemmelig."), annen
        )
        aktiv = opprett_jobb(annens_notat, "middels", 10)
        gammel = Genereringsjobb.objects.create(
            notat=annens_notat,
            vanskelighetsgrad="lett",
            antall=5,
            startet=timezone.now() - timedelta(seconds=121),
        )
        Genereringsjobb.objects.filter(pk=aktiv.pk).update(
            startet=timezone.now() - timedelta(seconds=10)
        )
        with mock.patch.object(ki, "les_fil") as les_fil:
            for jobb in (aktiv, gammel):
                with self.subTest(jobb=jobb.pk):
                    self.assertEqual(self._steg(jobb).status_code, 404)
                    svar = self.client.get(f"/jobber/{jobb.pk}/")
                    self.assertEqual(svar.status_code, 404)
        les_fil.assert_not_called()
        # Fristen sjekkes ikke for andres jobber via S8.
        gammel.refresh_from_db()
        self.assertEqual(gammel.status, Jobbstatus.LESER)
        aktiv.refresh_from_db()
        self.assertEqual(aktiv.status, Jobbstatus.LESER)
        self.assertIs(aktiv.i_gang, False)


class KortTxtTest(FeilTestCase):
    def test_ekte_opplasting_av_kort_txt_gir_teksten_for_for_lite_innhold(self):
        svar = self.client.post(
            f"/emner/{self.emne.pk}/last-opp/",
            {"fil": SimpleUploadedFile("kort.txt", b"Hei.")},
        )
        notat = Notat.objects.get(originalnavn="kort.txt")
        self.assertRedirects(svar, f"/notater/{notat.pk}/")
        svar = self.client.post(
            f"/notater/{notat.pk}/", {"vanskelighetsgrad": "middels", "antall": "10"}
        )
        jobb = Genereringsjobb.objects.get(notat=notat)
        self.assertRedirects(svar, f"/jobber/{jobb.pk}/")
        with (
            mock.patch.object(ki, "generer", side_effect=ki.KIFeil("for_lite_innhold")),
            self.assertLogs("studier.services.generering", "WARNING"),
        ):
            svar = self._kjor_til_slutt(jobb)
        self.assertEqual(jobb.feilkode, "for_lite_innhold")
        html = svar.content.decode()
        self.assertFeilside(html, jobb, "for_lite_innhold")


@mock.patch.object(ki, "_tvunget", False)
@override_settings(TESTMODUS="0", ANTHROPIC_API_KEY="sk-ant-test")
class UgyldigNokkelTest(FeilTestCase):
    def test_authentication_error_gir_api_nokkel_uten_nettverkskall(self):
        self.assertIs(ki.er_testmodus(), False)
        klient = FalskKlient(feil=statusfeil(anthropic.AuthenticationError, 401))
        jobb = opprett_jobb(self.notat, "middels", 10)
        with (
            mock.patch.object(ki_generering, "_klient", return_value=klient) as lag,
            mock.patch.object(
                socket.socket, "connect", side_effect=AssertionError("nettverkskall")
            ) as connect,
            self.assertLogs("studier.services.generering", "WARNING"),
        ):
            svar = self._kjor_til_slutt(jobb)
        lag.assert_called_once()
        connect.assert_not_called()
        self.assertEqual(jobb.status, Jobbstatus.FEILET)
        self.assertEqual(jobb.feilkode, "api_nokkel")
        self.assertFalse(Quiz.objects.exists())
        self.assertFeilside(svar.content.decode(), jobb, "api_nokkel")
