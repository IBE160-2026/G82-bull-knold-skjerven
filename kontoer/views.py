"""Innlogging, registrering, utlogging, vilkår og personvernerklæring (FR-1, FR-2, FR-7)."""

from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView, LogoutView, RedirectURLMixin
from django.db import IntegrityError
from django.shortcuts import redirect, render, resolve_url
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from farequiz import feilmeldinger
from kontoer import testbruker
from kontoer.forms import LoggInnForm, RegistrerForm
from studier.services.vilkar import godta_vilkar


def _er_utlogging(neste):
    """Sann når `neste` peker på utloggingen, som bare tar imot POST."""
    sti = urlsplit(neste).path.rstrip("/")
    return sti == reverse("kontoer:logg_ut").rstrip("/")


class UtenUtloggingSomMalMixin:
    """Følger ikke `next` til utloggingen, fordi en GET dit gir 405."""

    def get_redirect_url(self):
        neste = super().get_redirect_url()
        return "" if neste and _er_utlogging(neste) else neste


class LoggInnView(UtenUtloggingSomMalMixin, LoginView):
    """S1: hero, informasjonskort og innloggingsskjemaet."""

    template_name = "kontoer/logg_inn.html"
    authentication_form = LoggInnForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        kontekst = super().get_context_data(**kwargs)
        neste = kontekst[self.redirect_field_name]
        if neste and neste != "/":
            kontekst["okt_utlopt"] = feilmeldinger.OKT_UTLOPT
        # Malen viser dem bare i testmodus (FR-28).
        kontekst["testbruker_epost"] = testbruker.EPOST
        kontekst["testbruker_passord"] = testbruker.PASSORD
        return kontekst


class LoggUtView(LogoutView):
    """Bare POST. Sender til innlogging (LOGOUT_REDIRECT_URL)."""


@login_not_required
@require_http_methods(["GET", "POST"])
def registrer(request):
    """S2. En ny konto logges inn og sendes til startsiden."""
    if request.user.is_authenticated:
        return redirect(resolve_url(settings.LOGIN_REDIRECT_URL))
    form = RegistrerForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            bruker = form.lagre()
        except IntegrityError:
            # To registreringer med samme e-post samtidig.
            form.add_error("email", feilmeldinger.EPOST_FINNES)
        else:
            login(request, bruker)
            return redirect(resolve_url(settings.LOGIN_REDIRECT_URL))
    return render(request, "kontoer/registrer.html", {"form": form})


class VilkarView(UtenUtloggingSomMalMixin, RedirectURLMixin, TemplateView):
    """S1b. Vises til vilkårene er godtatt. Uten JavaScript er den en vanlig side."""

    template_name = "kontoer/vilkar.html"
    next_page = "/"
    http_method_names = ["get", "post", "head", "options"]

    def get(self, request, *args, **kwargs):
        if request.user.vilkar_godtatt is not None:
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        godta_vilkar(request.user)
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kontekst = super().get_context_data(**kwargs)
        kontekst[self.redirect_field_name] = self.get_redirect_url()
        return kontekst


@login_not_required
@require_http_methods(["GET", "HEAD"])
def personvern(request):
    """S15. Offentlig side."""
    return render(request, "kontoer/personvern.html")
