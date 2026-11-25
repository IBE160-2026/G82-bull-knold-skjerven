"""Tester for å starte og svare på en quiz (FR-17, FR-18, AD-6, AD-16, AD-17, AD-20), én per rad i I/O-matrisen i spec 3.1."""

import re
from datetime import timedelta
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

import ki
from farequiz import feilmeldinger
from studier.models import Alternativ, Emne, Okt, Oktstatus, Okttype, Quiz, Svar
from studier.services import okter
from studier.services.generering import generer_synkront, kjor_steg, opprett_jobb
from studier.services.notater import last_opp
from studier.services.okter import (
    OktErLevert,
    SvarAvvist,
    forste_ubesvarte,
    lagre_svar,
    start_eller_fortsett_okt,
)
from studier.tests.fabrikk import lag_bruker
from studier.tests.test_generering import GenereringTestCase, _quiz_json, _raatt
from studier.tests.test_slett_emne import _innlogget

LABEL = re.compile(r"<label[^>]*>.*?</label>", re.DOTALL)


class OktTestCase(GenereringTestCase):
    def setUp(self):
        super().setUp()
        self.quiz = self._quiz(self.notat)

    def _quiz(self, notat, antall=5, raatt=None):
        with mock.patch.object(ki, "generer", return_value=raatt or _raatt(antall)):
            return generer_synkront(notat, "middels", antall)

    def _okt(self, quiz=None):
        return start_eller_fortsett_okt(quiz or self.quiz)

    def _url(self, okt, nr):
        return f"/okter/{okt.pk}/sporsmal/{nr}/"

    def _rad(self, okt, nr):
        """(spørsmål, [alternativer i visningsrekkefølge]) for nr."""
        rad = okt.innhold[nr - 1]
        sporsmal = self.quiz.sporsmal.get(pk=rad["sporsmal"])
        alternativer = [Alternativ.objects.get(pk=pk) for pk in rad["alternativer"]]
        return sporsmal, alternativer

    def _svar(self, okt, nr, retning="neste", alternativ=None):
        data = {"retning": retning}
        if alternativ is not None:
            data["alternativ"] = str(alternativ.pk)
        return self.client.post(self._url(okt, nr), data)

    def _annen_bruker(self):
        annen = _innlogget(lag_bruker("annen@eks.no"))
        emne = Emne.objects.create(eier=annen, navn="Annet")
        notat = last_opp(emne, SimpleUploadedFile("hemmelig.txt", b"Hemmelig."), annen)
        return annen, self._quiz(notat)


