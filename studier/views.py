"""Views for emner og notater: Nytt emne (S16), emnesiden (S4), Slett emne (S13),
Last opp notat (S5/S6), notatsiden (S7) og generering (S8). Oversikt (S3) ligger i
farequiz/views.py."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

import ki
from farequiz import feilmeldinger
from studier.forms import EmneForm, NotatForm, NyQuizForm
from studier.models import Emne, Feilkode, Genereringsjobb, Jobbstatus, Notat, Quiz
from studier.services.emner import gi_nytt_navn, opprett_emne
from studier.services.emner import slett_emne as slett_emne_tjeneste
from studier.services.generering import aktiv_jobb, kjor_steg, opprett_jobb
from studier.services.notater import MAKS_STORRELSE
from studier.services.notater import last_opp as last_opp_tjeneste
from studier.tilgang import egne, hent_egen, hent_egen_eller_none


def _oversikt_brodsmule():
    return [{"tekst": "Oversikt", "url": reverse("startside")}]


@require_http_methods(["GET", "HEAD", "POST"])
def ny_emne(request):
    form = EmneForm(
        request.POST if request.method == "POST" else None, eier=request.user
    )
    if request.method == "POST" and form.is_valid():
        try:
            emne = opprett_emne(request.user, form.cleaned_data["navn"])
        except IntegrityError:
            form.add_error("navn", feilmeldinger.NAVN_TATT)
        else:
            return redirect("studier:emne", pk=emne.pk)
    return render(
        request,
        "studier/ny_emne.html",
        {
            "form": form,
            "tilbake_url": reverse("startside"),
            "tilbake_tekst": "Tilbake til Oversikt",
            "brodsmuler": [*_oversikt_brodsmule(), {"tekst": "Nytt emne"}],
        },
    )


def _vis_emne(request, objekt, form):
    return render(
        request,
        "studier/emne.html",
        {
            "emne": objekt,
            "notater": objekt.notater.order_by("-opprettet", "-pk"),
            "navn_form": form,
            "tilbake_url": reverse("startside"),
            "tilbake_tekst": "Tilbake til Oversikt",
            "brodsmuler": [*_oversikt_brodsmule(), {"tekst": objekt.navn}],
        },
    )


@require_http_methods(["GET", "HEAD"])
def emne(request, pk):
    objekt = hent_egen(Emne, pk, request.user)
    form = EmneForm(initial={"navn": objekt.navn}, eier=request.user, emne=objekt)
    return _vis_emne(request, objekt, form)


@require_http_methods(["POST"])
def endre_navn(request, pk):
    objekt = hent_egen(Emne, pk, request.user)
    form = EmneForm(request.POST, eier=request.user, emne=objekt)
    if form.is_valid():
        try:
            gi_nytt_navn(objekt, form.cleaned_data["navn"])
        except IntegrityError:
            objekt.refresh_from_db(fields=["navn"])
            form.add_error("navn", feilmeldinger.NAVN_TATT)
        else:
            return redirect("studier:emne", pk=objekt.pk)
    return _vis_emne(request, objekt, form)


@require_http_methods(["GET", "HEAD", "POST"])
def slett_emne(request, pk):
    objekt = hent_egen(Emne, pk, request.user)
    if request.method == "POST":
        slett_emne_tjeneste(objekt)
        return redirect("startside")
    emne_url = reverse("studier:emne", args=[objekt.pk])
    return render(
        request,
        "studier/slett_emne.html",
        {
            "emne": objekt,
            "antall_notater": objekt.notater.count(),
            "antall_quizer": Quiz.objects.filter(notat__emne=objekt).count(),
            "tilbake_url": emne_url,
            "tilbake_tekst": f"Tilbake til {objekt.navn}",
            "brodsmuler": [
                *_oversikt_brodsmule(),
                {"tekst": objekt.navn, "url": emne_url},
                {"tekst": "Slett emne"},
            ],
        },
    )


def _emne_kontekst(objekt, siste, notat=None):
    """Tilbake og brødsmuler for en side under emnet: Oversikt › emne › `siste`.

    Med `notat` står notatet mellom emnet og `siste`, og Tilbake går til notatet.
    """
    emne_url = reverse("studier:emne", args=[objekt.pk])
    kontekst = {
        "emne": objekt,
        "tilbake_url": emne_url,
        "tilbake_tekst": f"Tilbake til {objekt.navn}",
        "brodsmuler": [
            *_oversikt_brodsmule(),
            {"tekst": objekt.navn, "url": emne_url},
            {"tekst": siste},
        ],
    }
    if notat is not None:
        notat_url = reverse("studier:notat", args=[notat.pk])
        kontekst["tilbake_url"] = notat_url
        kontekst["tilbake_tekst"] = f"Tilbake til {notat.originalnavn}"
        kontekst["brodsmuler"].insert(
            -1, {"tekst": notat.originalnavn, "url": notat_url}
        )
    return kontekst


@require_http_methods(["GET", "HEAD", "POST"])
def last_opp(request, pk):
    """S5 første gang (ingen notater i noen emner), ellers S6. Virker uten JavaScript (AD-13)."""
    objekt = hent_egen(Emne, pk, request.user)
    if request.method == "POST":
        form = NotatForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                notat = last_opp_tjeneste(
                    objekt, form.cleaned_data["fil"], request.user
                )
            except ValidationError as feil:
                form.add_error("fil", feil)
            else:
                return redirect("studier:notat", pk=notat.pk)
    else:
        if request.GET.get("videre") != "1" and not egne(Notat, request.user).exists():
            return render(
                request,
                "studier/bekreft_opplasting.html",
                _emne_kontekst(objekt, "Last opp notat"),
            )
        form = NotatForm()
    return render(
        request,
        "studier/last_opp.html",
        {
            **_emne_kontekst(objekt, "Last opp notat"),
            "form": form,
            "maks_storrelse": MAKS_STORRELSE,
            "feil": {
                "ingen": feilmeldinger.VELG_FIL,
                "for_stor": feilmeldinger.FIL_FOR_STOR,
                "format": feilmeldinger.FIL_FEIL_FORMAT,
                "tom": feilmeldinger.FIL_TOM,
                "avbrutt": feilmeldinger.OPPLASTING_AVBRUTT,
            },
        },
    )


@require_http_methods(["GET", "HEAD", "POST"])
def notat(request, pk):
    """S7: quizkortene og skjemaet for ny quiz (FR-11). POST lager eller gjenbruker jobben (FR-14)."""
    objekt = hent_egen(Notat, pk, request.user)
    if request.method == "POST":
        form = NyQuizForm(request.POST)
        if form.is_valid():
            jobb = opprett_jobb(
                objekt,
                form.cleaned_data["vanskelighetsgrad"],
                form.cleaned_data["antall"],
            )
            return redirect("studier:jobb", pk=jobb.pk)
    else:
        form = NyQuizForm()
    quizer = list(
        objekt.quizer.annotate(antall_sporsmal=Count("sporsmal")).order_by(
            "-opprettet", "-pk"
        )
    )
    # Modellen som laget quizen, aldri gjeldende innstilling (AD-11).
    for quiz in quizer:
        quiz.modellnavn = ki.visningsnavn(quiz.modell)
    return render(
        request,
        "studier/notat.html",
        {
            "notat": objekt,
            "form": form,
            "nivaer": NyQuizForm.base_fields["vanskelighetsgrad"].choices,
            "quizer": quizer,
            "testmodus_forhandslagret": feilmeldinger.TESTMODUS_FORHANDSLAGRET,
            "aktiv_jobb": aktiv_jobb(objekt),
            **_emne_kontekst(objekt.emne, objekt.originalnavn),
        },
    )


# De tre stegene på S8, i rekkefølge, med statusen som betyr at steget pågår.
_STEG = (
    (Jobbstatus.LESER, "Leser filen"),
    (Jobbstatus.LAGER, "Lager spørsmål"),
    (Jobbstatus.SJEKKER, "Sjekker quizen"),
)
_IKONER = {"ferdig": "✓", "pågår": "…", "venter": "○"}
# Feilkodene der S8 sier at filen er lagret (spec 2.5, B3).
_FIL_ER_LAGRET_KODER = (Feilkode.FORMAT, Feilkode.API_FEIL, Feilkode.API_NOKKEL)


def _fremdrift_kontekst(jobb, vent=False):
    rekkefolge = [status for status, _ in _STEG]
    if jobb.status == Jobbstatus.FERDIG:
        naa = len(_STEG)
    elif jobb.status in rekkefolge:
        naa = rekkefolge.index(jobb.status)
    else:
        naa = -1
    steg = []
    for nr, (_, tekst) in enumerate(_STEG):
        tilstand = "ferdig" if nr < naa else "pågår" if nr == naa else "venter"
        steg.append({"tekst": tekst, "tilstand": tilstand, "ikon": _IKONER[tilstand]})
    kontekst = {"jobb": jobb, "steg": steg, "vent": vent}
    if jobb.status == Jobbstatus.FEILET:
        kontekst["feilmelding"] = feilmeldinger.generering_feilet(jobb.feilkode)
        # Ikke for timeout (teksten sier det selv) eller koder som ber om ny opplasting.
        if jobb.feilkode in _FIL_ER_LAGRET_KODER:
            kontekst["fil_er_lagret"] = feilmeldinger.FIL_ER_LAGRET
    return kontekst


@require_http_methods(["GET", "HEAD"])
def jobb(request, pk):
    """S8: fremdriften. HTMX driver ett steg om gangen via `steg`.

    Ved feil står kodens tekst og «Prøv igjen», som virker uten JavaScript.
    """
    objekt = hent_egen(Genereringsjobb, pk, request.user)
    notat_objekt = objekt.notat
    # Setter jobben til `feilet`/`timeout` hvis fristen er ute (FR-15).
    aktiv_jobb(notat_objekt)
    objekt.refresh_from_db()
    if objekt.status == Jobbstatus.FERDIG:
        return redirect("studier:notat", pk=objekt.notat_id)
    return render(
        request,
        "studier/jobb.html",
        {
            **_fremdrift_kontekst(objekt),
            **_emne_kontekst(notat_objekt.emne, "Lager quiz", notat=notat_objekt),
            "ingen_serverkontakt": feilmeldinger.INGEN_SERVERKONTAKT,
        },
    )


def _sluttfragment(request):
    """Svaret når jobben ikke finnes lenger, for eksempel fordi notatet er slettet."""
    return render(
        request,
        "studier/_slutt.html",
        {"melding": feilmeldinger.NOTAT_FINNES_IKKE},
    )


@require_POST
def steg(request, pk):
    """Kjører ett steg og gir fremdriftsfragmentet. En ferdig jobb gir `HX-Redirect` til S7.

    `vist` er statusen siden sist viste. Er den uendret, byttes ikke #fremdrift.
    Finnes ikke jobben (aldri, eller slettet med notatet, også midt i et steg),
    gis et sluttfragment med status 200. En annens jobb gir 404.
    """
    objekt = hent_egen_eller_none(Genereringsjobb, pk, request.user)
    if objekt is None:
        return _sluttfragment(request)
    kjort = kjor_steg(objekt.pk)
    try:
        objekt.refresh_from_db()
    except Genereringsjobb.DoesNotExist:
        return _sluttfragment(request)
    # #fremdrift byttes bare når statusen er en annen enn den siden viser.
    endret = objekt.status != request.POST.get("vist") or objekt.status in (
        Jobbstatus.FERDIG,
        Jobbstatus.FEILET,
    )
    svar = render(
        request,
        "studier/_fremdrift.html",
        {**_fremdrift_kontekst(objekt, vent=not kjort), "endret": endret},
    )
    if objekt.status == Jobbstatus.FERDIG:
        svar["HX-Redirect"] = reverse("studier:notat", args=[objekt.notat_id])
    return svar
