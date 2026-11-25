"""Tester for regelen for feilbanken (story 3.2, FR-21, FR-23, AD-2, AD-3, AD-5)."""

import re
from pathlib import Path

from django.conf import settings
from django.test import TestCase

from studier.models import (
    Emne,
    Feilbankrad,
    Genereringsjobb,
    Hendelse,
    Notat,
    Quiz,
    Sporsmal,
)
from studier.services.feilbank import registrer_svar
from studier.tests.fabrikk import lag_bruker


def _sporsmal(notat, tekst="Hva står HTML for?"):
    jobb = Genereringsjobb.objects.create(
        notat=notat, vanskelighetsgrad="middels", antall=5
    )
    quiz = Quiz.objects.create(
        notat=notat,
        jobb=jobb,
        vanskelighetsgrad="middels",
        sprak="nb",
        modell="claude-sonnet-5-5",
        prompt_versjon="1",
    )
    return Sporsmal.objects.create(quiz=quiz, tekst=tekst, begrunnelse="Fordi.")


class FeilbankTestCase(TestCase):
    def setUp(self):
        bruker = lag_bruker()
        emne = Emne.objects.create(eier=bruker, navn="Webutvikling")
        self.notat = Notat.objects.create(
            emne=emne,
            fil=f"notater/{bruker.pk}/test.pdf",
            originalnavn="forelesning.pdf",
            filtype="pdf",
            storrelse=1234,
        )
        self.sporsmal = _sporsmal(self.notat)

    def rad(self, sporsmal=None):
        return Feilbankrad.objects.get(sporsmal=sporsmal or self.sporsmal)


class UtenRadTest(FeilbankTestCase):
    def test_feil_svar_legger_i_feilbanken_med_teller_0(self):
        self.assertEqual(registrer_svar(self.sporsmal, riktig=False), Hendelse.LAGT_I)
        rad = self.rad()
        self.assertEqual(rad.riktige_pa_rad, 0)
        self.assertIsNone(rad.laert_tidspunkt)

    def test_riktig_svar_gir_ingen_og_ingen_rad(self):
        self.assertEqual(registrer_svar(self.sporsmal, riktig=True), Hendelse.INGEN)
        self.assertFalse(Feilbankrad.objects.exists())


class IFeilbankenTest(FeilbankTestCase):
    def setUp(self):
        super().setUp()
        registrer_svar(self.sporsmal, riktig=False)

    def test_riktig_gir_opp_og_teller_1(self):
        self.assertEqual(registrer_svar(self.sporsmal, riktig=True), Hendelse.OPP)
        rad = self.rad()
        self.assertEqual(rad.riktige_pa_rad, 1)
        self.assertIsNone(rad.laert_tidspunkt)

    def test_to_riktige_pa_rad_gir_laert(self):
        registrer_svar(self.sporsmal, riktig=True)
        self.assertEqual(registrer_svar(self.sporsmal, riktig=True), Hendelse.LAERT)
        rad = self.rad()
        self.assertEqual(rad.riktige_pa_rad, 2)
        self.assertIsNotNone(rad.laert_tidspunkt)

    def test_feil_nullstiller_telleren(self):
        registrer_svar(self.sporsmal, riktig=True)
        self.assertEqual(
            registrer_svar(self.sporsmal, riktig=False), Hendelse.NULLSTILT
        )
        rad = self.rad()
        self.assertEqual(rad.riktige_pa_rad, 0)
        self.assertIsNone(rad.laert_tidspunkt)

    def test_feil_med_teller_0_gir_nullstilt(self):
        self.assertEqual(
            registrer_svar(self.sporsmal, riktig=False), Hendelse.NULLSTILT
        )
        self.assertEqual(Feilbankrad.objects.count(), 1)


class LaertTest(FeilbankTestCase):
    def setUp(self):
        super().setUp()
        registrer_svar(self.sporsmal, riktig=False)
        registrer_svar(self.sporsmal, riktig=True)
        registrer_svar(self.sporsmal, riktig=True)
        self.rad_id = self.rad().pk

    def test_feil_apner_samme_rad_igjen(self):
        self.assertEqual(
            registrer_svar(self.sporsmal, riktig=False), Hendelse.NULLSTILT
        )
        rad = self.rad()
        self.assertEqual(rad.pk, self.rad_id)
        self.assertEqual(rad.riktige_pa_rad, 0)
        self.assertIsNone(rad.laert_tidspunkt)
        self.assertEqual(Feilbankrad.objects.count(), 1)

    def test_kan_bli_laert_pa_nytt(self):
        forste = self.rad().laert_tidspunkt
        hendelser = [
            registrer_svar(self.sporsmal, riktig=riktig)
            for riktig in (False, True, True)
        ]
        self.assertEqual(hendelser, [Hendelse.NULLSTILT, Hendelse.OPP, Hendelse.LAERT])
        rad = self.rad()
        self.assertEqual(rad.pk, self.rad_id)
        self.assertGreaterEqual(rad.laert_tidspunkt, forste)
        self.assertEqual(Feilbankrad.objects.count(), 1)

    def test_riktig_gir_ingen_og_endrer_ikke_raden(self):
        for_svar = self.rad()
        self.assertEqual(registrer_svar(self.sporsmal, riktig=True), Hendelse.INGEN)
        etter = self.rad()
        self.assertEqual(etter.riktige_pa_rad, for_svar.riktige_pa_rad)
        self.assertEqual(etter.laert_tidspunkt, for_svar.laert_tidspunkt)