class StartTest(OktTestCase):
    def test_start_lager_okt_med_innhold_og_sender_til_nr_1(self):
        svar = self.client.post(f"/quizer/{self.quiz.pk}/start/")
        okt = Okt.objects.get()
        self.assertRedirects(svar, self._url(okt, 1))
        self.assertEqual(okt.type, Okttype.FORSOK)
        self.assertEqual(okt.status, Oktstatus.PABEGYNT)
        self.assertEqual(okt.notat, self.notat)
        self.assertEqual(okt.quiz, self.quiz)
        sporsmal = list(self.quiz.sporsmal.order_by("id"))
        self.assertEqual(len(okt.innhold), 5)
        self.assertEqual([r["sporsmal"] for r in okt.innhold], [s.pk for s in sporsmal])
        for rad, s in zip(okt.innhold, sporsmal, strict=True):
            self.assertEqual(len(rad["alternativer"]), 3)
            self.assertCountEqual(
                rad["alternativer"], s.alternativer.values_list("pk", flat=True)
            )

    def test_alternativene_stokkes(self):
        with mock.patch.object(
            okter.random, "shuffle", side_effect=lambda liste: liste.reverse()
        ) as stokk:
            okt = self._okt()
        self.assertEqual(stokk.call_count, 5)
        for rad in okt.innhold:
            ids = list(
                Alternativ.objects.filter(sporsmal_id=rad["sporsmal"])
                .order_by("pk")
                .values_list("pk", flat=True)
            )
            self.assertEqual(rad["alternativer"], ids[::-1])

    def test_start_igjen_fortsetter_og_sender_til_forste_ubesvarte(self):
        okt = self._okt()
        for nr in (1, 2):
            sporsmal, alternativer = self._rad(okt, nr)
            lagre_svar(okt, sporsmal, alternativer[0])
        innhold = okt.innhold
        svar = self.client.post(f"/quizer/{self.quiz.pk}/start/")
        self.assertRedirects(svar, self._url(okt, 3))
        self.assertEqual(Okt.objects.count(), 1)
        okt.refresh_from_db()
        self.assertEqual(okt.innhold, innhold)

    def test_alle_besvart_gir_nr_1(self):
        okt = self._okt()
        for nr in range(1, 6):
            sporsmal, alternativer = self._rad(okt, nr)
            lagre_svar(okt, sporsmal, alternativer[1])
        self.assertEqual(forste_ubesvarte(okt), 1)
        svar = self.client.post(f"/quizer/{self.quiz.pk}/start/")
        self.assertRedirects(svar, self._url(okt, 1))

    def test_samtidig_start_gir_den_eksisterende_okten(self):
        forste = self._okt()
        ekte = okter._pabegynt_forsok
        kall = []

        def ser_ingen_forste_gang(quiz):
            # Det andre kallet ser ikke økten før det prøver å lage sin egen.
            kall.append(quiz)
            return None if len(kall) == 1 else ekte(quiz)

        with mock.patch.object(
            okter, "_pabegynt_forsok", side_effect=ser_ingen_forste_gang
        ):
            andre = self._okt()
        self.assertEqual(len(kall), 2)  # Unntaket kom, og økten ble hentet.
        self.assertEqual(andre, forste)
        self.assertEqual(Okt.objects.count(), 1)

    def test_start_tar_bare_post(self):
        svar = self.client.get(f"/quizer/{self.quiz.pk}/start/")
        self.assertEqual(svar.status_code, 405)
        self.assertFalse(Okt.objects.exists())

    def test_quizkortet_har_ta_quiz_skjema(self):
        html = self.client.get(self.notat_url).content.decode()
        self.assertIn(
            f'<form method="post" action="/quizer/{self.quiz.pk}/start/"', html
        )
        self.assertIn(">Ta quiz</button>", html)
        self.assertNotIn("Ta quizen", html)
        skjema = html.index(
            f'<form method="post" action="/quizer/{self.quiz.pk}/start/"'
        )
        knapp = html.index(">Ta quiz</button>", skjema)
        self.assertIn('name="csrfmiddlewaretoken"', html[skjema:knapp])


