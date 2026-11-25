"""Tester for resultatet av øving (S12, FR-23, AD-18, AD-20), én per rad i I/O-matrisen i spec 4.2."""

import re

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from farequiz import feilmeldinger
from studier.models import (
    Feilbankrad,
    Hendelse,
    Okt,
    Oktstatus,
    Okttype,
    Quiz,
    Sporsmal,
    Svar,
)
from studier.services.okter import lagre_svar, lever_okt
from studier.tests.test_oving import OvingTestCase


class OvingResultatTestCase(OvingTestCase):
    def _sett_k(self, sporsmal, k):
        Feilbankrad.objects.filter(sporsmal=sporsmal).update(riktige_pa_rad=k)

    def _svar_med(self, okt, riktig):
        """Svarer på alle spørsmålene i økten. `riktig(sporsmal)` velger riktig eller feil."""
        for rad in okt.innhold:
            s = Sporsmal.objects.get(pk=rad["sporsmal"])
            lagre_svar(okt, s, s.alternativer.filter(er_riktig=riktig(s)).first())

    def _svar_feil_alle(self, okt):
        self._svar_med(okt, lambda _s: False)

    def _resultat(self, okt):
        svar = self.client.get(f"/okter/{okt.pk}/resultat/")
        self.assertEqual(svar.status_code, 200)
        return svar, svar.content.decode()

    def _levert_oving(self, k, riktig=True):
        """Øving med en åpen rad per verdi i `k` (riktige på rad før økten), levert."""
        aapne = self._rader(len(k), 0)
        for s, verdi in zip(aapne, k, strict=True):
            self._sett_k(s, verdi)
        _, okt = self._start()
        if riktig:
            self._svar_alle(okt)
        else:
            self._svar_feil_alle(okt)
        lever_okt(okt)
        return aapne, okt


