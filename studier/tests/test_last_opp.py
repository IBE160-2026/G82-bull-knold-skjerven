"""Tester for å laste opp notat (FR-7, FR-8, AD-14), én per rad i I/O-matrisen i spec 2.3."""

import io
import re
import zipfile
from unittest import mock

import docx
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.http import Http404
from django.utils.html import escape

from farequiz import feilmeldinger
from studier.models import Emne, Notat
from studier.services.notater import MAKS_STORRELSE, last_opp, valider_fil
from studier.tests.fabrikk import lag_bruker
from studier.tests.test_slett_emne import MedFilerTestCase, _innlogget

PDF = b"%PDF-1.4\n" + b"x" * 100


def _docx(*avsnitt):
    dokument = docx.Document()
    for tekst in avsnitt:
        dokument.add_paragraph(tekst)
    buffer = io.BytesIO()
    dokument.save(buffer)
    return buffer.getvalue()


def _fil(navn, innhold):
    return SimpleUploadedFile(navn, innhold)


class OpplastingTestCase(MedFilerTestCase):
    def setUp(self):
        super().setUp()
        self.emne = Emne.objects.create(eier=self.bruker, navn="Webutvikling")
        self.url = f"/emner/{self.emne.pk}/last-opp/"

    def _filer(self):
        return sorted(sti for sti in self.media.rglob("*") if sti.is_file())

    def _send(self, navn=None, innhold=b""):
        data = {} if navn is None else {"fil": _fil(navn, innhold)}
        return self.client.post(self.url, data)

    def _sjekk_avvist(self, svar, tekst):
        self.assertEqual(svar.status_code, 200)
        html = svar.content.decode()
        self.assertRegex(
            html,
            r'<p id="feil-fil" role="alert" tabindex="-1" autofocus[^>]*>'
            + re.escape(tekst)
            + "</p>",
        )
        self.assertIn('aria-invalid="true"', html)
        self.assertIn('aria-describedby="hjelp-fil feil-fil"', html)
        self.assertEqual(Notat.objects.count(), 0)
        self.assertEqual(self._filer(), [])


class GyldigFilTest(OpplastingTestCase):
    def test_gyldig_pdf_lagres_og_sender_til_notatsiden(self):
        innhold = b"%PDF-1.7\n" + b"a" * (1024 * 1024)
        svar = self._send("Forelesning 1.PDF", innhold)
        notat = Notat.objects.get()
        self.assertRedirects(svar, f"/notater/{notat.pk}/")
        self.assertEqual(notat.emne, self.emne)
        self.assertEqual(notat.originalnavn, "Forelesning 1.PDF")
        self.assertEqual(notat.filtype, "pdf")
        self.assertEqual(notat.storrelse, len(innhold))
        self.assertRegex(
            notat.fil.name,
            rf"^notater/{self.bruker.pk}/[0-9a-f-]{{36}}\.pdf$",
        )
        self.assertEqual(self._filer(), [self.media / notat.fil.name])
        self.assertEqual((self.media / notat.fil.name).read_bytes(), innhold)

    def test_gyldig_docx(self):
        svar = self._send("notat.docx", _docx("Første avsnitt", "Andre"))
        notat = Notat.objects.get()
        self.assertRedirects(svar, f"/notater/{notat.pk}/")
        self.assertEqual(notat.filtype, "docx")
        self.assertTrue(notat.fil.name.endswith(".docx"))
        self.assertEqual(len(self._filer()), 1)

    def test_gyldig_txt_med_aeoeaa(self):
        innhold = "Blåbærsyltetøy på skolen.".encode()
        svar = self._send("ærlig.txt", innhold)
        notat = Notat.objects.get()
        self.assertRedirects(svar, f"/notater/{notat.pk}/")
        self.assertEqual((notat.originalnavn, notat.filtype), ("ærlig.txt", "txt"))
        self.assertEqual(notat.storrelse, len(innhold))

    def test_txt_i_cp1252_godtas(self):
        self.assertEqual(valider_fil(_fil("a.txt", "Søt".encode("cp1252"))), "txt")

    def test_noyaktig_5_mb_godtas(self):
        fil = _fil("stor.pdf", b"%PDF-" + b"x" * (MAKS_STORRELSE - 5))
        self.assertEqual(valider_fil(fil), "pdf")

    def test_originalnavn_uten_sti(self):
        notat = last_opp(
            self.emne, _fil("C:\\Users\\ola\\notat.txt", b"hei"), self.bruker
        )
        self.assertEqual(notat.originalnavn, "notat.txt")


