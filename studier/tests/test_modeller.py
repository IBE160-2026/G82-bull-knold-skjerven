import re

from django.db import IntegrityError, transaction
from django.test import TestCase

from studier.models import (
    Alternativ,
    Emne,
    Feilbankrad,
    Genereringsjobb,
    Notat,
    Okt,
    Oktstatus,
    Okttype,
    Quiz,
    Sporsmal,
    Svar,
    notatfil_sti,
)
from studier.tests.fabrikk import lag_bruker, lag_kjede


class IntegritetsTestCase(TestCase):
    def assertIntegrityError(self, lag):
        with self.assertRaises(IntegrityError), transaction.atomic():
            lag()


class EmneTest(IntegritetsTestCase):
    def setUp(self):
        self.ola = lag_bruker("ola@eks.no")
        self.kari = lag_bruker("kari@eks.no")

    def test_likt_navn_uansett_store_og_sma_bokstaver_gir_integrityerror(self):
        Emne.objects.create(eier=self.ola, navn="HTML")
        self.assertIntegrityError(
            lambda: Emne.objects.create(eier=self.ola, navn="html")
        )

    def test_to_brukere_kan_ha_samme_navn(self):
        Emne.objects.create(eier=self.ola, navn="HTML")
        Emne.objects.create(eier=self.kari, navn="HTML")
        self.assertEqual(Emne.objects.filter(navn="HTML").count(), 2)

    def test_samme_emne_kan_fa_nytt_navn_med_andre_bokstaver(self):
        emne = Emne.objects.create(eier=self.ola, navn="HTML")
        emne.navn = "html"
        emne.save()
        emne.refresh_from_db()
        self.assertEqual(emne.navn, "html")


class OktTest(IntegritetsTestCase):
    def setUp(self):
        self.kjede = lag_kjede(lag_bruker())
        self.notat = self.kjede[Notat]
        self.quiz = self.kjede[Quiz]
        # Kjeden har allerede ett påbegynt forsøk på quizen.

    def test_to_pabegynte_forsok_pa_samme_quiz_gir_integrityerror(self):
        self.assertIntegrityError(
            lambda: Okt.objects.create(
                notat=self.notat, quiz=self.quiz, type=Okttype.FORSOK
            )
        )

    def test_nytt_forsok_er_lov_nar_det_forrige_er_levert(self):
        Okt.objects.filter(pk=self.kjede[Okt].pk).update(status=Oktstatus.LEVERT)
        Okt.objects.create(notat=self.notat, quiz=self.quiz, type=Okttype.FORSOK)
        self.assertEqual(self.quiz.okter.count(), 2)

    def test_to_pabegynte_ovinger_pa_samme_notat_gir_integrityerror(self):
        Okt.objects.create(notat=self.notat, type=Okttype.OVING)
        self.assertIntegrityError(
            lambda: Okt.objects.create(notat=self.notat, type=Okttype.OVING)
        )

    def test_ny_oving_er_lov_nar_den_forrige_er_levert(self):
        Okt.objects.create(
            notat=self.notat, type=Okttype.OVING, status=Oktstatus.LEVERT
        )
        Okt.objects.create(notat=self.notat, type=Okttype.OVING)
        self.assertEqual(self.notat.okter.filter(type=Okttype.OVING).count(), 2)

    def test_forsok_uten_quiz_gir_integrityerror(self):
        self.assertIntegrityError(
            lambda: Okt.objects.create(
                notat=self.notat, type=Okttype.FORSOK, status=Oktstatus.LEVERT
            )
        )

    def test_oving_med_quiz_gir_integrityerror(self):
        self.assertIntegrityError(
            lambda: Okt.objects.create(
                notat=self.notat, quiz=self.quiz, type=Okttype.OVING
            )
        )

    def test_standardverdier(self):
        okt = Okt.objects.create(notat=self.notat, type=Okttype.OVING)
        self.assertEqual(okt.innhold, [])
        self.assertEqual(okt.status, Oktstatus.PABEGYNT)
        self.assertIsNotNone(okt.sist_endret)
        self.assertIsNone(okt.levert_tidspunkt)
        self.assertIsNone(okt.poengsum)


