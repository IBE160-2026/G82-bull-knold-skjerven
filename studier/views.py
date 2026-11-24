"""Views for emner: Nytt emne (S16) og emnesiden (S4). Oversikt (S3) ligger i farequiz/views.py."""

from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from farequiz import feilmeldinger
from studier.forms import EmneForm
from studier.models import Emne
from studier.services.emner import opprett_emne
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


@require_http_methods(["GET", "HEAD"])
def emne(request, pk):
    objekt = hent_egen(Emne, pk, request.user)
    return render(
        request,
        "studier/emne.html",
        {
            "emne": objekt,
            "notater": objekt.notater.all(),
            "tilbake_url": reverse("startside"),
            "tilbake_tekst": "Tilbake til Oversikt",
            "brodsmuler": [*_oversikt_brodsmule(), {"tekst": objekt.navn}],
        },
    )