class AvvistFilTest(OpplastingTestCase):
    def test_ingen_fil(self):
        self._sjekk_avvist(self._send(), feilmeldinger.VELG_FIL)

    def test_for_stor(self):
        innhold = b"%PDF-" + b"x" * (MAKS_STORRELSE + 1 - 5)
        self._sjekk_avvist(self._send("stor.pdf", innhold), feilmeldinger.FIL_FOR_STOR)

    def test_feil_endelse(self):
        for navn in ("video.mp4", "lysbilder.pptx", "bilde.png", "uten-endelse"):
            with self.subTest(navn=navn):
                self._sjekk_avvist(self._send(navn, PDF), feilmeldinger.FIL_FEIL_FORMAT)

    def test_feil_innhold(self):
        uten_dokument = io.BytesIO()
        with zipfile.ZipFile(uten_dokument, "w") as arkiv:
            arkiv.writestr("annet.xml", "<x/>")
        tilfeller = {
            "falsk.pdf": b"Dette er ikke en PDF",
            "falsk.docx": b"PK ikke en zip",
            "zip.docx": uten_dokument.getvalue(),
            "binaer.txt": b"\x81\x8d\x8f\x90\x9d",
            # Ekte PNG-hode med IHDR, omdøpt til .txt.
            "bilde.txt": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01",
            # «Unicode» fra Notisblokk: UTF-16 LE med BOM.
            "utf16.txt": "Hei på deg".encode("utf-16"),
        }
        for navn, innhold in tilfeller.items():
            with self.subTest(navn=navn):
                self._sjekk_avvist(
                    self._send(navn, innhold), feilmeldinger.FIL_FEIL_FORMAT
                )

    def test_tom(self):
        tilfeller = {
            "tom.pdf": b"",
            "tom.txt": b"",
            "mellomrom.txt": b"   \n\t  \r\n",
            "bom.txt": "\ufeff  ".encode(),
            "tom.docx": _docx(),
            "blank.docx": _docx("   ", ""),
        }
        for navn, innhold in tilfeller.items():
            with self.subTest(navn=navn):
                self._sjekk_avvist(self._send(navn, innhold), feilmeldinger.FIL_TOM)

    def test_tjenesten_avviser_selv_uten_skjema(self):
        with self.assertRaises(ValidationError) as feil:
            last_opp(self.emne, None, self.bruker)
        self.assertEqual(feil.exception.messages, [feilmeldinger.VELG_FIL])
        self.assertEqual(Notat.objects.count(), 0)


class TilgangTest(OpplastingTestCase):
    def test_uten_vilkar_gir_permission_denied(self):
        self.bruker.vilkar_godtatt = None
        self.bruker.save(update_fields=["vilkar_godtatt"])
        with self.assertRaises(PermissionDenied):
            last_opp(self.emne, _fil("notat.pdf", PDF), self.bruker)
        self.assertEqual(Notat.objects.count(), 0)
        self.assertEqual(self._filer(), [])

    def test_post_uten_vilkar_sendes_til_vilkar(self):
        self.bruker.vilkar_godtatt = None
        self.bruker.save(update_fields=["vilkar_godtatt"])
        svar = self._send("notat.pdf", PDF)
        self.assertRedirects(svar, "/vilkar/", fetch_redirect_response=False)
        self.assertEqual(Notat.objects.count(), 0)
        self.assertEqual(self._filer(), [])

    def test_annens_emne_gir_404(self):
        annens = Emne.objects.create(eier=lag_bruker("annen@eks.no"), navn="Hemmelig")
        url = f"/emner/{annens.pk}/last-opp/"
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.get(url + "?videre=1").status_code, 404)
        svar = self.client.post(url, {"fil": _fil("notat.pdf", PDF)})
        self.assertEqual(svar.status_code, 404)
        self.assertEqual(Notat.objects.count(), 0)
        self.assertEqual(self._filer(), [])

    def test_tjenesten_avviser_annens_emne(self):
        annen = _innlogget(lag_bruker("annen@eks.no"))
        with self.assertRaises(Http404):
            last_opp(self.emne, _fil("notat.pdf", PDF), annen)
        self.assertEqual(Notat.objects.count(), 0)
        self.assertEqual(self._filer(), [])