class SvareTest(OktTestCase):
    def setUp(self):
        super().setUp()
        self.okt = self._okt()

    def test_neste_med_svar_lagrer_og_sender_til_neste(self):
        gammel = timezone.now() - timedelta(hours=1)
        Okt.objects.filter(pk=self.okt.pk).update(sist_endret=gammel)
        sporsmal, alternativer = self._rad(self.okt, 2)
        svar = self._svar(self.okt, 2, alternativ=alternativer[2])
        self.assertRedirects(svar, self._url(self.okt, 3))
        lagret = Svar.objects.get()
        self.assertEqual(lagret.okt, self.okt)
        self.assertEqual(lagret.sporsmal, sporsmal)
        self.assertEqual(lagret.alternativ, alternativer[2])
        self.okt.refresh_from_db()
        self.assertGreater(self.okt.sist_endret, gammel)

    def test_endre_svar_gir_fortsatt_ett_svar(self):
        _, alternativer = self._rad(self.okt, 2)
        self._svar(self.okt, 2, alternativ=alternativer[0])
        self._svar(self.okt, 2, retning="forrige", alternativ=alternativer[1])
        self.assertEqual(Svar.objects.count(), 1)
        self.assertEqual(Svar.objects.get().alternativ, alternativer[1])

    def test_neste_uten_svar_lagrer_ingenting(self):
        svar = self._svar(self.okt, 2)
        self.assertRedirects(svar, self._url(self.okt, 3))
        self.assertFalse(Svar.objects.exists())

    def test_tomt_alternativ_regnes_som_uten_svar(self):
        svar = self.client.post(
            self._url(self.okt, 2), {"retning": "neste", "alternativ": ""}
        )
        self.assertRedirects(svar, self._url(self.okt, 3))
        self.assertFalse(Svar.objects.exists())

    def test_forrige(self):
        self.assertRedirects(
            self._svar(self.okt, 1, retning="forrige"), self._url(self.okt, 1)
        )
        self.assertRedirects(
            self._svar(self.okt, 3, retning="forrige"), self._url(self.okt, 2)
        )

    def test_neste_pa_siste_lagrer_og_sender_til_s10(self):
        sporsmal, alternativer = self._rad(self.okt, 5)
        svar = self._svar(self.okt, 5, alternativ=alternativer[0])
        self.assertRedirects(svar, f"/okter/{self.okt.pk}/lever/")
        self.assertEqual(Svar.objects.get().sporsmal, sporsmal)

    def test_se_over_og_lever_lagrer_valgt_svar_og_sender_til_s10(self):
        sporsmal, alternativer = self._rad(self.okt, 2)
        svar = self._svar(self.okt, 2, retning="lever", alternativ=alternativer[1])
        self.assertRedirects(svar, f"/okter/{self.okt.pk}/lever/")
        lagret = Svar.objects.get()
        self.assertEqual(lagret.sporsmal, sporsmal)
        self.assertEqual(lagret.alternativ, alternativer[1])

    def test_ukjent_retning_gir_400_og_ingenting_lagres(self):
        _, alternativer = self._rad(self.okt, 1)
        for retning in ("", "hopp"):
            with self.subTest(retning=retning):
                svar = self._svar(
                    self.okt, 1, retning=retning, alternativ=alternativer[0]
                )
                self.assertEqual(svar.status_code, 400)
        self.assertFalse(Svar.objects.exists())

    def test_alternativ_fra_annet_sporsmal_gir_400_med_melding(self):
        _, fra_nr_3 = self._rad(self.okt, 3)
        svar = self._svar(self.okt, 2, alternativ=fra_nr_3[0])
        self.assertEqual(svar.status_code, 400)
        html = svar.content.decode()
        self.assertIn("Spørsmål 2 av 5", html)
        self.assertIn(
            f'role="alert" tabindex="-1" autofocus class="mb-4 rounded-md border '
            f'border-error px-4 py-2 font-semibold text-error">'
            f"{feilmeldinger.SVAR_IKKE_LAGRET}</p>",
            html,
        )
        # Bare meldingen får fokus, ikke spørsmålet.
        self.assertEqual(html.count("autofocus"), 1)
        legend = re.search(r"<legend[^>]*>", html).group()
        self.assertNotIn("autofocus", legend)
        # Meldingen står ved knappene.
        self.assertLess(
            html.index(feilmeldinger.SVAR_IKKE_LAGRET), html.index(">Forrige<")
        )
        self.assertFalse(Svar.objects.exists())

    def test_annens_alternativ_gir_404(self):
        _, annens_quiz = self._annen_bruker()
        annens = Alternativ.objects.filter(sporsmal__quiz=annens_quiz).first()
        svar = self._svar(self.okt, 1, alternativ=annens)
        self.assertEqual(svar.status_code, 404)
        self.assertFalse(Svar.objects.exists())

    def test_ukjent_alternativ_gir_404(self):
        for verdi in ("999999", "x"):
            with self.subTest(verdi=verdi):
                svar = self.client.post(
                    self._url(self.okt, 1), {"retning": "neste", "alternativ": verdi}
                )
                self.assertEqual(svar.status_code, 404)
        self.assertFalse(Svar.objects.exists())

    def test_levert_okt_lagrer_ingenting_og_sender_til_s11(self):
        Okt.objects.filter(pk=self.okt.pk).update(status=Oktstatus.LEVERT)
        _, alternativer = self._rad(self.okt, 1)
        svar = self._svar(self.okt, 1, alternativ=alternativer[0])
        self.assertRedirects(
            svar, f"/okter/{self.okt.pk}/resultat/", fetch_redirect_response=False
        )
        self.assertFalse(Svar.objects.exists())

    def test_ukjent_nr_gir_404(self):
        _, alternativer = self._rad(self.okt, 1)
        for nr in (0, 6):
            with self.subTest(nr=nr):
                self.assertEqual(
                    self.client.get(self._url(self.okt, nr)).status_code, 404
                )
                svar = self._svar(self.okt, nr, alternativ=alternativer[0])
                self.assertEqual(svar.status_code, 404)
        svar = self.client.get(f"/okter/{self.okt.pk}/sporsmal/x/")
        self.assertEqual(svar.status_code, 404)
        self.assertFalse(Svar.objects.exists())


