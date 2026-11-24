"""Vilkårene håndheves i én mellomvare (AD-23)."""

from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect
from django.urls import reverse


class VilkarMiddleware:
    """
    Sender en innlogget bruker som ikke har godtatt vilkårene, til `/vilkar/`
    med `next`. Unntatt er `/vilkar/`, `/personvern/`, utlogging og statiske
    filer.

    Ligger etter `LoginRequiredMiddleware`. Sjekken skjer i `process_view`, slik
    at en utlogget bruker først sendes til innlogging.
    """

    UNNTATTE_SIDER = ("kontoer:vilkar", "kontoer:personvern", "kontoer:logg_ut")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        bruker = request.user
        if not bruker.is_authenticated or bruker.vilkar_godtatt is not None:
            return None
        if self._er_unntatt(request.path):
            return None
        vilkar = reverse("kontoer:vilkar")
        if request.method not in ("GET", "HEAD"):
            # En POST kan ikke gjentas med GET etter at vilkårene er godtatt.
            return redirect(vilkar)
        sporring = urlencode({REDIRECT_FIELD_NAME: request.get_full_path()})
        return redirect(f"{vilkar}?{sporring}")

    def _er_unntatt(self, sti):
        if settings.STATIC_URL and sti.startswith(settings.STATIC_URL):
            return True
        return sti in {reverse(navn) for navn in self.UNNTATTE_SIDER}