class EmnetSlettetUnderveisTest(OpplastingTestCase):
    def test_slettet_emne_gir_404_uten_fil(self):
        Emne.objects.filter(pk=self.emne.pk).delete()
        with self.assertRaises(Http404):
            last_opp(self.emne, _fil("notat.pdf", PDF), self.bruker)
        self.assertEqual(self._filer(), [])

    def test_raden_kan_ikke_lagres_filen_slettes_igjen(self):
        def feil_ved_lagring(notat, *args, **kwargs):
            # Filen er skrevet når raden skal lagres.
            self.assertEqual(self._filer(), [self.media / notat.fil.name])
            raise IntegrityError("emnet er borte")

        with (
            mock.patch.object(
                Notat, "save", autospec=True, side_effect=feil_ved_lagring
            ),
            self.assertRaises(IntegrityError),
        ):
            last_opp(self.emne, _fil("notat.pdf", PDF), self.bruker)
        self.assertEqual(Notat.objects.count(), 0)
        self.assertEqual(self._filer(), [])


class ForsteGangTest(OpplastingTestCase):
    def test_forste_gang_viser_s5(self):
        svar = self.client.get(self.url)
        self.assertEqual(svar.status_code, 200)
        html = svar.content.decode()
        self.assertIn("Vilkår</h1>", html)
        self.assertIn("Du har godtatt vilkårene.", html)
        self.assertIn('href="/personvern/"', html)
        self.assertIn(f'href="{self.url}?videre=1"', html)
        self.assertIn("Gå videre til opplasting", html)
        avbryt = html.index(">Avbryt</a>")
        self.assertIn(
            f'href="/emner/{self.emne.pk}/"',
            html[html.rindex("<a ", 0, avbryt) : avbryt],
        )
        self.assertNotIn('type="file"', html)

    def test_ga_videre_viser_s6(self):
        html = self.client.get(self.url + "?videre=1").content.decode()
        self.assertIn('type="file"', html)

    def test_senere_viser_s6_direkte(self):
        annet = Emne.objects.create(eier=self.bruker, navn="Databaser")
        last_opp(annet, _fil("notat.pdf", PDF), self.bruker)
        html = self.client.get(self.url).content.decode()
        self.assertIn("Last opp notat</h1>", html)
        self.assertIn('type="file"', html)

    def test_andres_notater_teller_ikke(self):
        annen = _innlogget(lag_bruker("annen@eks.no"))
        annens = Emne.objects.create(eier=annen, navn="Annet")
        last_opp(annens, _fil("notat.pdf", PDF), annen)
        html = self.client.get(self.url).content.decode()
        self.assertIn("Vilkår</h1>", html)


