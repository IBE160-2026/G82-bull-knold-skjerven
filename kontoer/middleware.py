"""Vilkårene håndheves i én mellomvare (AD-23). HTMX-forespørsler får `HX-Redirect`
i stedet for en omdirigering til innloggingen eller vilkårene."""

from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponse
from django.shortcuts import redirect, resolve_url
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

_OMDIRIGERINGER = (301, 302, 303, 307, 308)


class HtmxOmdirigeringMiddleware:
    """
    En HTMX-forespørsel (`HX-Request: true`) som ville fått en omdirigering til
    innloggingen eller `/vilkar/`, får i stedet status 200 med tom kropp og
    `HX-Redirect` til samme side. `next` er stien i `HX-Current-URL`, altså siden
    brukeren står på, ikke endepunktet forespørselen gikk til. Mangler headeren
    eller er den ugyldig, sendes ingen `next`. Da bytter nettleseren hele siden,
    og innloggingssiden byttes ikke inn i en del av siden (for eksempel S8).

    Ligger før `LoginRequiredMiddleware`, slik at den ser omdirigeringene fra
    både den og `VilkarMiddleware`.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        svar = self.get_response(request)
        if request.headers.get("HX-Request") != "true":
            return svar
        if svar.status_code not in _OMDIRIGERINGER or not svar.has_header("Location"):
            return svar
        side = urlsplit(svar["Location"]).path
        if side not in self._sider():
            return svar
        naa = request.headers.get("HX-Current-URL", "")
        neste = urlsplit(naa).path
        if (
            neste.startswith("/")
            and not neste.startswith("//")
            and url_has_allowed_host_and_scheme(naa, {request.get_host()})
        ):
            side = f"{side}?{urlencode({REDIRECT_FIELD_NAME: neste})}"
        nytt = HttpResponse(status=200)
        nytt["HX-Redirect"] = side
        return nytt

    @staticmethod
    def _sider():
        return {resolve_url(settings.LOGIN_URL), reverse("kontoer:vilkar")}


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
