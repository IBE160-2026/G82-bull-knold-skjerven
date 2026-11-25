"""Tester for å øve på feilbanken (FR-22, AD-6, AD-16), én per rad i I/O-matrisen i spec 4.1."""

import re
from datetime import timedelta
from unittest import mock

from django.db import IntegrityError
from django.utils import timezone

import ki
from farequiz.views import _fortsett_rader
from studier.models import Feilbankrad, Okt, Okttype, Quiz, Svar
from studier.services import okter
from studier.services.okter import (
    lagre_svar,
    lever_okt,
    start_eller_fortsett_okt,
)
from studier.tests.test_okter import OktTestCase


class OvingTestCase(OktTestCase):
    def setUp(self):
        super().setUp()
        self.quiz2 = self._quiz(self.notat, antall=5)
        self.ov_url = f"/notater/{self.notat.pk}/ov/"

    def _rader(self, antall=3, laert=1):
        """Feilbankrader for `laert + antall` spørsmål i to quizer. Gir de åpne spørsmålene."""
        sporsmal = [*self.quiz.sporsmal.order_by("id"), *self.quiz2.sporsmal.all()]
        aapne = []
        for i, s in enumerate(sporsmal[: antall + laert]):
            rad = Feilbankrad.objects.create(sporsmal=s)
            if i < laert:
                rad.laert_tidspunkt = timezone.now()
                rad.save()
            else:
                aapne.append(s)
        return aapne

    def _start(self):
        svar = self.client.post(self.ov_url)
        return svar, Okt.objects.filter(type=Okttype.OVING).first()

    def _svar_alle(self, okt, antall=None):
        for rad in okt.innhold[:antall]:
            s = self.quiz.sporsmal.filter(pk=rad["sporsmal"]).first() or (
                self.quiz2.sporsmal.get(pk=rad["sporsmal"])
            )
            lagre_svar(okt, s, s.alternativer.get(er_riktig=True))