class LagreSvarTest(OktTestCase):
    def setUp(self):
        super().setUp()
        self.okt = self._okt()

    def test_avviser_levert_okt(self):
        sporsmal, alternativer = self._rad(self.okt, 1)
        Okt.objects.filter(pk=self.okt.pk).update(status=Oktstatus.LEVERT)
        with self.assertRaises(OktErLevert):
            lagre_svar(self.okt, sporsmal, alternativer[0])
        self.assertFalse(Svar.objects.exists())

    def test_avviser_sporsmal_utenfor_okten(self):
        annen_quiz = self._quiz(self.notat)
        sporsmal = annen_quiz.sporsmal.first()
        with self.assertRaises(SvarAvvist):
            lagre_svar(self.okt, sporsmal, sporsmal.alternativer.first())
        self.assertFalse(Svar.objects.exists())

    def test_avviser_alternativ_fra_annet_sporsmal(self):
        sporsmal, _ = self._rad(self.okt, 1)
        _, fra_nr_2 = self._rad(self.okt, 2)
        with self.assertRaises(SvarAvvist):
            lagre_svar(self.okt, sporsmal, fra_nr_2[0])
        self.assertFalse(Svar.objects.exists())

    def test_svar_avvist_er_valueerror(self):
        self.assertTrue(issubclass(SvarAvvist, ValueError))
        self.assertTrue(issubclass(OktErLevert, SvarAvvist))


class TilgangTest(OktTestCase):
    def test_annens_okt_og_quiz_gir_404_og_ingenting_endres(self):
        _, annens_quiz = self._annen_bruker()
        annens_okt = start_eller_fortsett_okt(annens_quiz)
        rad = annens_okt.innhold[0]
        alternativ = Alternativ.objects.get(pk=rad["alternativer"][0])
        url = self._url(annens_okt, 1)
        self.assertEqual(self.client.get(url).status_code, 404)
        svar = self.client.post(url, {"retning": "neste", "alternativ": alternativ.pk})
        self.assertEqual(svar.status_code, 404)
        self.assertEqual(
            self.client.get(f"/okter/{annens_okt.pk}/lever/").status_code, 404
        )
        svar = self.client.post(f"/quizer/{annens_quiz.pk}/start/")
        self.assertEqual(svar.status_code, 404)
        self.assertContains(svar, "Fant ikke siden", status_code=404)
        self.assertEqual(Okt.objects.count(), 1)
        self.assertFalse(Svar.objects.exists())


class EtterGenereringTest(OktTestCase):
    def test_ferdig_jobb_gir_hx_redirect_til_nr_1_og_en_okt_for_begge_faner(self):
        jobb = opprett_jobb(self.notat, "lett", 5)
        with mock.patch.object(ki, "generer", return_value=_raatt(5)):
            for _ in range(2):
                kjor_steg(jobb.pk)
            forste = self._steg(jobb)
        jobb.refresh_from_db()
        okt = Okt.objects.get(quiz=jobb.quiz)
        self.assertEqual(forste["HX-Redirect"], self._url(okt, 1))
        # En annen fane spør etter at jobben er ferdig.
        andre = self._steg(jobb)
        self.assertEqual(andre["HX-Redirect"], self._url(okt, 1))
        self.assertEqual(Okt.objects.filter(quiz=jobb.quiz).count(), 1)

    def test_s8_get_for_ferdig_jobb_sender_til_s7_uten_okt(self):
        svar = self.client.get(f"/jobber/{self.quiz.jobb.pk}/")
        self.assertRedirects(svar, self.notat_url)
        self.assertFalse(Okt.objects.exists())


