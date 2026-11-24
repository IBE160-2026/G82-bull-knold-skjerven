"""Midlertidig startside. Story 1.4 gjør `/` til Oversikt (S3)."""

from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "HEAD"])
def startside(request):
    return render(request, "startside.html")
