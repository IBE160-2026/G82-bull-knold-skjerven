import hashlib
import re
import tempfile
from pathlib import Path

import docx
from django.conf import settings
from django.test import SimpleTestCase

from ki import Innhold, KIFeil, les_fil
from ki.feil import KODER

TESTDOKUMENTER = Path(settings.BASE_DIR) / "testdokumenter"
TEKST_PDF = TESTDOKUMENTER / "html-struktur-og-semantikk.pdf"
LYSBILDE_PDF = TESTDOKUMENTER / "css-layout-lysbilder.pdf"
SKANNET_PDF = TESTDOKUMENTER / "http-skannet.pdf"
DOCX = TESTDOKUMENTER / "universell-utforming.docx"
TXT = TESTDOKUMENTER / "javascript-og-dom.txt"


class KIFeilTest(SimpleTestCase):
    def test_kjente_koder_godtas(self):
        self.assertEqual(
            KODER,
            {
                "timeout",
                "format",
                "for_lite_innhold",
                "for_stor",
                "api_nokkel",
                "api_feil",
            },
        )
        for kode in KODER:
            with self.subTest(kode=kode):
                self.assertEqual(KIFeil(kode).kode, kode)

    def test_ukjent_kode_gir_valueerror(self):
        for kode in ("ukjent", "", "FORMAT", None):
            with self.subTest(kode=kode), self.assertRaises(ValueError):
                KIFeil(kode)


class LesFilTest(SimpleTestCase):
    def setUp(self):
        mappe = tempfile.TemporaryDirectory()
        self.addCleanup(mappe.cleanup)
        self.mappe = Path(mappe.name)

    def assertKIFeil(self, kode, sti):
        with self.assertRaises(KIFeil) as fanget:
            les_fil(sti)
        self.assertEqual(fanget.exception.kode, kode)

    def test_pdf_gir_hele_filen_som_bytes(self):
        for sti in (TEKST_PDF, LYSBILDE_PDF, SKANNET_PDF):
            with self.subTest(fil=sti.name):
                raa = sti.read_bytes()
                innhold = les_fil(sti)
                self.assertEqual(innhold.type, "pdf")
                self.assertIsInstance(innhold.data, bytes)
                self.assertEqual(innhold.data, raa)
                self.assertEqual(innhold.sha256, hashlib.sha256(raa).hexdigest())

    def test_docx_gir_avsnittene_med_linjeskift_mellom(self):
        innhold = les_fil(DOCX)
        self.assertEqual(innhold.type, "docx")
        self.assertIsInstance(innhold.data, str)
        self.assertEqual(innhold.sha256, hashlib.sha256(DOCX.read_bytes()).hexdigest())
        self.assertEqual(
            innhold.data.split("\n")[:3],
            [
                "Universell utforming av nettsider",
                "Webutvikling, forelesning 7. Notater skrevet av gruppe G82.",
                "Hva og hvorfor",
            ],
        )
        self.assertIn("\nWCAG\n", innhold.data)

    def test_txt_utf8_med_og_uten_bom(self):
        for koding in ("utf-8", "utf-8-sig"):
            sti = self.mappe / f"{koding}.txt"
            sti.write_bytes("Blåbærsyltetøy og ÆØÅ".encode(koding))
            with self.subTest(koding=koding):
                self.assertEqual(les_fil(sti).data, "Blåbærsyltetøy og ÆØÅ")

    def test_txt_utf8(self):
        innhold = les_fil(TXT)
        self.assertEqual(innhold.type, "txt")
        self.assertEqual(innhold.data, TXT.read_bytes().decode("utf-8"))
        self.assertTrue(innhold.data.startswith("JavaScript and the DOM"))

    def test_txt_cp1252_som_reserve(self):
        sti = self.mappe / "notat.txt"
        sti.write_bytes("Blåbærsyltetøy og ÆØÅ".encode("cp1252"))
        innhold = les_fil(sti)
        self.assertEqual(innhold.data, "Blåbærsyltetøy og ÆØÅ")
        self.assertEqual(innhold.sha256, hashlib.sha256(sti.read_bytes()).hexdigest())

    def test_fil_mangler_gir_api_feil(self):
        self.assertKIFeil("api_feil", self.mappe / "finnes-ikke.pdf")

    def test_tom_tekst_gir_for_lite_innhold(self):
        txt = self.mappe / "tom.txt"
        txt.write_bytes(b" \r\n\t \n")
        self.assertKIFeil("for_lite_innhold", txt)

        tom_docx = self.mappe / "tom.docx"
        dokument = docx.Document()
        dokument.add_paragraph("   ")
        dokument.add_paragraph("")
        dokument.save(str(tom_docx))
        self.assertKIFeil("for_lite_innhold", tom_docx)

    def test_typen_bestemmes_av_endelsen_uansett_store_bokstaver(self):
        sti = self.mappe / "NOTAT.TxT"
        sti.write_text("Hei", encoding="utf-8")
        self.assertEqual(les_fil(sti).type, "txt")

    def test_ukjent_endelse_gir_api_feil(self):
        for navn in ("notat.pptx", "notat.mp4", "notat"):
            sti = self.mappe / navn
            sti.write_bytes(b"innhold")
            with self.subTest(navn=navn):
                self.assertKIFeil("api_feil", sti)

    def test_odelagt_docx_gir_api_feil(self):
        sti = self.mappe / "odelagt.docx"
        sti.write_bytes(b"ikke en zip-fil")
        self.assertKIFeil("api_feil", sti)

    def test_innhold_er_uforanderlig(self):
        innhold = les_fil(TXT)
        self.assertIsInstance(innhold, Innhold)
        with self.assertRaises(AttributeError):
            innhold.data = "noe annet"


