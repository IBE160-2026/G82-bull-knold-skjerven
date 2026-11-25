"""Views for emner og notater: Nytt emne (S16), emnesiden (S4), Slett emne (S13),
Last opp notat (S5/S6) og notatsiden (S7). Oversikt (S3) ligger i farequiz/views.py."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from farequiz import feilmeldinger
from studier.forms import EmneForm, NotatForm
from studier.models import Emne, Notat, Quiz
from studier.services.emner import gi_nytt_navn, opprett_emne
from studier.services.emner import slett_emne as slett_emne_tjeneste
from studier.services.notater import MAKS_STORRELSE
from studier.services.notater import last_opp as last_opp_tjeneste
from studier.tilgang import egne, hent_egen


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


def _emne_kontekst(objekt, siste):
    """Tilbake og brødsmuler for en side under emnet: Oversikt › emne › `siste`."""
    emne_url = reverse("studier:emne", args=[objekt.pk])
    return {
        "emne": objekt,
        "tilbake_url": emne_url,
        "tilbake_tekst": f"Tilbake til {objekt.navn}",
        "brodsmuler": [
            *_oversikt_brodsmule(),
            {"tekst": objekt.navn, "url": emne_url},
            {"tekst": siste},
        ],
    }


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


@require_http_methods(["GET", "HEAD"])
def notat(request, pk):
    """S7, skallet. Quizskjemaet og quizlisten kommer i story 2.4."""
    objekt = hent_egen(Notat, pk, request.user)
    return render(
        request,
        "studier/notat.html",
        {"notat": objekt, **_emne_kontekst(objekt.emne, objekt.originalnavn)},
    )