class SekvensTest(FeilbankTestCase):
    def test_feil_riktig_feil_riktig_riktig(self):
        hendelser = [
            registrer_svar(self.sporsmal, riktig=riktig)
            for riktig in (False, True, False, True, True)
        ]
        self.assertEqual(
            hendelser,
            [
                Hendelse.LAGT_I,
                Hendelse.OPP,
                Hendelse.NULLSTILT,
                Hendelse.OPP,
                Hendelse.LAERT,
            ],
        )
        self.assertEqual(Feilbankrad.objects.count(), 1)
        self.assertIsNotNone(self.rad().laert_tidspunkt)

    def test_alle_fem_hendelsene_dekkes(self):
        hendelser = {
            registrer_svar(self.sporsmal, riktig=riktig)
            for riktig in (True, False, True, False, True, True, True)
        }
        self.assertEqual(hendelser, set(Hendelse.values))


class SporsmalsidentitetTest(FeilbankTestCase):
    def test_lik_tekst_i_annen_quiz_pavirkes_ikke(self):
        annet = _sporsmal(self.notat, tekst=self.sporsmal.tekst)
        self.assertEqual(registrer_svar(self.sporsmal, riktig=False), Hendelse.LAGT_I)
        self.assertFalse(Feilbankrad.objects.filter(sporsmal=annet).exists())
        self.assertEqual(registrer_svar(annet, riktig=True), Hendelse.INGEN)
        self.assertEqual(registrer_svar(annet, riktig=False), Hendelse.LAGT_I)
        self.assertEqual(Feilbankrad.objects.count(), 2)


class EnesteStedTest(TestCase):
    """`registrer_svar` er eneste sted som lager eller endrer `Feilbankrad` (AD-2)."""

    APPER = ("studier", "kontoer", "farequiz", "ki")
    TILLATT = {Path("studier/services/feilbank.py")}
    # Bare skriving. Lesing (Epic 4 og 5) er lov.
    MONSTER = re.compile(
        r"Feilbankrad\b[^\n]*\."
        r"(create|get_or_create|update_or_create|bulk_create|bulk_update|update|delete|save)\("
        r"|(?<!class )\bFeilbankrad\("
        r"|feilbankrad\b[^\n]*\.(save|delete|update)\("
    )

    def test_monsteret_finner_skriving_og_slipper_lesing(self):
        skriving = [
            "Feilbankrad.objects.create(sporsmal=s)",
            "Feilbankrad.objects.get_or_create(sporsmal=s)",
            "Feilbankrad.objects.filter(pk=1).update(riktige_pa_rad=0)",
            "egne(Feilbankrad, bruker).update(laert_tidspunkt=None)",
            "Feilbankrad(sporsmal=s).save()",
            "sporsmal.feilbankrad.save()",
        ]
        lesing = [
            "class Feilbankrad(models.Model):",
            "Feilbankrad.objects.filter(laert_tidspunkt__isnull=True).count()",
            "egne(Feilbankrad, bruker).exists()",
            'Feilbankrad: "sporsmal__quiz__notat__emne__eier",',
        ]
        for linje in skriving:
            with self.subTest(skriving=linje):
                self.assertTrue(self.MONSTER.search(linje))
        for linje in lesing:
            with self.subTest(lesing=linje):
                self.assertFalse(self.MONSTER.search(linje))

    def test_ingen_andre_skriver_til_feilbankrad(self):
        rot = Path(settings.BASE_DIR)
        treff = []
        for app in self.APPER:
            self.assertTrue((rot / app).is_dir(), f"Fant ikke appen {app}.")
            for fil in (rot / app).rglob("*.py"):
                relativ = fil.relative_to(rot)
                deler = set(relativ.parts)
                if (
                    relativ in self.TILLATT
                    or "migrations" in deler
                    or "tests" in deler
                    or fil.name.startswith("tests")
                ):
                    continue
                for nr, linje in enumerate(
                    fil.read_text(encoding="utf-8").splitlines(), 1
                ):
                    if self.MONSTER.search(linje):
                        treff.append(f"{relativ}:{nr}: {linje.strip()}")
        self.assertEqual(treff, [])
