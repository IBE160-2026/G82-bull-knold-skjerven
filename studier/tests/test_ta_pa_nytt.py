"""Tester for å ta en quiz på nytt (FR-20, FR-23, AD-6), story 3.4."""

import re
from unittest import mock

from studier.models import Feilbankrad, Hendelse, Okt, Oktstatus, Svar
from studier.services import okter
from studier.services.feilbank import fasit_synlig
from studier.services.okter import lever_okt
from studier.tests.test_levering import LeveringTestCase


class TaPaNyttTestCase(LeveringTestCase):
    def _start_url(self, quiz=None):
        return f"/quizer/{(quiz or self.quiz).pk}/start/"

    def _levert(self, riktige=(), okt=None):
        okt = okt or self.okt
        self._besvar_alle(riktige=riktige, okt=okt)
        self.assertTrue(lever_okt(okt))
        return okt

    def _ta_pa_nytt(self):
        svar = self.client.post(self._start_url())
        ny = Okt.objects.get(quiz=self.quiz, status=Oktstatus.PABEGYNT)
        self.assertRedirects(svar, self._url(ny, 1), fetch_redirect_response=False)
        return ny

    def _kortknapp(self, html, quiz=None):
        """Teksten på knappen i skjemaet til quizkortet."""
        start = html.index(f'action="{self._start_url(quiz)}"')
        knapp = html.index("<button", start)
        return html[html.index(">", knapp) + 1 : html.index("</button>", knapp)]


class QuizkortTest(TaPaNyttTestCase):
    def test_uten_levert_forsok_heter_knappen_ta_quiz(self):
        # setUp har laget et påbegynt forsøk.
        html = self.client.get(self.notat_url).content.decode()
        self.assertEqual(self._kortknapp(html), "Ta quiz")
        self.assertNotIn("Ta på nytt", html)

    def test_med_levert_forsok_heter_knappen_ta_pa_nytt(self):
        self._levert()
        html = self.client.get(self.notat_url).content.decode()
        self.assertEqual(self._kortknapp(html), "Ta på nytt")
        self.assertNotIn(">Ta quiz<", html)

    def test_ta_pa_nytt_ogsa_med_nytt_paabegynt_forsok(self):
        self._levert()
        self._ta_pa_nytt()
        html = self.client.get(self.notat_url).content.decode()
        self.assertEqual(self._kortknapp(html), "Ta på nytt")

    def test_knappen_gjelder_hvert_kort_for_seg(self):
        self._levert()
        annen = self._quiz(self.notat)
        html = self.client.get(self.notat_url).content.decode()
        self.assertEqual(self._kortknapp(html), "Ta på nytt")
        self.assertEqual(self._kortknapp(html, annen), "Ta quiz")
        # Annoteringen dobler ikke antall spørsmål.
        self.assertEqual(html.count("Middels, 5 spørsmål"), 2)


class NyttForsokTest(TaPaNyttTestCase):
    def _tilstand(self, okt):
        okt = Okt.objects.get(pk=okt.pk)
        svar = sorted(okt.svar.values_list("sporsmal_id", "alternativ_id", "hendelse"))
        return (
            okt.status,
            okt.innhold,
            okt.levert_tidspunkt,
            okt.poengsum,
            okt.antall,
            svar,
        )

    def test_nytt_forsok_fra_notatsiden_og_gamle_er_uendret(self):
        gammel = self._levert(riktige={1, 2})
        for_ = self._tilstand(gammel)
        ny = self._ta_pa_nytt()
        self.assertNotEqual(ny.pk, gammel.pk)
        self.assertEqual(ny.status, Oktstatus.PABEGYNT)
        self.assertFalse(ny.svar.exists())
        self.assertEqual(
            [rad["sporsmal"] for rad in ny.innhold],
            [rad["sporsmal"] for rad in gammel.innhold],
        )
        # Nye svar og levering endrer ikke det gamle forsøket.
        self._levert(riktige={1, 2, 3, 4, 5}, okt=ny)
        self.assertEqual(self._tilstand(gammel), for_)
        self.assertEqual(Okt.objects.filter(quiz=self.quiz).count(), 2)

    def test_alternativene_stokkes_paa_nytt(self):
        gammel = self._levert()

        def synkende(liste):
            liste.sort(reverse=True)

        with mock.patch.object(okter.random, "shuffle", side_effect=synkende) as stokk:
            ny = self._ta_pa_nytt()
        # Én ny stokking per spørsmål, og resultatet er det som lagres i det nye
        # forsøket, ikke rekkefølgen fra det gamle.
        self.assertEqual(stokk.call_count, len(ny.innhold))
        for gammel_rad, ny_rad in zip(gammel.innhold, ny.innhold, strict=True):
            self.assertEqual(
                ny_rad["alternativer"],
                sorted(gammel_rad["alternativer"], reverse=True),
            )

    def test_paabegynt_forsok_fortsettes(self):
        self._levert()
        ny = self._ta_pa_nytt()
        self._besvar(1, True, okt=ny)
        svar = self.client.post(self._start_url())
        self.assertRedirects(svar, self._url(ny, 2), fetch_redirect_response=False)
        self.assertEqual(
            Okt.objects.filter(quiz=self.quiz, status=Oktstatus.PABEGYNT).count(), 1
        )
        self.assertEqual(Okt.objects.filter(quiz=self.quiz).count(), 2)

    def test_annen_brukers_quiz_gir_404(self):
        _, quiz = self._annen_bruker()
        svar = self.client.post(self._start_url(quiz))
        self.assertEqual(svar.status_code, 404)
        self.assertFalse(Okt.objects.filter(quiz=quiz).exists())