class OvingResultatTest(OvingResultatTestCase):
    def test_noen_laert(self):
        Quiz.objects.filter(pk=self.quiz.pk).update(sprak="en")
        aapne, okt = self._levert_oving(k=(1, 1, 0))
        svar, html = self._resultat(okt)
        self.assertIn(
            '<p role="status" class="text-3xl font-semibold tabular-nums">'
            "3 av 3 riktige</p>",
            html,
        )
        self.assertIn("2 spørsmål er lært.", html)
        self.assertEqual(svar.context["antall_laert"], 2)
        # Rekkefølgen på siden.
        rekke = [
            html.index('<h1 class="mb-4 text-2xl font-semibold">Øv på feil</h1>'),
            html.index('role="status"'),
            html.index("2 spørsmål er lært."),
            html.index(">Lært</h2>"),
            html.index(">Svar</h2>"),
        ]
        self.assertEqual(rekke, sorted(rekke))
        laert_seksjon = html[html.index(">Lært</h2>") : html.index(">Svar</h2>")]
        for s in aapne[:2]:
            riktig = s.alternativer.get(er_riktig=True)
            nr = [r["sporsmal"] for r in okt.innhold].index(s.pk) + 1
            self.assertIn(f'<strong lang="en">{nr}. {s.tekst}</strong>', laert_seksjon)
            self.assertIn(
                f'Lært. Riktig svar var: <span lang="en">{riktig.tekst}</span>',
                laert_seksjon,
            )
            self.assertIn(
                f'Begrunnelse: <span lang="en">{s.begrunnelse}</span>', laert_seksjon
            )
        self.assertNotIn(aapne[2].tekst, laert_seksjon)
        svar_seksjon = html[html.index(">Svar</h2>") :]
        # Fasiten gjentas ikke i raden, og lærte rader har «Lært» i stedet for teller.
        self.assertNotIn("Riktig svar:", svar_seksjon)
        self.assertNotIn("Begrunnelse:", svar_seksjon)
        self.assertEqual(
            svar_seksjon.count('<span class="font-semibold">Lært</span>'), 2
        )
        self.assertEqual(svar_seksjon.count("av 2 riktige på rad"), 1)
        self.assertIn("1 av 2 riktige på rad", svar_seksjon)
        self.assertNotIn(aapne[2].begrunnelse, html)
        # Én fylt og én tom prikk, skjult for skjermlesere.
        rader = {r["tekst"]: r for r in svar.context["rader"]}
        self.assertEqual(rader[aapne[2].tekst]["prikker"], [True, False])
        prikk = "inline-block h-3 w-3 rounded-full border-2 border-accent-strong"
        self.assertEqual(html.count(f'{prikk} bg-accent-strong"></span>'), 1)
        self.assertEqual(html.count(f'{prikk}"></span>'), 1)
        self.assertIn('<span class="inline-flex gap-1" aria-hidden="true">', html)

    def test_feil_svar(self):
        _, okt = self._levert_oving(k=(1,), riktig=False)
        svar, html = self._resultat(okt)
        self.assertIn("0 av 1 riktige", html)
        self.assertIn('<strong class="text-error">Feil</strong>', html)
        self.assertIn(
            '<span class="text-error font-semibold" aria-hidden="true">✕</span>', html
        )
        self.assertIn("0 av 2 riktige på rad", html)
        self.assertNotIn("Riktig svar", html)
        self.assertNotIn("Begrunnelse", html)
        self.assertNotIn("er lært.", html)
        self.assertNotIn(">Lært</h2>", html)
        self.assertEqual(svar.context["rader"][0]["prikker"], [False, False])
        prikk = "inline-block h-3 w-3 rounded-full border-2 border-accent-strong"
        self.assertNotIn(f'{prikk} bg-accent-strong"></span>', html)
        self.assertEqual(html.count(f'{prikk}"></span>'), 2)
        self.assertEqual(svar.context["antall_laert"], 0)

    def test_alt_laert(self):
        _, okt = self._levert_oving(k=(1, 1))
        _, html = self._resultat(okt)
        self.assertIn("Alle spørsmålene er lært. Feilbanken er tom.", html)
        self.assertIn(f'href="{self.notat_url}"', html)
        self.assertIn("Tilbake til notatet", html)
        self.assertNotIn(f'action="{self.ov_url}"', html)
        self.assertNotIn("Øv på feil (", html)
        main = re.search(r"<main.*?</main>", html, re.DOTALL).group()
        self.assertNotIn("!", main)

    def test_ikke_tom_feilbank_uten_melding(self):
        _, okt = self._levert_oving(k=(1, 0))
        _, html = self._resultat(okt)
        self.assertNotIn("Feilbanken er tom", html)
        self.assertIn("Øv på feil (1)", html)

    def test_ubesvarte(self):
        aapne = self._rader(3, 0)
        _, okt = self._start()
        self._svar_alle(okt, 1)
        svar = self.client.post(f"/okter/{okt.pk}/lever/")
        self.assertEqual(svar.status_code, 200)
        html = svar.content.decode()
        self.assertIn(feilmeldinger.ubesvarte_tekst([2, 3]), html)
        self.assertIn(f'href="/okter/{okt.pk}/sporsmal/2/"', html)
        self.assertIn(f'href="/okter/{okt.pk}/sporsmal/3/"', html)
        okt.refresh_from_db()
        self.assertEqual(okt.status, Oktstatus.PABEGYNT)
        self.assertEqual(
            list(Svar.objects.filter(okt=okt).values_list("hendelse", flat=True)), [""]
        )
        for s in aapne:
            rad = Feilbankrad.objects.get(sporsmal=s)
            self.assertEqual(rad.riktige_pa_rad, 0)
            self.assertIsNone(rad.laert_tidspunkt)

    def test_laert_sa_feil(self):
        aapne, oving = self._levert_oving(k=(1,))
        sporsmal = aapne[0]
        self.assertEqual(Svar.objects.get(okt=oving).hendelse, Hendelse.LAERT)
        forsok = self._okt()
        self._svar_med(forsok, lambda s: s.pk != sporsmal.pk)
        lever_okt(forsok)
        rad = Feilbankrad.objects.get(sporsmal=sporsmal)
        self.assertIsNone(rad.laert_tidspunkt)
        self.assertEqual(rad.riktige_pa_rad, 0)
        svar, html = self._resultat(oving)
        self.assertEqual(svar.context["antall_laert"], 0)
        self.assertNotIn(">Lært</h2>", html)
        self.assertNotIn("er lært.", html)
        self.assertNotIn("Riktig svar", html)
        self.assertNotIn("Begrunnelse", html)
        self.assertNotIn('<span class="font-semibold">Lært</span>', html)
        self.assertIn("0 av 2 riktige på rad", html)
        self.assertNotIn("Feilbanken er tom", html)

    def test_forsok_uendret(self):
        # Bare ett lært spørsmål: ingen åpne rader, så feilbanken er tom.
        self._rader(0, 1)
        forsok = self._okt()
        self._svar_alle(forsok)
        lever_okt(forsok)
        svar, html = self._resultat(forsok)
        self.assertNotIn("ovemodus", html)
        self.assertNotIn(">Lært</h2>", html)
        self.assertNotIn("er lært.", html)
        self.assertNotIn("riktige på rad", html)
        self.assertNotIn("Feilbanken er tom", html)
        self.assertFalse(svar.context["feilbank_tom"])
        self.assertIn('<h1 class="mb-4 text-2xl font-semibold">Resultat</h1>', html)
        self.assertRegex(html, r"<title>Resultat – notat\.txt")
        # Det lærte spørsmålet har fortsatt fasiten inne i raden.
        laert = self.quiz.sporsmal.order_by("id").first()
        self.assertIn(
            f"Riktig svar: <span>{laert.alternativer.get(er_riktig=True).tekst}</span>",
            html,
        )
        self.assertFalse(svar.context["er_oving"])
        self.assertEqual(html.count("Begrunnelse:"), 1)

    def test_tilgang(self):
        _annen, annens_quiz = self._annen_bruker()
        annens_okt = Okt.objects.create(
            notat=annens_quiz.notat,
            type=Okttype.OVING,
            status=Oktstatus.LEVERT,
            innhold=[],
        )
        svar = self.client.get(f"/okter/{annens_okt.pk}/resultat/")
        self.assertEqual(svar.status_code, 404)


