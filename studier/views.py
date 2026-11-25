"""Views for emner: Nytt emne (S16), emnesiden (S4) og Slett emne (S13). Oversikt (S3) ligger i farequiz/views.py."""

from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from farequiz import feilmeldinger
from studier.forms import EmneForm
from studier.models import Emne, Quiz
from studier.services.emner import gi_nytt_navn, opprett_emne
from studier.services.emner import slett_emne as slett_emne_tjeneste
from studier.tilgang import hent_egen


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
            "notater": objekt.notater.all(),
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
