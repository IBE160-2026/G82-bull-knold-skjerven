"""Lager testbrukeren med et fast datasett (FR-28, AD-21, UX-DR26).

Alt går gjennom tjenestene i `studier/services/` (AD-1), og alltid i testmodus,
så ingen KI kalles. Finnes testbrukeren, slettes emnene hens først, slik at
resultatet blir det samme ved hver kjøring.
"""

import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

import ki
from ki import generering as ki_generering
from kontoer import testbruker
from studier.models import Sporsmal
from studier.services.emner import opprett_emne, slett_emne
from studier.services.generering import generer_synkront
from studier.services.notater import last_opp
from studier.services.okter import lagre_svar, lever_okt, start_eller_fortsett_okt
from studier.services.vilkar import godta_vilkar

EMNE = "Webutvikling"
HTML = "html-struktur-og-semantikk.pdf"
DOCX = "universell-utforming.docx"
TXT = "javascript-og-dom.txt"
ANTALL = 10
# Nivåene seed lager quiz på, per testdokument.
NIVAER_PER_DOKUMENT = {HTML: ("lett", "middels"), DOCX: ("vanskelig",), TXT: ()}


class Command(BaseCommand):
    help = "Lager testbrukeren med emnet Webutvikling og ferdige data. Bare testmodus."

    def handle(self, *args, **options):
        ki.tving_testmodus()
        mappe = settings.BASE_DIR / "testdokumenter"
        # Sjekkes før noe endres, så en kjøring uten mock-svar ikke etterlater halve data.
        _sjekk_mocksvar(mappe)

        bruker = self._klargjor_bruker()
        emne = opprett_emne(bruker, EMNE)
        html, docx, _txt = [
            self._last_opp(emne, mappe / navn, bruker) for navn in (HTML, DOCX, TXT)
        ]
        try:
            self._html_notat(html)
            self._docx_notat(docx)
        except ki.KIFeil as feil:
            raise CommandError(
                f"Generering i testmodus feilet med {feil.kode}. "
                "Sjekk at ki/mock/ er komplett, og kjør kommandoen på nytt."
            ) from feil

        self.stdout.write(
            self.style.SUCCESS(
                f"Testbrukeren er klar. Logg inn med {testbruker.EPOST} "
                f"og passordet {testbruker.PASSORD}."
            )
        )

    def _klargjor_bruker(self):
        """Lager testbrukeren, eller sletter emnene og setter passordet på nytt."""
        Bruker = get_user_model()
        bruker = Bruker.objects.filter(email=testbruker.EPOST).first()
        if bruker is None:
            bruker = Bruker.objects.create_user(testbruker.EPOST, testbruker.PASSORD)
        else:
            for emne in list(bruker.emner.all()):
                slett_emne(emne)
            bruker.set_password(testbruker.PASSORD)
            bruker.is_active = True
            bruker.save(update_fields=["password", "is_active"])
        godta_vilkar(bruker)
        return bruker

    def _last_opp(self, emne, sti, bruker):
        with sti.open("rb") as fil:
            return last_opp(emne, File(fil, name=sti.name), bruker)

    def _html_notat(self, notat):
        """Lett: 8–10 i feilbanken, 8 og 9 lært, 10 åpen. Middels: påbegynt forsøk."""
        lett = generer_synkront(notat, "lett", ANTALL)
        nr = _nummer(lett)
        _lever_forsok(lett, lambda sporsmal: nr[sporsmal.pk] <= 7)
        _lever_forsok(lett, lambda sporsmal: True)
        oving = start_eller_fortsett_okt(notat=notat)
        _svar(oving, lambda sporsmal: nr[sporsmal.pk] != 10)
        lever_okt(oving)

        middels = generer_synkront(notat, "middels", ANTALL)
        forsok = start_eller_fortsett_okt(middels)
        # Fremdriften på S3 og S7 teller svarene, så fire svar gir «spørsmål 4 av 10».
        _svar(forsok, lambda sporsmal: True, antall=4)

    def _docx_notat(self, notat):
        """Vanskelig: ett levert forsøk med 6 riktige, så 7–10 ligger i feilbanken."""
        vanskelig = generer_synkront(notat, "vanskelig", ANTALL)
        nr = _nummer(vanskelig)
        _lever_forsok(vanskelig, lambda sporsmal: nr[sporsmal.pk] <= 6)


def _sjekk_mocksvar(mappe):
    """Hever `CommandError` hvis testdokumentene eller mock-svarene seed trenger, mangler."""
    mock = ki_generering.MOCK_MAPPE
    lag = (
        "Kjør `python manage.py lag_mocksvar` med gruppas API-nøkkel, "
        "eller hent ki/mock/ fra repoet. Ingenting er endret."
    )
    for navn in NIVAER_PER_DOKUMENT:
        if not (mappe / navn).is_file():
            raise CommandError(
                f"Fant ikke testdokumentet {navn} i {mappe}. Ingenting er endret."
            )
    try:
        manifest = json.loads((mock / "manifest.json").read_text(encoding="utf-8"))
        filer = manifest["filer"]
        if not isinstance(filer, dict):
            raise TypeError("filer er ikke et objekt")
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as feil:
        raise CommandError(
            f"Mock-svarene mangler eller er ugyldige (ki/mock/manifest.json). {lag}"
        ) from feil
    for navn, nivaer in NIVAER_PER_DOKUMENT.items():
        try:
            dokument = filer.get(ki.les_fil(mappe / navn).sha256)
        except ki.KIFeil as feil:
            raise CommandError(
                f"Testdokumentet {navn} kunne ikke leses. Ingenting er endret."
            ) from feil
        if not isinstance(dokument, str):
            raise CommandError(
                f"Testdokumentet {navn} står ikke i ki/mock/manifest.json. {lag}"
            )
        for nivaa in nivaer:
            if not (mock / dokument / f"{nivaa}.json").is_file():
                raise CommandError(
                    f"Mock-svaret ki/mock/{dokument}/{nivaa}.json mangler. {lag}"
                )


def _nummer(quiz):
    """`{sporsmal_id: nr}` med nr 1-basert i quizens rekkefølge."""
    return {
        pk: nr
        for nr, pk in enumerate(
            quiz.sporsmal.order_by("id").values_list("pk", flat=True), start=1
        )
    }


def _svar(okt, riktig, antall=None):
    """Svarer på de første `antall` spørsmålene i økten (alle uten `antall`).

    Alternativet velges på `er_riktig`, ikke på posisjon, så stokkingen ikke
    endrer resultatet.
    """
    rader = okt.innhold if antall is None else okt.innhold[:antall]
    sporsmal_per_pk = Sporsmal.objects.prefetch_related("alternativer").in_bulk(
        [rad["sporsmal"] for rad in rader]
    )
    for rad in rader:
        sporsmal = sporsmal_per_pk[rad["sporsmal"]]
        onsket = riktig(sporsmal)
        alternativ = next(
            alt for alt in sporsmal.alternativer.all() if alt.er_riktig == onsket
        )
        lagre_svar(okt, sporsmal, alternativ)


def _lever_forsok(quiz, riktig):
    okt = start_eller_fortsett_okt(quiz)
    _svar(okt, riktig)
    lever_okt(okt)
