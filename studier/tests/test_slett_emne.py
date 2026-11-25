"""Tester for å slette emne (FR-6, AD-14), én per rad i I/O-matrisen i spec 1.6."""

import re
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.db import transaction
from django.test import TestCase, override_settings
from django.utils import timezone

from studier.models import (
    Alternativ,
    Emne,
    Feilbankrad,
    Genereringsjobb,
    Notat,
    Okt,
    Quiz,
    Sporsmal,
    Svar,
)
from studier.services.emner import slett_emne
from studier.tests.fabrikk import lag_bruker, lag_kjede


def _innlogget(bruker):
    bruker.vilkar_godtatt = timezone.now()
    bruker.save(update_fields=["vilkar_godtatt"])
    return bruker


def _rader_i(emne_pk):
    """Antall rader per modell som hører til emnet med denne pk-en."""
    return {
        Emne: Emne.objects.filter(pk=emne_pk).count(),
        Notat: Notat.objects.filter(emne_id=emne_pk).count(),
        Genereringsjobb: Genereringsjobb.objects.filter(notat__emne_id=emne_pk).count(),
        Quiz: Quiz.objects.filter(notat__emne_id=emne_pk).count(),
        Sporsmal: Sporsmal.objects.filter(quiz__notat__emne_id=emne_pk).count(),
        Alternativ: Alternativ.objects.filter(
            sporsmal__quiz__notat__emne_id=emne_pk
        ).count(),
        Okt: Okt.objects.filter(notat__emne_id=emne_pk).count(),
        Svar: Svar.objects.filter(okt__notat__emne_id=emne_pk).count(),
        Feilbankrad: Feilbankrad.objects.filter(
            sporsmal__quiz__notat__emne_id=emne_pk
        ).count(),
    }


class MedFilerTestCase(TestCase):
    """Midlertidig `MEDIA_ROOT`, så testene kan lage og slette ekte filer."""

    def setUp(self):
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        innstillinger = override_settings(MEDIA_ROOT=media)
        innstillinger.enable()
        self.addCleanup(innstillinger.disable)
        self.media = Path(media)
        self.bruker = _innlogget(lag_bruker())
        self.client.force_login(self.bruker)

    def _lag_fil(self, notat):
        sti = self.media / notat.fil.name
        sti.parent.mkdir(parents=True, exist_ok=True)
        sti.write_bytes(b"%PDF-1.4 test")
        return sti