class OvingTest(OvingTestCase):
    def test_start(self):
        # Radene opprettes i en annen rekkefølge enn spørsmåls-ID-ene, fra to quizer.
        s1 = list(self.quiz.sporsmal.order_by("id"))
        s2 = list(self.quiz2.sporsmal.order_by("id"))
        aapne = [s2[1], s1[3], s1[0]]
        start = timezone.now() - timedelta(hours=1)
        for i, s in enumerate(aapne):
            rad = Feilbankrad.objects.create(sporsmal=s)
            Feilbankrad.objects.filter(pk=rad.pk).update(
                opprettet=start + timedelta(minutes=i)
            )
        Feilbankrad.objects.create(sporsmal=s1[1], laert_tidspunkt=timezone.now())
        svar, okt = self._start()
        self.assertRedirects(svar, self._url(okt, 1), fetch_redirect_response=False)
        self.assertEqual(okt.type, Okttype.OVING)
        self.assertIsNone(okt.quiz)
        self.assertEqual(okt.notat, self.notat)
        self.assertEqual([r["sporsmal"] for r in okt.innhold], [s.pk for s in aapne])
        for rad in okt.innhold:
            self.assertEqual(len(rad["alternativer"]), 3)

    def test_fortsett(self):
        self._rader(3, 1)
        _, okt = self._start()
        self._svar_alle(okt, 1)
        svar = self.client.post(self.ov_url)
        self.assertRedirects(svar, self._url(okt, 2), fetch_redirect_response=False)
        self.assertEqual(Okt.objects.filter(type=Okttype.OVING).count(), 1)

    def test_last_innhold(self):
        aapne = self._rader(3, 0)
        _, okt = self._start()
        Feilbankrad.objects.filter(sporsmal=aapne[0]).update(
            laert_tidspunkt=timezone.now()
        )
        original = list(okt.innhold)
        svar = self.client.post(self.ov_url)
        self.assertRedirects(svar, self._url(okt, 1), fetch_redirect_response=False)
        self.assertEqual(Okt.objects.get(pk=okt.pk).innhold, original)
        self.assertEqual(len(original), 3)

    def test_tom_feilbank(self):
        html = self.client.get(self.notat_url).content.decode()
        self.assertIn('aria-disabled="true"', html)
        self.assertIn("Ingen spørsmål i feilbanken", html)
        svar, okt = self._start()
        self.assertIsNone(okt)
        self.assertRedirects(svar, self.notat_url, fetch_redirect_response=False)

    def test_tom_men_pabegynt(self):
        self._rader(2, 0)
        _, okt = self._start()
        Feilbankrad.objects.update(laert_tidspunkt=timezone.now())
        html = self.client.get(self.notat_url).content.decode()
        self.assertNotIn('aria-disabled="true"', html)
        self.assertIn(">Fortsett<", html)
        self.assertIn("Påbegynt – spørsmål 1 av 2", html)
        svar = self.client.post(self.ov_url)
        self.assertRedirects(svar, self._url(okt, 1), fetch_redirect_response=False)

    def test_knapp_med_antall(self):
        self._rader(3, 1)
        html = self.client.get(self.notat_url).content.decode()
        self.assertIn("Øv på feil (3)", html)

    def test_samtidig_start(self):
        self._rader(2, 0)
        forste = start_eller_fortsett_okt(notat=self.notat)
        with (
            mock.patch.object(okter, "_pabegynt_oving", side_effect=[None, forste]),
            mock.patch.object(okter.Okt.objects, "create", side_effect=IntegrityError),
        ):
            andre = start_eller_fortsett_okt(notat=self.notat)
        self.assertEqual(forste.pk, andre.pk)

    def test_ugyldige_argumenter(self):
        with self.assertRaises(ValueError):
            start_eller_fortsett_okt()
        with self.assertRaises(ValueError):
            start_eller_fortsett_okt(self.quiz, notat=self.notat)

    def test_s11_knapp_etter_forsok(self):
        self._rader(2, 0)
        okt = self._okt(self.quiz2)
        self._svar_alle(okt)
        lever_okt(okt)
        html = self.client.get(f"/okter/{okt.pk}/resultat/").content.decode()
        self.assertIn("Øv på feil (2)", html)

    def test_s11_levert_oving(self):
        self._rader(2, 0)
        _, okt = self._start()
        self._svar_alle(okt)
        lever_okt(okt)
        svar = self.client.get(f"/okter/{okt.pk}/resultat/")
        self.assertEqual(svar.status_code, 200)
        html = svar.content.decode()
        self.assertNotIn("/start/", html)
        self.assertIn("2 av 2 riktige", html)
        for rad in Feilbankrad.objects.all():
            self.assertEqual(rad.riktige_pa_rad, 1)
        for s in Svar.objects.filter(okt=okt):
            self.assertEqual(s.hendelse, "opp")

    def test_s3_rader(self):
        self._rader(2, 0)
        forsok = self._okt()
        _, oving = self._start()
        Okt.objects.filter(pk=forsok.pk).update(
            sist_endret=timezone.now() - timedelta(hours=1)
        )
        rader = _fortsett_rader(self.bruker)
        self.assertEqual([r["okt"].pk for r in rader], [oving.pk, forsok.pk])
        self.assertEqual(rader[0]["tittel"], "Øv på feil, 2 spørsmål")
        html = self.client.get("/").content.decode()
        self.assertIn("Fortsett øvingen", html)
        self.assertIn("Fortsett quizen", html)

    def test_tilgang(self):
        _annen, annens_quiz = self._annen_bruker()
        annens_notat = annens_quiz.notat
        Feilbankrad.objects.create(sporsmal=annens_quiz.sporsmal.first())
        self.assertEqual(
            self.client.post(f"/notater/{annens_notat.pk}/ov/").status_code, 404
        )
        self.assertFalse(Okt.objects.filter(type=Okttype.OVING).exists())
        annens_okt = Okt.objects.create(
            notat=annens_notat, type=Okttype.OVING, innhold=[]
        )
        self.assertEqual(
            self.client.get(f"/okter/{annens_okt.pk}/lever/").status_code, 404
        )
        self.assertEqual(Svar.objects.count(), 0)