class SkjemaTest(OpplastingTestCase):
    def setUp(self):
        super().setUp()
        self.html = self.client.get(self.url + "?videre=1").content.decode()

    def test_filfelt_med_etikett_hjelpetekst_og_accept(self):
        html = self.html
        self.assertIn('<label for="id_fil"', html)
        self.assertIn(">Velg fil</label>", html)
        self.assertRegex(
            html,
            r'<input id="id_fil" name="fil" type="file" accept="\.pdf,\.docx,\.txt"'
            r'[^>]*aria-describedby="hjelp-fil"',
        )
        self.assertIn('id="hjelp-fil"', html)
        self.assertIn("PDF, DOCX eller TXT. Maks 5 MB.", html)
        self.assertIn('enctype="multipart/form-data"', html)
        self.assertIn(
            "Innholdet i filen sendes til en ekstern KI-tjeneste for å lage quiz.", html
        )
        self.assertIn(">Last opp</button>", html)
        self.assertNotIn('role="alert" tabindex="-1" autofocus', html)

    def test_data_attributter_til_skriptet(self):
        self.assertIn(f'data-maks="{MAKS_STORRELSE}"', self.html)
        self.assertEqual(MAKS_STORRELSE, 5242880)
        for navn, tekst in (
            ("ingen", feilmeldinger.VELG_FIL),
            ("for-stor", feilmeldinger.FIL_FOR_STOR),
            ("format", feilmeldinger.FIL_FEIL_FORMAT),
            ("tom", feilmeldinger.FIL_TOM),
            ("avbrutt", feilmeldinger.OPPLASTING_AVBRUTT),
        ):
            with self.subTest(navn=navn):
                self.assertIn(f'data-feil-{navn}="{escape(tekst)}"', self.html)

    def test_skript_og_meny_lastes(self):
        self.assertIn("js/meny.js", self.html)
        self.assertIn("js/opplasting.js", self.html)
        self.assertIn('role="status"', self.html)

    def test_brodsmuler_og_tilbake(self):
        self.assertIn('aria-label="Tilbake til Webutvikling"', self.html)
        self.assertIn('<span aria-current="page">Last opp notat</span>', self.html)


class NotatsidenTest(OpplastingTestCase):
    def test_s7_viser_navn_brodsmuler_og_tekst(self):
        notat = last_opp(self.emne, _fil("HTML-forelesning.pdf", PDF), self.bruker)
        svar = self.client.get(f"/notater/{notat.pk}/")
        self.assertEqual(svar.status_code, 200)
        html = svar.content.decode()
        self.assertIn(
            '<h1 class="mb-4 text-2xl font-semibold">HTML-forelesning.pdf</h1>', html
        )
        self.assertIn("Lag en quiz for å komme i gang", html)
        self.assertIn(
            f'<a href="/emner/{self.emne.pk}/" class="underline">Webutvikling</a>', html
        )
        self.assertIn('<span aria-current="page">HTML-forelesning.pdf</span>', html)
        self.assertIn('aria-label="Tilbake til Webutvikling"', html)

    def test_annens_notat_gir_404(self):
        annen = _innlogget(lag_bruker("annen@eks.no"))
        annens = Emne.objects.create(eier=annen, navn="Annet")
        notat = last_opp(annens, _fil("hemmelig.pdf", PDF), annen)
        svar = self.client.get(f"/notater/{notat.pk}/")
        self.assertEqual(svar.status_code, 404)
        self.assertNotContains(svar, "hemmelig.pdf", status_code=404)

    def test_emnesiden_viser_notatene_nyeste_forst_som_lenker(self):
        eldre = last_opp(self.emne, _fil("eldre.pdf", PDF), self.bruker)
        nyere = last_opp(self.emne, _fil("nyere.txt", b"tekst"), self.bruker)
        html = self.client.get(f"/emner/{self.emne.pk}/").content.decode()
        self.assertIn(f'href="/emner/{self.emne.pk}/last-opp/"', html)
        self.assertLess(
            html.index(f'href="/notater/{nyere.pk}/"'),
            html.index(f'href="/notater/{eldre.pk}/"'),
        )
        self.assertLess(html.index("nyere.txt"), html.index("eldre.pdf"))


class FilenServeresIkkeTest(OpplastingTestCase):
    def test_ingen_url_gir_filen(self):
        notat = last_opp(self.emne, _fil("notat.pdf", PDF), self.bruker)
        for url in (
            f"/media/{notat.fil.name}",
            f"/{notat.fil.name}",
            f"/media/notater/{self.bruker.pk}/",
            "/media/",
        ):
            with self.subTest(url=url):
                svar = self.client.get(url)
                self.assertEqual(svar.status_code, 404)
                self.assertNotIn(PDF, svar.content)
