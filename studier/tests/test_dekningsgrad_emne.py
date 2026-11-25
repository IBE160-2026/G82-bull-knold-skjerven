"""Tester for dekningsgraden per emne på S4 og S3 (FR-25, AD-4, UX-DR7, UX-DR8), én per rad i I/O-matrisen i spec 5.2."""

import re

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from studier.models import Emne, Feilbankrad, Notat, Okt, Oktstatus, Okttype, Svar
from studier.services import dekningsgrad
from studier.services.feilbank import antall_apne_per_notat, apne_rader
from studier.services.notater import last_opp
from studier.tests.fabrikk import lag_bruker, lag_kjede
from studier.tests.test_dekningsgrad import (
    LETT,
    MIDDELS,
    VANSKELIG,
    DekningTestCase,
)


def _notatkort(html, navn):
    """Notatkortet på S4 (lenken) med filnavnet `navn`."""
    treff = re.search(
        rf'<a href="/notater/\d+/"[^>]*>\s*<span class="block text-lg font-semibold">'
        rf"{re.escape(navn)}</span>.*?</a>",
        html,
        flags=re.DOTALL,
    )
    return treff.group(0) if treff else None


def _emnekort(html, navn):
    """Emnekortet på S3 (lenken) for emnet `navn`."""
    treff = re.search(
        rf'<a href="/emner/\d+/"[^>]*>\s*<span class="block text-lg font-semibold">'
        rf"{re.escape(navn)}</span>.*?</a>",
        html,
        flags=re.DOTALL,
    )
    return treff.group(0) if treff else None


def _flis(html, tekst):
    """Verdien (`<dd>`) i flisen med `<dt>tekst</dt>`."""
    treff = re.search(
        rf'<div class="stat-tile[^"]*">\s*<dt[^>]*>{tekst}</dt>\s*<dd[^>]*>([^<]*)</dd>',
        html,
    )
    return treff.group(1) if treff else None


class EmneTestCase(DekningTestCase):
    def setUp(self):
        super().setUp()
        self.emne_url = f"/emner/{self.emne.pk}/"

    def _notat(self, navn, emne=None):
        return last_opp(
            emne or self.emne,
            SimpleUploadedFile(navn, b"Et notat."),
            self.bruker,
        )

    def _s4(self):
        return self.client.get(self.emne_url).content.decode()

    def _s3(self):
        return self.client.get("/").content.decode()

    def _fr25(self):
        """Notat A med 80 %, B med 40 % og C uten quiz, i tillegg til `self.notat` uten quiz."""
        a = self._notat("a.txt")
        self._forsok(self._quiz(LETT, 2, notat=a), riktige=2)
        self._forsok(self._quiz(MIDDELS, 2, notat=a), riktige=2)
        self._forsok(self._quiz(VANSKELIG, 5, notat=a), riktige=3)
        b = self._notat("b.txt")
        self._forsok(self._quiz(VANSKELIG, 5, notat=b), riktige=4)
        c = self._notat("c.txt")
        return a, b, c

    def _meld_alle(self, quiz):
        quiz.sporsmal.update(meldt_tidspunkt=timezone.now())