class S9Test(OktTestCase):
    def setUp(self):
        super().setUp()
        self.okt = self._okt()

    def _html(self, nr):
        svar = self.client.get(self._url(self.okt, nr))
        self.assertEqual(svar.status_code, 200)
        return svar.content.decode()

    def test_s9_viser_ki_merke_posisjon_reiserute_og_sporsmal(self):
        sporsmal, _ = self._rad(self.okt, 3)
        html = self._html(3)
        self.assertIn(
            "Laget av KI (claude-test). Spørsmålene kan inneholde feil.", html
        )
        self.assertIn("<title>Spørsmål 3 av 5 – notat.txt – FåreQuiz</title>", html)
        self.assertIn(">Spørsmål 3 av 5</h1>", html)
        self.assertIn('<div class="reiserute reiserute-faar" aria-hidden="true">', html)
        self.assertIn('<span style="width: 60%"></span>', html)
        self.assertIn('<svg class="faar" style="left: 60%"', html)
        self.assertIn(
            f'<legend id="sporsmal" class="flashcard" tabindex="-1" autofocus>'
            f"{sporsmal.tekst}</legend>",
            html,
        )
        self.assertLess(html.index("Laget av KI ("), html.index("Spørsmål 3 av 5</h1>"))
        self.assertLess(html.index("Spørsmål 3 av 5</h1>"), html.index("<fieldset"))
        self.assertEqual(html.count('type="radio" name="alternativ"'), 3)
        self.assertIn(
            '<button type="submit" name="retning" value="lever" class="min-h-11 '
            'cursor-pointer font-semibold underline">Se over og lever</button>',
            html,
        )
        # Knappen står i skjemaet, så et valgt svar lagres før S10.
        skjema = re.search(
            r"<form method=\"post\" action=\"/okter/.*?</form>", html, re.DOTALL
        ).group()
        self.assertIn('value="lever"', skjema)
        self.assertIn('name="csrfmiddlewaretoken"', skjema)
        self.assertNotIn('<script src="/static/js/htmx', html)
        self.assertNotIn("hx-", html.split("<main", 1)[1])

    def test_brodsmuler_og_tilbake_gar_til_notatet(self):
        html = self._html(2)
        nav = re.search(
            r'<nav aria-label="Brødsmuler".*?</nav>', html, re.DOTALL
        ).group()
        steg = re.findall(r"<li>(.*?)</li>", nav, re.DOTALL)
        self.assertEqual(len(steg), 4)
        self.assertIn("Oversikt", steg[0])
        self.assertIn(f'href="/emner/{self.emne.pk}/"', steg[1])
        self.assertIn(f'href="{self.notat_url}"', steg[2])
        self.assertIn('<span aria-current="page">Spørsmål 2 av 5</span>', steg[3])
        self.assertIn(f'<a href="{self.notat_url}" class="inline-flex min-h-11', html)

    def test_alternativene_i_rekkefolgen_fra_innhold_og_lagret_svar_valgt(self):
        sporsmal, alternativer = self._rad(self.okt, 1)
        lagre_svar(self.okt, sporsmal, alternativer[1])
        html = self._html(1)
        verdier = re.findall(r'name="alternativ" value="(\d+)"', html)
        self.assertEqual(verdier, [str(a.pk) for a in alternativer])
        self.assertIn(f'value="{alternativer[1].pk}" checked>', html)
        self.assertEqual(html.count(" checked>"), 1)
        for alternativ in alternativer:
            self.assertIn(f"<span>{alternativ.tekst}</span>", html)

    def test_fasit_skjult(self):
        for nr in range(1, 6):
            with self.subTest(nr=nr):
                sporsmal, alternativer = self._rad(self.okt, nr)
                svar = self.client.get(self._url(self.okt, nr))
                html = svar.content.decode()
                self.assertNotIn(sporsmal.begrunnelse, html)
                self.assertNotIn("er_riktig", html)
                etiketter = LABEL.findall(html.split("<main", 1)[1])
                self.assertEqual(len(etiketter), 3)
                # Ingen klasse eller data-* skiller det riktige alternativet ut.
                for etikett in etiketter:
                    self.assertNotIn("data-", etikett)
                    uten_tekst = re.sub(r"<span>.*?</span>", "", etikett)
                    uten_tekst = re.sub(r'value="\d+"', "", uten_tekst)
                    uten_tekst = uten_tekst.replace(" checked", "")
                    self.assertEqual(
                        uten_tekst,
                        '<label class="svaralternativ"><input type="radio" '
                        'name="alternativ" > </label>',
                    )
                # Rekkefølgen er den stokkede, ikke databasens.
                self.assertEqual(
                    re.findall(r'name="alternativ" value="(\d+)"', html),
                    [str(a.pk) for a in alternativer],
                )
                for nokkel in ("begrunnelse", "er_riktig"):
                    self.assertNotIn(nokkel, svar.context)
                for alternativ in svar.context["alternativer"]:
                    self.assertEqual(set(alternativ), {"id", "tekst"})

    def test_riktig_alternativ_har_ingen_fast_posisjon(self):
        posisjoner = set()
        for _ in range(20):
            Okt.objects.all().delete()
            okt = self._okt()
            for rad in okt.innhold:
                riktig = Alternativ.objects.get(
                    sporsmal_id=rad["sporsmal"], er_riktig=True
                )
                posisjoner.add(rad["alternativer"].index(riktig.pk))
        self.assertEqual(posisjoner, {0, 1, 2})

    def test_spraak_en_gir_lang_pa_sporsmal_og_alternativer(self):
        quiz = self._quiz(
            self.notat,
            raatt=ki.RaattSvar(
                tekst=_quiz_json(5, sprak="en"),
                forhandslagret=False,
                modell="claude-test",
                prompt_versjon="7",
            ),
        )
        self.assertEqual(quiz.sprak, "en")
        okt = self._okt(quiz)
        html = self.client.get(self._url(okt, 1)).content.decode()
        self.assertIn('class="flashcard" tabindex="-1" autofocus lang="en">', html)
        self.assertEqual(html.count('<span lang="en">'), 3)

    def test_spraak_nb_gir_ingen_lang(self):
        html = self._html(1)
        main = html.split("<main", 1)[1]
        self.assertNotIn("lang=", main)

    def test_spraakvarianter(self):
        for sprak, forventet in (
            ("nn", None),
            ("no", None),
            ("nb-NO", None),
            ("NB", None),
            ("en-GB", "en-GB"),
        ):
            with self.subTest(sprak=sprak):
                Quiz.objects.filter(pk=self.quiz.pk).update(sprak=sprak)
                main = self._html(1).split("<main", 1)[1]
                if forventet is None:
                    self.assertNotIn("lang=", main)
                else:
                    self.assertIn(
                        f'class="flashcard" tabindex="-1" autofocus lang="{forventet}">',
                        main,
                    )
                    self.assertEqual(main.count(f'<span lang="{forventet}">'), 3)

    def test_enter_i_radiogruppen_gar_til_neste(self):
        # Første knapp i skjemaet er standardknappen ved Enter.
        html = self._html(2)
        skjema = re.search(
            r"<form method=\"post\" action=\"/okter/.*?</form>", html, re.DOTALL
        ).group()
        knapper = re.findall(
            r'<button type="submit" name="retning" value="(\w+)"', skjema
        )
        self.assertEqual(knapper, ["neste", "lever", "forrige", "neste"])

    def test_s10_skall_viser_hvert_sporsmal_som_lenke(self):
        sporsmal, alternativer = self._rad(self.okt, 2)
        lagre_svar(self.okt, sporsmal, alternativer[0])
        svar = self.client.get(f"/okter/{self.okt.pk}/lever/")
        self.assertEqual(svar.status_code, 200)
        html = svar.content.decode()
        self.assertIn("<title>Se over og lever – notat.txt – FåreQuiz</title>", html)
        self.assertIn(">Se over og lever</h1>", html)
        self.assertIn(
            f'href="/okter/{self.okt.pk}/sporsmal/2/" class="inline-flex min-h-11 '
            'items-center font-semibold underline">Spørsmål 2 – besvart</a>',
            html,
        )
        for nr in (1, 3, 4, 5):
            self.assertIn(f"Spørsmål {nr} – ikke besvart</a>", html)
        self.assertIn(">Lever</button>", html)
        nav = re.search(
            r'<nav aria-label="Brødsmuler".*?</nav>', html, re.DOTALL
        ).group()
        self.assertIn(f'href="{self.notat_url}"', nav)
        self.assertIn('<span aria-current="page">Se over og lever</span>', nav)