class VisSlettesidenTest(MedFilerTestCase):
    def test_s13_viser_navn_antall_og_knapper_i_riktig_rekkefolge(self):
        kjede = lag_kjede(self.bruker, "Webutvikling")
        emne = kjede[Emne]
        svar = self.client.get(f"/emner/{emne.pk}/slett/")
        self.assertEqual(svar.status_code, 200)
        html = svar.content.decode()
        self.assertIn("Slette emnet «Webutvikling»?", html)
        self.assertIn(
            "Dette sletter 1 notat, 1 quiz og all historikk. Det kan ikke angres.",
            html,
        )
        self.assertEqual(html.count("<h1"), 1)
        self.assertNotIn("<dialog", html)
        avbryt = html.index(">Avbryt</a>")
        skjema = html.index(f'<form method="post" action="/emner/{emne.pk}/slett/"')
        fareknapp = html.index("Slett emnet og alt innhold")
        self.assertLess(avbryt, skjema)
        self.assertLess(avbryt, fareknapp)
        self.assertLess(skjema, fareknapp)
        self.assertIn("bg-error", html[skjema:fareknapp])
        self.assertIn("csrfmiddlewaretoken", html[skjema:fareknapp])
        avbryt_lenke = html[html.rindex("<a ", 0, avbryt) : avbryt]
        self.assertIn(f'href="/emner/{emne.pk}/"', avbryt_lenke)
        # Ingen tabindex som endrer rekkefølgen.
        self.assertIsNone(re.search(r'tabindex="[1-9]', html))

    def test_flertall_i_teksten(self):
        kjede = lag_kjede(self.bruker, "Webutvikling")
        notat = kjede[Notat]
        Notat.objects.create(
            emne=kjede[Emne],
            fil="notater/x/annen.pdf",
            originalnavn="annen.pdf",
            filtype="pdf",
            storrelse=1,
        )
        jobb = Genereringsjobb.objects.create(
            notat=notat, vanskelighetsgrad="lett", antall=3
        )
        Quiz.objects.create(
            notat=notat,
            jobb=jobb,
            vanskelighetsgrad="lett",
            sprak="nb",
            modell="m",
            prompt_versjon="1",
        )
        html = self.client.get(f"/emner/{kjede[Emne].pk}/slett/").content.decode()
        self.assertIn("Dette sletter 2 notater, 2 quizer og all historikk.", html)

    def test_tomt_emne_har_egen_tekst(self):
        emne = Emne.objects.create(eier=self.bruker, navn="Tomt")
        html = self.client.get(f"/emner/{emne.pk}/slett/").content.decode()
        self.assertIn(
            "Dette sletter emnet. Det har ingen notater eller quizer ennå. "
            "Det kan ikke angres.",
            html,
        )

    def test_brodsmuler_og_tilbake_til_emnet(self):
        emne = Emne.objects.create(eier=self.bruker, navn="HTML")
        html = self.client.get(f"/emner/{emne.pk}/slett/").content.decode()
        self.assertIn('aria-label="Tilbake til HTML"', html)
        self.assertIn(f'<a href="/emner/{emne.pk}/" class="underline">HTML</a>', html)
        self.assertIn('<span aria-current="page">Slett emne</span>', html)

    def test_s4_har_lenke_til_s13(self):
        emne = Emne.objects.create(eier=self.bruker, navn="HTML")
        html = self.client.get(f"/emner/{emne.pk}/").content.decode()
        self.assertIn(f'href="/emner/{emne.pk}/slett/"', html)
        self.assertIn(">Slett emne</a>", html)

    def test_get_sletter_ingenting(self):
        emne = Emne.objects.create(eier=self.bruker, navn="HTML")
        self.client.get(f"/emner/{emne.pk}/slett/")
        self.assertTrue(Emne.objects.filter(pk=emne.pk).exists())


