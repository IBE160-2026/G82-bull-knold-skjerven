"""Skjemaer for registrering og innlogging (FR-1, FR-2)."""

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from farequiz import feilmeldinger


class RegistrerForm(forms.Form):
    """E-post og passord. En brukt e-post gir feil uansett store og små bokstaver."""

    email = forms.EmailField(
        label="E-post",
        max_length=254,
        error_messages={
            "required": feilmeldinger.UGYLDIG_EPOST,
            "invalid": feilmeldinger.UGYLDIG_EPOST,
            "max_length": feilmeldinger.UGYLDIG_EPOST,
        },
    )
    passord = forms.CharField(
        label="Passord",
        strip=False,
        widget=forms.PasswordInput,
        error_messages={"required": feilmeldinger.FOR_KORT_PASSORD},
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise ValidationError(feilmeldinger.EPOST_FINNES, code="epost_finnes")
        return email

    def clean_passord(self):
        passord = self.cleaned_data["passord"]
        try:
            password_validation.validate_password(passord)
        except ValidationError as feil:
            raise ValidationError(
                [
                    ValidationError(feilmeldinger.FOR_KORT_PASSORD, code=e.code)
                    if e.code == "password_too_short"
                    else e
                    for e in feil.error_list
                ]
            ) from None
        return passord

    def lagre(self):
        """Lager brukeren. Passordet lagres bare som hash."""
        return get_user_model().objects.create_user(
            self.cleaned_data["email"], self.cleaned_data["passord"]
        )


class LoggInnForm(AuthenticationForm):
    """Innlogging med e-post. Alle feil gir samme melding."""

    username = forms.CharField(
        label="E-post",
        widget=forms.EmailInput,
        error_messages={
            "required": feilmeldinger.FEIL_INNLOGGING,
            "max_length": feilmeldinger.FEIL_INNLOGGING,
        },
    )
    password = forms.CharField(
        label="Passord",
        strip=False,
        widget=forms.PasswordInput,
        error_messages={"required": feilmeldinger.FEIL_INNLOGGING},
    )

    error_messages = {
        "invalid_login": feilmeldinger.FEIL_INNLOGGING,
        "inactive": feilmeldinger.FEIL_INNLOGGING,
    }

    @property
    def feilmelding(self):
        """Meldingen som vises over skjemaet. Den er lik for alle feil."""
        return feilmeldinger.FEIL_INNLOGGING if self.errors else ""