class MatriseTest(EmneTestCase):
    def test_fr25_eksempel(self):
        a, b, c = self._fr25()
        dekninger = dekningsgrad.for_notater([a, b, c])
        self.assertAlmostEqual(dekninger[a.pk].total, 0.8)
        self.assertAlmostEqual(dekninger[b.pk].total, 0.4)
        self.assertFalse(dekninger[c.pk].har_quiz)
        emne = dekningsgrad.for_emner([self.emne])[self.emne.pk]
        self.assertIsInstance(emne, float)
        self.assertAlmostEqual(emne, 0.6)

        html = self._s4()
        self.assertEqual(_flis(html, "Dekningsgrad"), "60 %")
        self.assertIn("Dekningsgrad 80 %", _notatkort(html, "a.txt"))
        self.assertIn('<span style="width: 80%"></span>', _notatkort(html, "a.txt"))
        self.assertIn("Dekningsgrad 40 %", _notatkort(html, "b.txt"))
        kort_c = _notatkort(html, "c.txt")
        self.assertIn("Ingen quiz", kort_c)
        self.assertNotIn("Dekningsgrad", kort_c)
        self.assertNotIn("reiserute", kort_c)

        self.assertIn("Dekningsgrad 60 %", _emnekort(self._s3(), "Webutvikling"))

    def test_emne_uten_notater(self):
        tomt = Emne.objects.create(eier=self.bruker, navn="Tomt")
        self.assertEqual(dekningsgrad.for_emner([tomt]), {tomt.pk: None})
        kort = _emnekort(self._s3(), "Tomt")
        self.assertIn("Ingen notater", kort)
        self.assertNotIn("Dekningsgrad", kort)
        self.assertNotIn("reiserute", kort)
        html = self.client.get(f"/emner/{tomt.pk}/").content.decode()
        self.assertNotIn("stat-tile", html)
        self.assertNotIn("I feilbanken", html)
        self.assertIn("Ingen notater ennå. Last opp det første.", html)

    def test_ingen_quiz(self):
        self._notat("annet.txt")
        self.assertIsNone(dekningsgrad.for_emner([self.emne])[self.emne.pk])
        kort = _emnekort(self._s3(), "Webutvikling")
        self.assertIn("Ingen dekningsgrad", kort)
        self.assertNotIn("reiserute", kort)
        html = self._s4()
        self.assertEqual(_flis(html, "Dekningsgrad"), "Ingen dekningsgrad")
        self.assertEqual(_notatkort(html, "notat.txt").count("Ingen quiz"), 1)

    def test_alle_meldt_teller_som_uten_quiz(self):
        meldt = self._quiz(LETT, 2)
        self._forsok(meldt, riktige=2)
        self._meld_alle(meldt)
        dekning = dekningsgrad.for_notater([self.notat])[self.notat.pk]
        self.assertFalse(dekning.har_quiz)
        self.assertIsNone(dekningsgrad.for_emner([self.emne])[self.emne.pk])
        self.assertIn("Ingen quiz", _notatkort(self._s4(), "notat.txt"))
        # Med et annet notat på 50 % er snittet 50 %, ikke 25 %.
        annet = self._notat("annet.txt")
        self._forsok(self._quiz(LETT, 2, notat=annet), riktige=2)
        self._forsok(self._quiz(MIDDELS, 2, notat=annet), riktige=2)
        self.assertAlmostEqual(dekningsgrad.for_emner([self.emne])[self.emne.pk], 0.5)
        self.assertEqual(_flis(self._s4(), "Dekningsgrad"), "50 %")

    def test_feilbank(self):
        a = self._notat("a.txt")
        b = self._notat("b.txt")
        quiz_a = self._quiz(LETT, 4, notat=a)
        quiz_b = self._quiz(LETT, 3, notat=b)
        sp_a = list(quiz_a.sporsmal.order_by("id"))
        sp_b = list(quiz_b.sporsmal.order_by("id"))
        Feilbankrad.objects.create(sporsmal=sp_a[0])
        Feilbankrad.objects.create(sporsmal=sp_a[1])
        Feilbankrad.objects.create(sporsmal=sp_b[0])
        # En meldt og en lært rad telles ikke.
        Feilbankrad.objects.create(sporsmal=sp_a[2])
        sp_a[2].meldt_tidspunkt = timezone.now()
        sp_a[2].save(update_fields=["meldt_tidspunkt"])
        Feilbankrad.objects.create(sporsmal=sp_b[1], laert_tidspunkt=timezone.now())

        antall = antall_apne_per_notat([a, b, self.notat])
        self.assertEqual(antall, {a.pk: 2, b.pk: 1, self.notat.pk: 0})
        for notat in (a, b):
            self.assertEqual(antall[notat.pk], apne_rader(notat).count())

        html = self._s4()
        self.assertIn("2 i feilbanken", _notatkort(html, "a.txt"))
        self.assertIn("1 i feilbanken", _notatkort(html, "b.txt"))
        self.assertIn("0 i feilbanken", _notatkort(html, "notat.txt"))
        self.assertEqual(_flis(html, "I feilbanken"), "3")

    def test_samme_som_s7(self):
        a, b, c = self._fr25()
        quiz = self._quiz(MIDDELS, 3)
        self._forsok(quiz, riktige=1)
        self._forsok(quiz, riktige=2, status=Oktstatus.PABEGYNT)
        Feilbankrad.objects.create(sporsmal=quiz.sporsmal.order_by("id").first())
        oving = Okt.objects.create(
            notat=self.notat, type=Okttype.OVING, status=Oktstatus.LEVERT
        )
        siste = quiz.sporsmal.order_by("id").last()
        Svar.objects.create(
            okt=oving, sporsmal=siste, alternativ=siste.alternativer.get(er_riktig=True)
        )
        alle = [self.notat, a, b, c]
        dekninger = dekningsgrad.for_notater(alle)
        for notat in alle:
            with self.subTest(notat=notat.originalnavn):
                self.assertEqual(dekninger[notat.pk], dekningsgrad.for_notat(notat))
        self.assertAlmostEqual(dekninger[self.notat.pk].nivaer[MIDDELS], 1 / 3)
        # Faste tall, så testen ikke bare sammenligner `for_notat` med seg selv.
        self.assertAlmostEqual(dekninger[self.notat.pk].total, 0.1)
        self.assertAlmostEqual(dekninger[a.pk].total, 0.8)
        self.assertAlmostEqual(dekninger[b.pk].total, 0.4)
        self.assertFalse(dekninger[c.pk].har_quiz)
        self.assertEqual(dekninger[c.pk].total, 0.0)

    def test_notat_med_quiz_pa_0_prosent_teller_i_snittet(self):
        self._quiz(LETT, 2)
        annet = self._notat("annet.txt")
        self._forsok(self._quiz(LETT, 2, notat=annet), riktige=2)
        self._forsok(self._quiz(MIDDELS, 2, notat=annet), riktige=2)
        dekning = dekningsgrad.for_notater([self.notat])[self.notat.pk]
        self.assertTrue(dekning.har_quiz)
        self.assertEqual(dekning.total, 0.0)
        self.assertAlmostEqual(dekningsgrad.for_emner([self.emne])[self.emne.pk], 0.25)
        html = self._s4()
        self.assertEqual(_flis(html, "Dekningsgrad"), "25 %")
        kort = _notatkort(html, "notat.txt")
        self.assertIn("Dekningsgrad 0 %", kort)
        self.assertIn('<span style="width: 0%"></span>', kort)
        self.assertNotIn("Ingen quiz", kort)

    def test_andre_brukere(self):
        annen = lag_bruker("annen@eks.no")
        # Den andre brukeren har et levert forsøk med riktig svar og en åpen feilbankrad.
        kjede = lag_kjede(annen, "Hemmelig emne")
        andres_notat = kjede[Notat]
        Okt.objects.filter(pk=kjede[Okt].pk).update(status=Oktstatus.LEVERT)
        self._forsok(self._quiz(LETT, 2), riktige=1)

        s3 = self._s3()
        self.assertNotIn("Hemmelig emne", s3)
        self.assertIn("Dekningsgrad 10 %", _emnekort(s3, "Webutvikling"))
        s4 = self._s4()
        self.assertNotIn(andres_notat.originalnavn, s4)
        self.assertEqual(_flis(s4, "Dekningsgrad"), "10 %")
        self.assertEqual(_flis(s4, "I feilbanken"), "0")
        self.assertEqual(self.client.get(f"/emner/{kjede[Emne].pk}/").status_code, 404)

    def test_antall_sporringer_pa_s3_og_s4(self):
        self._forsok(self._quiz(LETT, 2), riktige=1)
        Feilbankrad.objects.create(sporsmal=self.notat.quizer.get().sporsmal.first())
        with CaptureQueriesContext(connection) as s4_en:
            self._s4()
        with CaptureQueriesContext(connection) as s3_en:
            self._s3()
        for navn in ("a.txt", "b.txt"):
            notat = self._notat(navn)
            quiz = self._quiz(MIDDELS, 3, notat=notat)
            self._forsok(quiz, riktige=2)
            Feilbankrad.objects.create(sporsmal=quiz.sporsmal.last())
        with CaptureQueriesContext(connection) as s4_tre:
            self._s4()
        for navn in ("Databaser", "Kjemi"):
            emne = Emne.objects.create(eier=self.bruker, navn=navn)
            notat = self._notat(f"{navn}.txt", emne=emne)
            self._forsok(self._quiz(VANSKELIG, 4, notat=notat), riktige=3)
        with CaptureQueriesContext(connection) as s3_tre:
            self._s3()
        self.assertEqual(len(s4_en), len(s4_tre))
        self.assertEqual(len(s3_en), len(s3_tre))


