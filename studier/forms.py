"""Skjema for emner (FR-4)."""

from django import forms

from farequiz import feilmeldinger
from studier.models import Emne


class EmneForm(forms.Form):
    navn = forms.CharField(
        label="Navn på emnet",
        max_length=100,
        error_messages={
            "required": feilmeldinger.NAVN_TOMT,
            "max_length": feilmeldinger.NAVN_FOR_LANGT,
        },
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )

    def __init__(self, *args, eier, **kwargs):
        super().__init__(*args, **kwargs)
        self.eier = eier

    def clean_navn(self):
        navn = self.cleaned_data["navn"].strip()
        if not navn:
            raise forms.ValidationError(feilmeldinger.NAVN_TOMT)
        # Python-sammenligning, slik at også Æ, Ø og Å regnes likt. SQLite-LOWER gjør bare ASCII.
        if any(
            emne.navn.casefold() == navn.casefold()
            for emne in Emne.objects.filter(eier=self.eier).only("navn")
        ):
            raise forms.ValidationError(feilmeldinger.NAVN_TATT)
        return navn
