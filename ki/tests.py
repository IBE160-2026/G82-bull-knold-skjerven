import ast
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase, override_settings

import ki

KI_MAPPE = Path(ki.__file__).resolve().parent
FORBUDTE_PAKKER = {"studier", "kontoer"}


class TestmodusTest(SimpleTestCase):
    @override_settings(TESTMODUS="0", ANTHROPIC_API_KEY="sk-ant-test")
    def test_testmodus_er_tvunget_i_tester(self):
        self.assertTrue(ki.er_testmodus())


@mock.patch.object(ki, "_tvunget", False)
class TestmodusUtenTvangTest(SimpleTestCase):
    @override_settings(TESTMODUS="", ANTHROPIC_API_KEY="")
    def test_uten_env_er_testmodus_pa(self):
        self.assertTrue(ki.er_testmodus())

    @override_settings(TESTMODUS="0", ANTHROPIC_API_KEY="   ")
    def test_nokkel_med_bare_mellomrom_regnes_som_manglende(self):
        self.assertTrue(ki.er_testmodus())

    def test_sanne_verdier_gir_testmodus_selv_med_nokkel(self):
        for verdi in ("1", "true", "yes", "on", "TRUE", "Yes", "oN", " on "):
            with (
                self.subTest(verdi=verdi),
                override_settings(TESTMODUS=verdi, ANTHROPIC_API_KEY="sk-ant"),
            ):
                self.assertTrue(ki.er_testmodus())

    def test_av_med_nokkel(self):
        for verdi in ("0", "", "false", "nei", "off"):
            with (
                self.subTest(verdi=verdi),
                override_settings(TESTMODUS=verdi, ANTHROPIC_API_KEY="sk-ant"),
            ):
                self.assertFalse(ki.er_testmodus())

    @override_settings(TESTMODUS="0", ANTHROPIC_API_KEY="sk-ant-test")
    def test_tving_testmodus_gjelder_uansett_miljo(self):
        self.assertFalse(ki.er_testmodus())
        ki.tving_testmodus()
        self.assertTrue(ki.er_testmodus())


class KiIsolasjonTest(SimpleTestCase):
    def test_ki_importerer_aldri_fra_studier_eller_kontoer(self):
        filer = sorted(KI_MAPPE.rglob("*.py"))
        self.assertTrue(filer)
        for fil in filer:
            tre = ast.parse(fil.read_text(encoding="utf-8"), filename=str(fil))
            for node in ast.walk(tre):
                if isinstance(node, ast.Import):
                    moduler = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    moduler = [node.module or ""]
                else:
                    continue
                for modul in moduler:
                    with self.subTest(fil=fil.name, modul=modul):
                        self.assertNotIn(modul.split(".")[0], FORBUDTE_PAKKER)