class TjenesteTest(EmneTestCase):
    def test_for_notater_er_to_sporringer(self):
        a, b, c = self._fr25()
        with CaptureQueriesContext(connection) as sporringer:
            dekningsgrad.for_notater([self.notat, a, b, c])
        self.assertEqual(len(sporringer), 2)

    def test_for_emner_for_flere_emner(self):
        self._fr25()
        annet = Emne.objects.create(eier=self.bruker, navn="Annet")
        notat = self._notat("x.txt", emne=annet)
        self._forsok(self._quiz(VANSKELIG, 2, notat=notat), riktige=2)
        tomt = Emne.objects.create(eier=self.bruker, navn="Tomt")
        with CaptureQueriesContext(connection) as sporringer:
            dekninger = dekningsgrad.for_emner([self.emne, annet, tomt])
        self.assertEqual(len(sporringer), 3)
        self.assertAlmostEqual(dekninger[self.emne.pk], 0.6)
        self.assertEqual(dekninger[annet.pk], 0.5)
        self.assertIsNone(dekninger[tomt.pk])

    def test_antall_apne_per_notat_er_en_sporring(self):
        a = self._notat("a.txt")
        Feilbankrad.objects.create(
            sporsmal=self._quiz(LETT, 2, notat=a).sporsmal.first()
        )
        with CaptureQueriesContext(connection) as sporringer:
            antall_apne_per_notat([a, self.notat])
        self.assertEqual(len(sporringer), 1)


