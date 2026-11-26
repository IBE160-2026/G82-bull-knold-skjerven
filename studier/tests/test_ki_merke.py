"""KI-merket med modellnavnet på S7, S9 og S12, også i testmodus (SM-8, NFR-9)."""

from django.test import TestCase
from django.urls import reverse

import ki
from studier.models import Notat, Okt, Okttype, Quiz
from studier.tests.fabrikk import godta, lag_bruker, lag_olas

MODELL = "claude-haiku-5-5"
MERKE = "Laget av KI"
MODELLNAVN = "Claude Haiku 5.5"
BANNER = "Testmodus: quizene bruker mock-svar, ingen KI kalles."


class KiMerkeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ola = lag_bruker("ola@eks.no")
        godta(cls.ola)
        cls.kjede = lag_olas(cls.ola)
        Quiz.objects.filter(pk=cls.kjede[Quiz].pk).update(modell=MODELL)

    def setUp(self):
        self.client.force_login(self.ola)

    def _sjekk(self, svar):
        self.assertEqual(svar.status_code, 200)
        html = svar.content.decode()
        self.assertTrue(ki.er_testmodus())
        self.assertIn(BANNER, html)
        self.assertIn(MERKE, html)
        self.assertIn(MODELLNAVN, html)

    def test_s7_notatsiden(self):
        self._sjekk(
            self.client.get(reverse("studier:notat", args=[self.kjede[Notat].pk]))
        )

    def test_s9_ta_quiz(self):
        okt = self.kjede[Okt]
        self.assertEqual(okt.type, Okttype.FORSOK)
        svar = self.client.get(reverse("studier:sporsmal", args=[okt.pk, 1]))
        self._sjekk(svar)
        self.assertIn(f"{MERKE} ({MODELLNAVN})", svar.content.decode())

    def test_s12_ov_pa_feil(self):
        svar = self.client.post(
            reverse("studier:ov_pa_feil", args=[self.kjede[Notat].pk]), follow=True
        )
        oving = Okt.objects.get(type=Okttype.OVING)
        self.assertEqual(
            svar.redirect_chain[-1][0],
            reverse("studier:sporsmal", args=[oving.pk, 1]),
        )
        self._sjekk(svar)
        html = svar.content.decode()
        self.assertIn("Øv på feil", html)
        self.assertIn(f"{MERKE} ({MODELLNAVN})", html)