class QuizOgSporsmalTest(IntegritetsTestCase):
    def setUp(self):
        self.kjede = lag_kjede(lag_bruker())

    def test_en_quiz_per_jobb(self):
        quiz = self.kjede[Quiz]
        self.assertIntegrityError(
            lambda: Quiz.objects.create(
                notat=quiz.notat,
                jobb=quiz.jobb,
                vanskelighetsgrad="lett",
                sprak="nb",
                modell="m",
                prompt_versjon="1",
            )
        )

    def test_hoyst_ett_riktig_alternativ(self):
        self.assertIntegrityError(
            lambda: Alternativ.objects.create(
                sporsmal=self.kjede[Sporsmal], tekst="Også riktig", er_riktig=True
            )
        )

    def test_flere_gale_alternativer_er_lov(self):
        Alternativ.objects.create(sporsmal=self.kjede[Sporsmal], tekst="Galt")
        self.assertEqual(self.kjede[Sporsmal].alternativer.count(), 3)

    def test_sporsmal_sorteres_pa_id(self):
        quiz = self.kjede[Quiz]
        andre = Sporsmal.objects.create(quiz=quiz, tekst="A", begrunnelse="b")
        tredje = Sporsmal.objects.create(quiz=quiz, tekst="0", begrunnelse="b")
        self.assertEqual(
            list(quiz.sporsmal.all()), [self.kjede[Sporsmal], andre, tredje]
        )

    def test_meldt_tidspunkt_er_tomt_som_standard(self):
        self.assertIsNone(self.kjede[Sporsmal].meldt_tidspunkt)


class SvarOgFeilbankTest(IntegritetsTestCase):
    def setUp(self):
        self.kjede = lag_kjede(lag_bruker())

    def test_ett_svar_per_sporsmal_per_okt(self):
        svar = self.kjede[Svar]
        self.assertIntegrityError(
            lambda: Svar.objects.create(
                okt=svar.okt, sporsmal=svar.sporsmal, alternativ=svar.alternativ
            )
        )

    def test_hendelse_er_tom_til_levering(self):
        self.assertEqual(self.kjede[Svar].hendelse, "")

    def test_hoyst_en_feilbankrad_per_sporsmal(self):
        self.assertIntegrityError(
            lambda: Feilbankrad.objects.create(sporsmal=self.kjede[Sporsmal])
        )

    def test_feilbankrad_standardverdier(self):
        rad = self.kjede[Feilbankrad]
        self.assertEqual(rad.riktige_pa_rad, 0)
        self.assertIsNone(rad.laert_tidspunkt)
        self.assertIsNotNone(rad.opprettet)


class CascadeTest(TestCase):
    def test_sletting_av_emne_sletter_alt_under_og_ikke_andre_emner(self):
        bruker = lag_bruker()
        kjede = lag_kjede(bruker, "HTML")
        annen = lag_kjede(bruker, "CSS")
        kjede[Emne].delete()
        for modell in (
            Notat,
            Genereringsjobb,
            Quiz,
            Sporsmal,
            Alternativ,
            Okt,
            Svar,
            Feilbankrad,
        ):
            with self.subTest(modell=modell.__name__):
                self.assertFalse(modell.objects.filter(pk=kjede[modell].pk).exists())
                self.assertTrue(modell.objects.filter(pk=annen[modell].pk).exists())


class NotatfilStiTest(TestCase):
    def test_sti_er_eier_id_og_uuid_med_endelse(self):
        bruker = lag_bruker()
        notat = Notat(emne=Emne(eier=bruker, navn="HTML"))
        sti = notatfil_sti(notat, "Forelesning 1.PDF")
        self.assertRegex(
            sti,
            rf"^notater/{bruker.pk}/[0-9a-f]{{8}}-[0-9a-f]{{4}}-4[0-9a-f]{{3}}"
            rf"-[0-9a-f]{{4}}-[0-9a-f]{{12}}\.pdf$",
        )

    def test_to_filer_med_samme_navn_far_ulik_sti(self):
        notat = Notat(emne=Emne(eier=lag_bruker(), navn="HTML"))
        self.assertNotEqual(notatfil_sti(notat, "a.txt"), notatfil_sti(notat, "a.txt"))

    def test_originalnavnet_er_ikke_med_i_stien(self):
        notat = Notat(emne=Emne(eier=lag_bruker(), navn="HTML"))
        self.assertIsNone(re.search("hemmelig", notatfil_sti(notat, "hemmelig.docx")))