class OvingSideTest(OvingTestCase):
    def _oving(self):
        self._rader(2, 0)
        _, okt = self._start()
        return okt

    def test_s9_oving(self):
        okt = self._oving()
        html = self.client.get(self._url(okt, 1)).content.decode()
        self.assertIn('<h1 class="text-2xl font-semibold">Øv på feil</h1>', html)
        self.assertIn("Spørsmål 1 av 2", html)
        self.assertIn("Laget av KI (", html)
        self.assertIn('class="ovemodus"', html)
        self.assertIn("Øv på feil – Spørsmål 1 av 2 –", html)
        nav = re.search(r'<nav aria-label="Brødsmuler".*?</nav>', html, re.DOTALL)
        self.assertIn("Øv på feil – Spørsmål 1 av 2", nav.group())
        self.assertNotIn("begrunnelse", html.lower())
        rad = okt.innhold[0]
        pos = [html.index(f'value="{pk}"') for pk in rad["alternativer"]]
        self.assertEqual(pos, sorted(pos))

    def test_s9_forsok_uten_ovemodus(self):
        okt = self._okt()
        html = self.client.get(self._url(okt, 1)).content.decode()
        self.assertNotIn("ovemodus", html)
        self.assertNotIn("Øv på feil", html)

    def test_s10_ovemodus_bare_for_oving(self):
        okt = self._oving()
        html = self.client.get(f"/okter/{okt.pk}/lever/").content.decode()
        self.assertIn('class="ovemodus"', html)
        forsok = self._okt()
        html = self.client.get(f"/okter/{forsok.pk}/lever/").content.decode()
        self.assertNotIn("ovemodus", html)

    def test_s9_kontekst_uten_fasit(self):
        okt = self._oving()
        svar = self.client.get(self._url(okt, 1))
        self.assertNotIn("er_riktig", svar.context)
        self.assertNotIn("begrunnelse", svar.context)

    def test_s9_viser_modellen_fra_sporsmalets_quiz(self):
        Quiz.objects.filter(pk=self.quiz2.pk).update(modell="claude-opus-4-8")
        self.quiz.refresh_from_db()
        sporsmal = [
            self.quiz.sporsmal.order_by("id").first(),
            self.quiz2.sporsmal.first(),
        ]
        for s in sporsmal:
            Feilbankrad.objects.create(sporsmal=s)
        _, okt = self._start()
        for nr, s in enumerate(sporsmal, start=1):
            self.assertEqual(okt.innhold[nr - 1]["sporsmal"], s.pk)
            html = self.client.get(self._url(okt, nr)).content.decode()
            modell = (
                "claude-opus-4-8" if s.quiz_id == self.quiz2.pk else self.quiz.modell
            )
            self.assertIn(f"Laget av KI ({ki.visningsnavn(modell)})", html)

    def test_s10_tittel(self):
        okt = self._oving()
        html = self.client.get(f"/okter/{okt.pk}/lever/").content.decode()
        self.assertRegex(html, r"<title>Øv på feil – Se over og lever")
        forsok = self._okt()
        html = self.client.get(f"/okter/{forsok.pk}/lever/").content.decode()
        self.assertRegex(html, r"<title>Se over og lever")


class OvingMer(OvingTestCase):
    def test_bare_notatets_rader(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        from studier.services.notater import last_opp

        annet = last_opp(
            self.emne, SimpleUploadedFile("annet.txt", b"Annet."), self.bruker
        )
        annen_quiz = self._quiz(annet)
        fremmed = annen_quiz.sporsmal.first()
        Feilbankrad.objects.create(sporsmal=fremmed)
        self._rader(2, 0)
        html = self.client.get(self.notat_url).content.decode()
        self.assertIn("Øv på feil (2)", html)
        _, okt = self._start()
        self.assertNotIn(fremmed.pk, [r["sporsmal"] for r in okt.innhold])
        self.assertEqual(len(okt.innhold), 2)

    def test_fremdrift_med_svar(self):
        self._rader(3, 0)
        _, okt = self._start()
        self._svar_alle(okt, 2)
        html = self.client.get(self.notat_url).content.decode()
        self.assertIn("Påbegynt – spørsmål 2 av 3", html)

    def test_s11_fortsett_uten_apne_rader(self):
        self._rader(2, 0)
        forsok = self._okt()
        self._svar_alle(forsok)
        lever_okt(forsok)
        self._start()
        Feilbankrad.objects.update(laert_tidspunkt=timezone.now())
        html = self.client.get(f"/okter/{forsok.pk}/resultat/").content.decode()
        self.assertIn(">Fortsett<", html)
        self.assertIn(f'action="{self.ov_url}"', html)

    def test_ov_tar_bare_post(self):
        self._rader(2, 0)
        self.assertEqual(self.client.get(self.ov_url).status_code, 405)
        self.assertFalse(Okt.objects.filter(type=Okttype.OVING).exists())
