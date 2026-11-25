import copy
import dataclasses
import json

from django.test import SimpleTestCase

from ki import KIFeil, QuizUtkast, sjekk
from ki.format import Alternativ, Sporsmal

ANTALL = 5


def lag_svar(antall=ANTALL):
    return {
        "sprak": "nb",
        "modell": "claude-sonnet-5-5",
        "prompt_versjon": "1",
        "sporsmal": [
            {
                "tekst": f"Spørsmål {nr}?",
                "begrunnelse": f"Fordi {nr}.",
                "alternativer": [
                    {"tekst": f"Riktig {nr}", "er_riktig": True},
                    {"tekst": f"Feil A {nr}", "er_riktig": False},
                    {"tekst": f"Feil B {nr}", "er_riktig": False},
                ],
            }
            for nr in range(1, antall + 1)
        ],
    }


class SjekkTest(SimpleTestCase):
    def assertFormatfeil(self, svar, antall=ANTALL):
        raatt = svar if isinstance(svar, str) else json.dumps(svar)
        with self.assertRaises(KIFeil) as fanget:
            sjekk(raatt, antall)
        self.assertEqual(fanget.exception.kode, "format")

    def test_gyldig_svar_gir_quizutkast_med_alle_felt(self):
        utkast = sjekk(json.dumps(lag_svar()), ANTALL)
        self.assertIsInstance(utkast, QuizUtkast)
        self.assertEqual(utkast.sprak, "nb")
        self.assertEqual(utkast.modell, "claude-sonnet-5-5")
        self.assertEqual(utkast.prompt_versjon, "1")
        self.assertIs(utkast.forhandslagret, False)
        self.assertEqual(len(utkast.sporsmal), ANTALL)
        forste = utkast.sporsmal[0]
        self.assertIsInstance(forste, Sporsmal)
        self.assertEqual(forste.tekst, "Spørsmål 1?")
        self.assertEqual(forste.begrunnelse, "Fordi 1.")
        self.assertEqual(
            forste.alternativer,
            (
                Alternativ("Riktig 1", True),
                Alternativ("Feil A 1", False),
                Alternativ("Feil B 1", False),
            ),
        )

    def test_forhandslagret_leses_nar_feltet_finnes(self):
        svar = lag_svar()
        svar["forhandslagret"] = True
        self.assertIs(sjekk(json.dumps(svar), ANTALL).forhandslagret, True)

    def test_utkastet_er_uforanderlig(self):
        utkast = sjekk(json.dumps(lag_svar()), ANTALL)
        for objekt, felt in (
            (utkast, "sprak"),
            (utkast.sporsmal[0], "tekst"),
            (utkast.sporsmal[0].alternativer[0], "er_riktig"),
        ):
            with (
                self.subTest(felt=felt),
                self.assertRaises(dataclasses.FrozenInstanceError),
            ):
                setattr(objekt, felt, None)
        self.assertIsInstance(utkast.sporsmal, tuple)
        self.assertIsInstance(utkast.sporsmal[0].alternativer, tuple)

    def test_ugyldig_json(self):
        for raatt in ("{ikke json", "", "[]", '"tekst"', "null"):
            with self.subTest(raatt=raatt):
                self.assertFormatfeil(raatt)

    def test_feil_antall_sporsmal(self):
        for antall in (ANTALL - 1, ANTALL + 1):
            with self.subTest(antall=antall):
                self.assertFormatfeil(lag_svar(antall))

    def test_feil_antall_alternativer(self):
        to = lag_svar()
        del to["sporsmal"][2]["alternativer"][2]
        fire = lag_svar()
        fire["sporsmal"][2]["alternativer"].append(
            {"tekst": "Ekstra", "er_riktig": False}
        )
        for navn, svar in (("2", to), ("4", fire)):
            with self.subTest(alternativer=navn):
                self.assertFormatfeil(svar)

    def test_feil_antall_riktige(self):
        null = lag_svar()
        null["sporsmal"][1]["alternativer"][0]["er_riktig"] = False
        to = lag_svar()
        to["sporsmal"][1]["alternativer"][1]["er_riktig"] = True
        for navn, svar in (("0", null), ("2", to)):
            with self.subTest(riktige=navn):
                self.assertFormatfeil(svar)

    def test_like_alternativer(self):
        svar = lag_svar()
        svar["sporsmal"][0]["alternativer"][2]["tekst"] = "  riktig 1 "
        self.assertFormatfeil(svar)

    def test_like_alternativer_med_ulike_mellomrom_inni(self):
        svar = lag_svar()
        svar["sporsmal"][0]["alternativer"][2]["tekst"] = "Riktig  1"
        self.assertFormatfeil(svar)

    def test_tekstfelt_strippes(self):
        svar = lag_svar()
        svar["sprak"] = "  nb \n"
        svar["modell"] = " claude-sonnet-5-5 "
        svar["prompt_versjon"] = " 1 "
        svar["sporsmal"][0]["tekst"] = "\t Spørsmål 1? "
        svar["sporsmal"][0]["begrunnelse"] = " Fordi 1. \n"
        svar["sporsmal"][0]["alternativer"][0]["tekst"] = "  Riktig 1  "
        utkast = sjekk(json.dumps(svar), ANTALL)
        self.assertEqual(utkast.sprak, "nb")
        self.assertEqual(utkast.modell, "claude-sonnet-5-5")
        self.assertEqual(utkast.prompt_versjon, "1")
        self.assertEqual(utkast.sporsmal[0].tekst, "Spørsmål 1?")
        self.assertEqual(utkast.sporsmal[0].begrunnelse, "Fordi 1.")
        self.assertEqual(utkast.sporsmal[0].alternativer[0].tekst, "Riktig 1")

    def test_dypt_nostet_json_gir_formatfeil(self):
        self.assertFormatfeil("[" * 100_000 + "]" * 100_000)

    def test_like_sporsmal(self):
        svar = lag_svar()
        svar["sporsmal"][3]["tekst"] = " SPØRSMÅL 1? "
        self.assertFormatfeil(svar)

    def test_manglende_eller_tomme_felt(self):
        stier = [
            ("sprak",),
            ("modell",),
            ("prompt_versjon",),
            ("sporsmal",),
            ("sporsmal", 0, "tekst"),
            ("sporsmal", 0, "begrunnelse"),
            ("sporsmal", 0, "alternativer"),
            ("sporsmal", 0, "alternativer", 1, "tekst"),
            ("sporsmal", 0, "alternativer", 1, "er_riktig"),
        ]
        for sti in stier:
            *forelder_sti, felt = sti
            for variant in ("fjernet", "tom streng", "bare mellomrom"):
                svar = copy.deepcopy(lag_svar())
                forelder = svar
                for steg in forelder_sti:
                    forelder = forelder[steg]
                if variant == "fjernet":
                    del forelder[felt]
                else:
                    forelder[felt] = "" if variant == "tom streng" else "   "
                with self.subTest(felt=".".join(map(str, sti)), variant=variant):
                    self.assertFormatfeil(svar)

    def test_feil_type(self):
        tilfeller = {
            "er_riktig som streng": lambda s: s["sporsmal"][0]["alternativer"][
                0
            ].update(er_riktig="true"),
            "er_riktig som tall": lambda s: s["sporsmal"][0]["alternativer"][0].update(
                er_riktig=1
            ),
            "sporsmal som objekt": lambda s: s.update(sporsmal={"tekst": "Hva?"}),
            "spørsmål som streng": lambda s: s["sporsmal"].__setitem__(0, "Hva?"),
            "alternativ som streng": lambda s: s["sporsmal"][0][
                "alternativer"
            ].__setitem__(0, "Riktig"),
            "tekst som tall": lambda s: s["sporsmal"][0].update(tekst=42),
            "prompt_versjon som tall": lambda s: s.update(prompt_versjon=1),
            "forhandslagret som streng": lambda s: s.update(forhandslagret="false"),
        }
        for navn, endre in tilfeller.items():
            svar = lag_svar()
            endre(svar)
            with self.subTest(navn):
                self.assertFormatfeil(svar)
