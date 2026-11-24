"""Midlertidig startside. Story 1.4 gjør `/` til Oversikt (S3)."""

from django.db.models import Count
from django.db.models.functions import Lower
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from studier.models import Emne
from studier.tilgang import egne


@require_http_methods(["GET", "HEAD"])
def startside(request):
    """Oversikt (S3): emnene til innlogget bruker, alfabetisk."""
    emner = (
        egne(Emne, request.user)
        .annotate(antall_notater=Count("notater"))
        .order_by(Lower("navn"))
    )
    return render(
        request,
        "studier/oversikt.html",
        {"emner": emner, "brodsmuler_oversikt": [{"tekst": "Oversikt"}]},
    )
