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

    def __init__(self, *args, eier, emne=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.eier = eier
        # Ved endring av navn telles ikke emnet selv som duplikat.
        self.emne = emne

    def clean_navn(self):
        navn = self.cleaned_data["navn"].strip()
        if not navn:
            raise forms.ValidationError(feilmeldinger.NAVN_TOMT)
        # Python-sammenligning, slik at også Æ, Ø og Å regnes likt. SQLite-LOWER gjør bare ASCII.
        andre = Emne.objects.filter(eier=self.eier).only("navn")
        if self.emne is not None:
            andre = andre.exclude(pk=self.emne.pk)
        if any(annet.navn.casefold() == navn.casefold() for annet in andre):
            raise forms.ValidationError(feilmeldinger.NAVN_TATT)
        return navn
