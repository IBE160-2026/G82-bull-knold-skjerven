"""Tilgang per URL (SM-5, FR-2, FR-3, AD-8).

Testene går gjennom URL-mønstrene fra resolveren, så et nytt mønster med ID
uten oppsett i `OPPSETT` gir feil med mønsterets navn.
"""

import shutil
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import parse_qs, urlsplit

from django.apps import apps
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import URLPattern, URLResolver, get_resolver, reverse

from studier.models import Emne, Genereringsjobb, Notat, Okt, Quiz
from studier.tests.fabrikk import godta, lag_bruker, lag_olas

# Sidene en utlogget bruker kan åpne. Alle andre sender til Logg inn med `next`.
OFFENTLIGE = {"kontoer:logg_inn", "kontoer:registrer", "kontoer:personvern"}

FANT_IKKE = "Fant ikke siden"
FINNES_IKKE = 999_999

GET_POST = frozenset({"GET", "POST"})
BARE_GET = frozenset({"GET"})
BARE_POST = frozenset({"POST"})


def _ingen_data(kjede):
    return {}


@dataclass(frozen=True)
class Oppsett:
    """Hvordan et mønster med ID testes.

    `kwargs` gir URL-argumentene fra Olas objekter (`kjede`, se `lag_olas`).
    `metoder` er metodene viewet tar imot. `data` gir POST-dataene. De er
    gyldige der det går, så et hull i tilgangen ville endret databasen.
    """

    kwargs: Callable
    metoder: frozenset
    data: Callable = _ingen_data


def _pk(nokkel):
    return lambda kjede: {"pk": kjede[nokkel].pk}


def _nr(nokkel):
    return lambda kjede: {"pk": kjede[nokkel].pk, "nr": 1}


# Ett oppsett per URL-mønster med ID. Et nytt mønster må legges til her.
OPPSETT = {
    "studier:emne": Oppsett(_pk(Emne), BARE_GET),
    "studier:endre_navn": Oppsett(
        _pk(Emne), BARE_POST, lambda kjede: {"navn": "Kapret"}
    ),
    "studier:slett_emne": Oppsett(_pk(Emne), GET_POST),
    "studier:last_opp": Oppsett(
        _pk(Emne),
        GET_POST,
        lambda kjede: {
            "fil": SimpleUploadedFile("kapret.txt", b"Et kapret notat. " * 50)
        },
    ),
    "studier:notat": Oppsett(
        _pk(Notat),
        GET_POST,
        lambda kjede: {"vanskelighetsgrad": "lett", "antall": "5"},
    ),
    "studier:ov_pa_feil": Oppsett(_pk(Notat), BARE_POST),
    "studier:jobb": Oppsett(_pk(Genereringsjobb), BARE_GET),
    "studier:steg": Oppsett(
        _pk(Genereringsjobb), BARE_POST, lambda kjede: {"vist": "leser"}
    ),
    "studier:start_quiz": Oppsett(_pk(Quiz), BARE_POST),
    "studier:sporsmal": Oppsett(
        _nr(Okt),
        GET_POST,
        lambda kjede: {"retning": "neste", "alternativ": kjede["feil"].pk},
    ),
    "studier:lever": Oppsett(_pk(Okt), GET_POST),
    "studier:resultat": Oppsett(_pk("levert"), BARE_GET),
    "studier:meld": Oppsett(_nr("levert"), GET_POST),
}


def url_monstre(monstre=None, prefiks="", navnerom="", omformere=None):
    """`[(navn, rute, omformere)]` for alle URL-mønstrene, med navnerommet i navnet."""
    if monstre is None:
        monstre = get_resolver().url_patterns
    resultat = []
    for monster in monstre:
        rute = prefiks + str(monster.pattern)
        alle_omformere = {**(omformere or {}), **monster.pattern.converters}
        if isinstance(monster, URLResolver):
            nytt = ":".join(filter(None, (navnerom, monster.namespace)))
            resultat += url_monstre(monster.url_patterns, rute, nytt, alle_omformere)
        elif isinstance(monster, URLPattern):
            navn = monster.name and ":".join(filter(None, (navnerom, monster.name)))
            resultat.append((navn or rute, rute, alle_omformere))
    return resultat


def ruter_med_id():
    return sorted(navn for navn, _, omformere in url_monstre() if omformere)


def ruter_uten_id():
    return sorted(navn for navn, _, omformere in url_monstre() if not omformere)


def hele_databasen():
    """Alle radene i appenes modeller, også tidsstempler. Viser om noe er endret."""
    rader = {}
    for app in ("kontoer", "studier"):
        for modell in apps.get_app_config(app).get_models():
            rader[modell.__name__] = list(modell.objects.order_by("pk").values())
    return rader


class MediaTestCase(TestCase):
    """Midlertidig `MEDIA_ROOT`, så en opplasting aldri havner i `media/`."""

    @classmethod
    def setUpClass(cls):
        cls._media = tempfile.mkdtemp()
        cls._innstillinger = override_settings(MEDIA_ROOT=cls._media)
        cls._innstillinger.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._innstillinger.disable()
        shutil.rmtree(cls._media, ignore_errors=True)