class TestdokumenterTest(SimpleTestCase):
    def test_alle_fem_testdokumentene_kan_leses(self):
        typer = {}
        for sti in (TEKST_PDF, LYSBILDE_PDF, SKANNET_PDF, DOCX, TXT):
            with self.subTest(fil=sti.name):
                innhold = les_fil(sti)
                self.assertTrue(innhold.data)
                typer[sti.name] = innhold.type
        self.assertEqual(sorted(typer.values()), ["docx", "pdf", "pdf", "pdf", "txt"])

    def kilderad(self, navn):
        kilder = (TESTDOKUMENTER / "KILDER.md").read_text(encoding="utf-8")
        rader = [r for r in kilder.splitlines() if r.startswith(f"| `{navn}`")]
        self.assertEqual(len(rader), 1, f"{navn} mangler i tabellen i KILDER.md")
        return rader[0]

    def test_hver_fil_star_i_kilder_med_kilde_og_lisens(self):
        filer = [
            f
            for f in TESTDOKUMENTER.iterdir()
            if f.is_file()
            and not f.name.startswith(".")
            and f.name.lower() != "desktop.ini"
            and f.name != "KILDER.md"
        ]
        self.assertEqual(len(filer), 5)
        for fil in filer:
            with self.subTest(fil=fil.name):
                rad = self.kilderad(fil.name)
                self.assertIn("laget av gruppa G82", rad)
                self.assertIn("CC BY 4.0", rad)

    def test_pdf_formen_stemmer_med_kilder(self):
        for sti, sider in ((TEKST_PDF, 10), (LYSBILDE_PDF, 11), (SKANNET_PDF, 2)):
            with self.subTest(fil=sti.name):
                raa = sti.read_bytes()
                antall = max(int(n) for n in re.findall(rb"/Count (\d+)", raa))
                self.assertEqual(antall, sider)
                oppgitt = re.search(
                    r"(\d+) (?:liggende )?sider", self.kilderad(sti.name)
                )
                self.assertEqual(int(oppgitt.group(1)), sider)

    def test_lysbilde_pdf_er_liggende(self):
        boks = re.search(rb"/MediaBox\s*\[\s*([\d.\s]+)\]", LYSBILDE_PDF.read_bytes())
        _, _, bredde, hoyde = (float(t) for t in boks.group(1).split())
        self.assertGreater(bredde, hoyde)

    def test_skannet_pdf_har_ingen_fonter(self):
        self.assertNotIn(b"/Font", SKANNET_PDF.read_bytes())