class HtmlTest(EmneTestCase):
    def test_s4_flisene_under_h1_og_over_notatene(self):
        self._fr25()
        html = self._s4()
        flis = html.index('<dl class="mb-6 grid')
        self.assertLess(html.index("</h1>"), flis)
        self.assertLess(flis, html.index(">Last opp notat</a>"))
        self.assertIn(
            '<div class="stat-tile rounded-lg bg-surface-inverse p-4 text-ink-inverse">',
            html,
        )
        self.assertEqual(html.count('<div class="stat-tile'), 2)
        self.assertEqual(_flis(html, "I feilbanken"), "0")

    def test_s4_ingen_dekningsgrad_i_flisen(self):
        html = self._s4()
        self.assertEqual(_flis(html, "Dekningsgrad"), "Ingen dekningsgrad")
        self.assertIn('<dl class="mb-6 grid gap-3 md:grid-cols-2">', html)
        self.assertNotIn("–", html[html.index("<dl") : html.index("</dl>")])

    def test_s4_notatkortet_har_skjult_stolpe(self):
        self._fr25()
        kort = _notatkort(self._s4(), "b.txt")
        self.assertIn(
            '<div class="reiserute" aria-hidden="true"><span style="width: 40%"></span></div>',
            kort,
        )
        self.assertIn("Lastet opp", kort)
        self.assertIn("0 i feilbanken", kort)
        tekst = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", kort)).strip()
        self.assertRegex(
            tekst, r"^b\.txt, Lastet opp [^,]+, Dekningsgrad 40 %, 0 i feilbanken$"
        )

    def test_s3_teksten_star_i_lenken(self):
        self._fr25()
        kort = _emnekort(self._s3(), "Webutvikling")
        self.assertIn("4 notater", kort)
        self.assertIn(
            '<div class="reiserute" aria-hidden="true"><span style="width: 60%"></span></div>',
            kort,
        )
        tekst = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", kort)).strip()
        self.assertTrue(
            tekst.startswith("Webutvikling, 4 notater, Dekningsgrad 60 %"), tekst
        )