class SlettTest(MedFilerTestCase):
    def test_post_sletter_alt_og_fila_og_sender_til_s3(self):
        kjede = lag_kjede(self.bruker, "Webutvikling")
        emne = kjede[Emne]
        fil = self._lag_fil(kjede[Notat])
        with self.captureOnCommitCallbacks(execute=True) as tilbakekall:
            svar = self.client.post(f"/emner/{emne.pk}/slett/")
        self.assertEqual(len(tilbakekall), 1)
        self.assertRedirects(svar, "/", fetch_redirect_response=False)
        self.assertEqual(set(_rader_i(emne.pk).values()), {0})
        self.assertFalse(fil.exists())
        oversikt = self.client.get("/").content.decode()
        self.assertNotIn("Webutvikling", oversikt)

    def test_fil_som_mangler_gir_ingen_feil(self):
        kjede = lag_kjede(self.bruker)
        emne = kjede[Emne]
        self.assertFalse((self.media / kjede[Notat].fil.name).exists())
        with (
            self.assertNoLogs("studier.services.emner", level="WARNING"),
            self.captureOnCommitCallbacks(execute=True) as tilbakekall,
        ):
            svar = self.client.post(f"/emner/{emne.pk}/slett/")
        self.assertEqual(len(tilbakekall), 1)
        self.assertRedirects(svar, "/", fetch_redirect_response=False)
        self.assertFalse(Emne.objects.filter(pk=emne.pk).exists())

    def test_annen_feil_enn_oserror_stopper_ikke_resten(self):
        kjede = lag_kjede(self.bruker)
        notat2 = Notat.objects.create(
            emne=kjede[Emne],
            fil=f"notater/{self.bruker.pk}/to.pdf",
            originalnavn="to.pdf",
            filtype="pdf",
            storrelse=1,
        )
        self._lag_fil(kjede[Notat])
        fil2 = self._lag_fil(notat2)
        from django.core.files.storage import default_storage

        ekte_delete = default_storage.delete

        def feiler_forste(navn):
            if navn == kjede[Notat].fil.name:
                raise ValueError("ugyldig sti")
            return ekte_delete(navn)

        with (
            mock.patch.object(default_storage, "delete", side_effect=feiler_forste),
            self.assertLogs("studier.services.emner", level="WARNING"),
            self.captureOnCommitCallbacks(execute=True),
        ):
            svar = self.client.post(f"/emner/{kjede[Emne].pk}/slett/")
        self.assertRedirects(svar, "/", fetch_redirect_response=False)
        self.assertEqual(set(_rader_i(kjede[Emne].pk).values()), {0})
        self.assertFalse(fil2.exists())

    def test_fil_som_ikke_kan_slettes_stopper_ikke_resten(self):
        kjede = lag_kjede(self.bruker)
        notat2 = Notat.objects.create(
            emne=kjede[Emne],
            fil=f"notater/{self.bruker.pk}/to.pdf",
            originalnavn="to.pdf",
            filtype="pdf",
            storrelse=1,
        )
        fil1 = self._lag_fil(kjede[Notat])
        fil2 = self._lag_fil(notat2)
        from django.core.files.storage import default_storage

        ekte_delete = default_storage.delete

        def feiler_forste(navn):
            if navn == kjede[Notat].fil.name:
                raise PermissionError("låst")
            return ekte_delete(navn)

        with (
            mock.patch.object(default_storage, "delete", side_effect=feiler_forste),
            self.assertLogs("studier.services.emner", level="WARNING"),
            self.captureOnCommitCallbacks(execute=True),
        ):
            svar = self.client.post(f"/emner/{kjede[Emne].pk}/slett/")
        self.assertRedirects(svar, "/", fetch_redirect_response=False)
        self.assertTrue(fil1.exists())
        self.assertFalse(fil2.exists())
        self.assertFalse(Emne.objects.filter(pk=kjede[Emne].pk).exists())

    def test_tilbakerulling_beholder_rader_og_fil(self):
        kjede = lag_kjede(self.bruker)
        emne = kjede[Emne]
        fil = self._lag_fil(kjede[Notat])
        far = _rader_i(emne.pk)

        class Avbrutt(Exception):
            pass

        with self.captureOnCommitCallbacks(execute=True) as tilbakekall:
            try:
                with transaction.atomic():
                    slett_emne(emne)
                    raise Avbrutt
            except Avbrutt:
                pass
        self.assertEqual(tilbakekall, [])
        self.assertEqual(_rader_i(emne.pk), far)
        self.assertTrue(fil.exists())

    def test_andre_emner_er_uendret(self):
        valgt = lag_kjede(self.bruker, "Kjemi")
        beholdt = lag_kjede(self.bruker, "Fysikk")
        Notat.objects.filter(pk=beholdt[Notat].pk).update(
            fil=f"notater/{self.bruker.pk}/fysikk.pdf"
        )
        beholdt[Notat].refresh_from_db()
        fil_beholdt = self._lag_fil(beholdt[Notat])
        annens = lag_kjede(lag_bruker("annen@eks.no"), "Kjemi")
        far_beholdt = _rader_i(beholdt[Emne].pk)
        far_annens = _rader_i(annens[Emne].pk)
        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(f"/emner/{valgt[Emne].pk}/slett/")
        self.assertEqual(set(_rader_i(valgt[Emne].pk).values()), {0})
        self.assertEqual(_rader_i(beholdt[Emne].pk), far_beholdt)
        self.assertEqual(_rader_i(annens[Emne].pk), far_annens)
        self.assertTrue(fil_beholdt.exists())
        beholdt[Emne].refresh_from_db()
        self.assertEqual(beholdt[Emne].navn, "Fysikk")