class OvingResultatSideTest(OvingResultatTestCase):
    def test_tittel_brodsmule_og_ovemodus(self):
        _, okt = self._levert_oving(k=(0,))
        _, html = self._resultat(okt)
        self.assertRegex(html, r"<title>Øv på feil – Resultat – notat\.txt")
        self.assertIn('<div class="ovemodus">', html)
        nav = re.search(r'<nav aria-label="Brødsmuler".*?</nav>', html, re.DOTALL)
        self.assertIn("Øv på feil – Resultat", nav.group())
        self.assertIn("Tilbake til notatet", html)
        self.assertNotIn("/start/", html)
        # «Lært»-seksjonen står bare når noe ble lært.
        self.assertNotIn(">Lært</h2>", html)

    def test_ingen_fasit_for_ikke_laerte(self):
        # Det ene blir lært, det andre svares feil, så riktig tekst ikke er «Ditt svar».
        laert, ikke_laert = self._rader(2, 0)
        self._sett_k(laert, 1)
        _, okt = self._start()
        self._svar_med(okt, lambda s: s.pk == laert.pk)
        lever_okt(okt)
        svar, html = self._resultat(okt)
        self.assertNotIn(ikke_laert.alternativer.get(er_riktig=True).tekst, html)
        self.assertNotIn(ikke_laert.begrunnelse, html)
        rader = {r["tekst"]: r for r in svar.context["rader"]}
        self.assertIsNone(rader[ikke_laert.tekst]["fasit"])
        self.assertEqual([s["tekst"] for s in svar.context["laerte"]], [laert.tekst])
        self.assertIn(laert.begrunnelse, html)

    def test_laert_senere_men_ikke_i_okten(self):
        """Lært nå, men svaret i økten ga `opp`: vanlig rad med fasit, ingen «Lært»-seksjon."""
        (sporsmal,), okt = self._levert_oving(k=(0,))
        self.assertEqual(Svar.objects.get(okt=okt).hendelse, Hendelse.OPP)
        Feilbankrad.objects.filter(sporsmal=sporsmal).update(
            riktige_pa_rad=2, laert_tidspunkt=timezone.now()
        )
        svar, html = self._resultat(okt)
        self.assertEqual(svar.context["antall_laert"], 0)
        self.assertNotIn(">Lært</h2>", html)
        self.assertNotIn("spørsmål er lært.", html)
        self.assertIn('<span class="font-semibold">Lært</span>', html)
        self.assertNotIn("riktige på rad", html)
        riktig = sporsmal.alternativer.get(er_riktig=True)
        self.assertIn(f"Riktig svar: <span>{riktig.tekst}</span>", html)
        self.assertIn(f"Begrunnelse: <span>{sporsmal.begrunnelse}</span>", html)

    def test_riktig_alternativ_for_andre_star_ikke_pa_siden(self):
        # Ett spørsmål blir lært, det andre svares feil.
        aapne = self._rader(2, 0)
        self._sett_k(aapne[0], 1)
        _, okt = self._start()
        self._svar_med(okt, lambda s: s.pk == aapne[0].pk)
        lever_okt(okt)
        _, html = self._resultat(okt)
        self.assertIn(
            "Lært. Riktig svar var: <span>"
            f"{aapne[0].alternativer.get(er_riktig=True).tekst}</span>",
            html,
        )
        self.assertNotIn(aapne[1].alternativer.get(er_riktig=True).tekst, html)

    def test_sporringer_vokser_ikke_utover_fasit_synlig(self):
        """Fra to til fire spørsmål: én spørring mer per spørsmål (`fasit_synlig`)."""
        aapne = self._rader(2, 0)
        _, okt = self._start()
        self._svar_feil_alle(okt)
        lever_okt(okt)
        with CaptureQueriesContext(connection) as to:
            self._resultat(okt)
        # Tell nå: loggen tømmes ved neste forespørsel.
        antall_for_to = len(to.captured_queries)
        for s in self.quiz.sporsmal.exclude(pk__in=[a.pk for a in aapne])[:2]:
            Feilbankrad.objects.create(sporsmal=s)
        self.client.post(self.ov_url)
        okt4 = Okt.objects.get(type=Okttype.OVING, status=Oktstatus.PABEGYNT)
        self.assertEqual(len(okt4.innhold), 4)
        self._svar_feil_alle(okt4)
        lever_okt(okt4)
        with self.assertNumQueries(antall_for_to + 2):
            self._resultat(okt4)