class UrlTilgangTest(MediaTestCase):
    """Kari er innlogget og prøver Olas ID-er i hver URL (SM-5)."""

    @classmethod
    def setUpTestData(cls):
        cls.ola = lag_bruker("ola@eks.no")
        cls.kari = lag_bruker("kari@eks.no")
        godta(cls.ola, cls.kari)
        cls.olas = lag_olas(cls.ola)
        lag_olas(cls.kari)

    def setUp(self):
        self.client.force_login(self.kari)

    def _url(self, navn, kjede, finnes_ikke=False):
        kwargs = OPPSETT[navn].kwargs(kjede)
        if finnes_ikke:
            kwargs["pk"] = FINNES_IKKE
        return reverse(navn, kwargs=kwargs)

    def _send(self, metode, navn, url):
        if metode == "GET":
            return self.client.get(url)
        return self.client.post(url, OPPSETT[navn].data(self.olas))

    def test_alle_monstre_med_id_har_oppsett(self):
        ruter = set(ruter_med_id())
        mangler = sorted(ruter - set(OPPSETT))
        self.assertFalse(
            mangler,
            "URL-mønstre med ID mangler oppsett i OPPSETT i "
            f"studier/tests/test_tilgang_urler.py: {', '.join(mangler)}",
        )
        foreldet = sorted(set(OPPSETT) - ruter)
        self.assertFalse(
            foreldet,
            f"OPPSETT har mønstre som ikke finnes lenger: {', '.join(foreldet)}",
        )

    def test_andres_id_gir_404_og_endrer_ingenting(self):
        for navn, oppsett in OPPSETT.items():
            for metode in ("GET", "POST"):
                with self.subTest(navn=navn, metode=metode):
                    for_ = hele_databasen()
                    svar = self._send(metode, navn, self._url(navn, self.olas))
                    self.assertEqual(hele_databasen(), for_)
                    if metode in oppsett.metoder:
                        self.assertEqual(svar.status_code, 404)
                        self.assertContains(svar, FANT_IKKE, status_code=404)
                    else:
                        # Samme svar som for en ID som ikke finnes (beslutning 26.11).
                        finnes_ikke = self._send(
                            metode, navn, self._url(navn, self.olas, finnes_ikke=True)
                        )
                        self.assertEqual(svar.status_code, finnes_ikke.status_code)
                        self.assertEqual(svar.status_code, 405)

    def test_ola_far_ikke_404_for_egne_id_er(self):
        """Viser at oppsettet peker på objekter som finnes, så 404-en over skyldes eieren."""
        self.client.force_login(self.ola)
        for navn, oppsett in OPPSETT.items():
            with self.subTest(navn=navn):
                url = self._url(navn, self.olas)
                if "GET" in oppsett.metoder:
                    self.assertIn(self.client.get(url).status_code, (200, 302))
                else:
                    svar = self.client.post(url, oppsett.data(self.olas))
                    self.assertNotEqual(svar.status_code, 404)


class InnloggingTest(MediaTestCase):
    """Utlogget bruker: bare de offentlige sidene vises (FR-2)."""

    @classmethod
    def setUpTestData(cls):
        cls.ola = lag_bruker("ola@eks.no")
        godta(cls.ola)
        cls.olas = lag_olas(cls.ola)

    def _urler(self):
        urler = {navn: reverse(navn) for navn in ruter_uten_id()}
        for navn in ruter_med_id():
            if navn not in OPPSETT:
                self.fail(f"URL-mønsteret {navn} har ID, men mangler oppsett i OPPSETT")
            urler[navn] = reverse(navn, kwargs=OPPSETT[navn].kwargs(self.olas))
        return urler

    def test_alle_monstre_er_med(self):
        self.assertEqual(set(self._urler()), {navn for navn, _, _ in url_monstre()})
        self.assertLessEqual(OFFENTLIGE, set(self._urler()))

    def test_offentlige_sider_gir_200(self):
        for navn in sorted(OFFENTLIGE):
            with self.subTest(navn=navn):
                self.assertEqual(self.client.get(reverse(navn)).status_code, 200)

    def test_andre_sider_sender_til_logg_inn_med_next(self):
        logg_inn = reverse("kontoer:logg_inn")
        for navn, url in sorted(self._urler().items()):
            if navn in OFFENTLIGE:
                continue
            with self.subTest(navn=navn, url=url):
                svar = self.client.get(url)
                self.assertEqual(svar.status_code, 302)
                sted = urlsplit(svar["Location"])
                self.assertEqual(sted.path, logg_inn)
                self.assertEqual(parse_qs(sted.query).get("next"), [url])

    def test_post_sender_til_logg_inn_og_endrer_ingenting(self):
        logg_inn = reverse("kontoer:logg_inn")
        for navn, url in sorted(self._urler().items()):
            if navn in OFFENTLIGE:
                continue
            data = OPPSETT[navn].data(self.olas) if navn in OPPSETT else {}
            with self.subTest(navn=navn, url=url):
                for_ = hele_databasen()
                svar = self.client.post(url, data)
                self.assertEqual(hele_databasen(), for_)
                self.assertEqual(svar.status_code, 302)
                self.assertEqual(urlsplit(svar["Location"]).path, logg_inn)