class ResultatsideTest(TaPaNyttTestCase):
    def test_s11_har_ta_pa_nytt_skjema(self):
        self._levert()
        html = self.client.get(self._resultat_url()).content.decode()
        skjema = html.index(f'<form method="post" action="{self._start_url()}"')
        slutt = html.index("</form>", skjema)
        self.assertIn("csrfmiddlewaretoken", html[skjema:slutt])
        self.assertIn(">Ta på nytt</button>", html[skjema:slutt])
        self.assertLess(skjema, html.index("Tilbake til notatet"))

    def test_ta_pa_nytt_fra_s11_lager_nytt_forsok(self):
        gammel = self._levert()
        html = self.client.get(self._resultat_url()).content.decode()
        skjema = re.search(
            r'<form method="post" action="([^"]+)"[^>]*>\s*<input[^>]*csrf[^>]*>'
            r"\s*<button[^>]*>Ta på nytt</button>",
            html,
        )
        self.assertIsNotNone(skjema)
        svar = self.client.post(skjema.group(1))
        ny = Okt.objects.get(quiz=self.quiz, status=Oktstatus.PABEGYNT)
        self.assertNotEqual(ny.pk, gammel.pk)
        self.assertRedirects(svar, self._url(ny, 1), fetch_redirect_response=False)

    def test_eldre_resultat_har_ogsa_knappen(self):
        gammel = self._levert()
        self._levert(okt=self._ta_pa_nytt())
        html = self.client.get(self._resultat_url(gammel)).content.decode()
        self.assertIn(">Ta på nytt</button>", html)


class LaertGjennomNyeForsokTest(TaPaNyttTestCase):
    def _hendelse(self, okt, nr):
        return Svar.objects.get(okt=okt, sporsmal_id=okt.innhold[nr - 1]["sporsmal"])

    def test_to_riktige_paa_rad_i_nye_forsok_gir_laert_og_fasit(self):
        forste = self._levert(riktige={2, 3, 4, 5})  # Spørsmål 1 feil.
        sporsmal_id = forste.innhold[0]["sporsmal"]
        self.assertEqual(self._hendelse(forste, 1).hendelse, Hendelse.LAGT_I)

        andre = self._levert(riktige={1, 2, 3, 4, 5}, okt=self._ta_pa_nytt())
        self.assertEqual(self._hendelse(andre, 1).hendelse, Hendelse.OPP)
        html = self.client.get(self._resultat_url(andre)).content.decode()
        self.assertNotIn("Riktig svar:", html)
        self.assertNotIn("feilbanken", html)

        tredje = self._levert(riktige={1, 2, 3, 4, 5}, okt=self._ta_pa_nytt())
        self.assertEqual(self._hendelse(tredje, 1).hendelse, Hendelse.LAERT)
        rad = Feilbankrad.objects.get(sporsmal_id=sporsmal_id)
        self.assertIsNotNone(rad.laert_tidspunkt)
        self.assertTrue(fasit_synlig(rad.sporsmal))

        html = self.client.get(self._resultat_url(tredje)).content.decode()
        riktig = rad.sporsmal.alternativer.get(er_riktig=True)
        self.assertEqual(html.count("Riktig svar:"), 1)
        self.assertIn(riktig.tekst, html)
        self.assertIn(f"Begrunnelse: <span>{rad.sporsmal.begrunnelse}</span>", html)
        # De gamle hendelsene er uendret.
        self.assertEqual(self._hendelse(forste, 1).hendelse, Hendelse.LAGT_I)
        self.assertEqual(self._hendelse(andre, 1).hendelse, Hendelse.OPP)

    def test_feil_i_nytt_forsok_nullstiller_og_telles_ikke_som_lagt_i(self):
        self._levert(riktige={2, 3, 4, 5})
        andre = self._levert(riktige={2, 3, 4, 5}, okt=self._ta_pa_nytt())
        self.assertEqual(self._hendelse(andre, 1).hendelse, Hendelse.NULLSTILT)
        self.assertEqual(Feilbankrad.objects.count(), 1)
        html = self.client.get(self._resultat_url(andre)).content.decode()
        self.assertNotIn("feilbanken", html)