class HeleQuizenTest(OktTestCase):
    def test_svar_med_neste_og_tilbake_med_forrige_beholder_svar_og_rekkefolge(self):
        svar = self.client.post(f"/quizer/{self.quiz.pk}/start/", follow=True)
        okt = Okt.objects.get()
        rekkefolge = {}
        valgt = {}
        for nr in range(1, 6):
            html = svar.content.decode()
            self.assertIn(f"Spørsmål {nr} av 5", html)
            rekkefolge[nr] = re.findall(r'name="alternativ" value="(\d+)"', html)
            valgt[nr] = rekkefolge[nr][nr % 3]
            svar = self.client.post(
                self._url(okt, nr),
                {"retning": "neste", "alternativ": valgt[nr]},
                follow=True,
            )
        self.assertEqual(svar.redirect_chain[-1][0], f"/okter/{okt.pk}/lever/")
        svar = self.client.get(self._url(okt, 5))
        for nr in range(5, 0, -1):
            html = svar.content.decode()
            self.assertEqual(
                re.findall(r'name="alternativ" value="(\d+)"', html), rekkefolge[nr]
            )
            self.assertIn(f'value="{valgt[nr]}" checked>', html)
            svar = self.client.post(
                self._url(okt, nr), {"retning": "forrige"}, follow=True
            )
        self.assertEqual(Svar.objects.filter(okt=okt).count(), 5)