class TilgangTest(MedFilerTestCase):
    def test_andres_emne_gir_404_ved_get_og_post(self):
        annens = lag_kjede(lag_bruker("annen@eks.no"), "Hemmelig")
        fil = self._lag_fil(annens[Notat])
        far = _rader_i(annens[Emne].pk)
        url = f"/emner/{annens[Emne].pk}/slett/"
        svar = self.client.get(url)
        self.assertEqual(svar.status_code, 404)
        self.assertNotContains(svar, "Hemmelig", status_code=404)
        with self.captureOnCommitCallbacks(execute=True):
            svar = self.client.post(url)
        self.assertEqual(svar.status_code, 404)
        self.assertEqual(_rader_i(annens[Emne].pk), far)
        self.assertTrue(fil.exists())

    def test_allerede_slettet_gir_404(self):
        emne = Emne.objects.create(eier=self.bruker, navn="HTML")
        url = f"/emner/{emne.pk}/slett/"
        with self.captureOnCommitCallbacks(execute=True):
            forste = self.client.post(url)
        self.assertRedirects(forste, "/", fetch_redirect_response=False)
        self.assertFalse(Emne.objects.filter(pk=emne.pk).exists())
        self.assertEqual(self.client.post(url).status_code, 404)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_utlogget_sendes_til_innlogging(self):
        emne = Emne.objects.create(eier=self.bruker, navn="HTML")
        self.client.logout()
        for metode in (self.client.get, self.client.post):
            with self.subTest(metode=metode.__name__):
                svar = metode(f"/emner/{emne.pk}/slett/")
                self.assertEqual(svar.status_code, 302)
                self.assertIn("/logg-inn/", svar["Location"])
        self.assertTrue(Emne.objects.filter(pk=emne.pk).exists())


# En linje som nevner en av modellene (eller et navn som `notater`, `quizer`) og kaller
# `.delete(`. Også modellene over dem, siden sletting der går videre med cascade.
SLETTEMONSTER = re.compile(
    r"\b(notat|quiz|okt|feilbankrad|emne|genereringsjobb|jobb|sporsmal|bruker|user)"
    r"\w*\b[^\n]*\.delete\(",
    re.IGNORECASE,
)


class KildesjekkTest(TestCase):
    """Bare `slett_emne` sletter `Notat`, `Quiz`, `Okt` eller `Feilbankrad` (AD-14)."""

    APPER = ("farequiz", "kontoer", "studier", "ki")
    TILLATT = Path("studier") / "services" / "emner.py"

    def _kildefiler(self):
        rot = Path(settings.BASE_DIR)
        for app in self.APPER:
            self.assertTrue((rot / app).is_dir(), f"Fant ikke appen {app}.")
            for fil in (rot / app).rglob("*.py"):
                relativ = fil.relative_to(rot)
                deler = relativ.parts
                if "tests" in deler or fil.name.startswith("tests"):
                    continue
                if "migrations" in deler or relativ == self.TILLATT:
                    continue
                yield relativ, fil.read_text(encoding="utf-8")

    def test_ingen_annen_kode_sletter_disse_modellene(self):
        funn = [
            f"{sti}: {linje.strip()}"
            for sti, tekst in self._kildefiler()
            for linje in tekst.splitlines()
            if SLETTEMONSTER.search(linje)
        ]
        self.assertEqual(funn, [])

    def test_monsteret_finner_sletting(self):
        for linje in (
            "Notat.objects.filter(emne=emne).delete()",
            "quiz.delete()",
            "okt.delete()",
            "self.notater.all().delete()",
            "Feilbankrad.objects.all().delete()",
            "Emne.objects.filter(pk=1).delete()",
            "emne.delete()",
            "jobb.delete()",
            "Genereringsjobb.objects.all().delete()",
            "sporsmal.delete()",
            "request.user.delete()",
            "Bruker.objects.filter(pk=1).delete()",
        ):
            with self.subTest(linje=linje):
                self.assertTrue(SLETTEMONSTER.search(linje))
        self.assertIsNone(SLETTEMONSTER.search("default_storage.delete(navn)"))
