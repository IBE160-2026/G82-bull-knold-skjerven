"""Skjema for emner (FR-4)."""

from django import forms
from django.db.models.functions import Lower

from farequiz import feilmeldinger
from studier.models import Emne


class EmneForm(forms.Form):
    navn = forms.CharField(
        label="Navn på emnet",
        max_length=255,
        error_messages={"required": feilmeldinger.NAVN_TOMT},
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )

    def __init__(self, *args, eier, **kwargs):
        super().__init__(*args, **kwargs)
        self.eier = eier

    def clean_navn(self):
        navn = self.cleaned_data["navn"].strip()
        if not navn:
            raise forms.ValidationError(feilmeldinger.NAVN_TOMT)
        if len(navn) > 100:
            raise forms.ValidationError(feilmeldinger.NAVN_FOR_LANGT)
        finnes = (
            Emne.objects.filter(eier=self.eier)
            .annotate(navn_liten=Lower("navn"))
            .filter(navn_liten=navn.lower())
        )
        if finnes.exists():
            raise forms.ValidationError(feilmeldinger.NAVN_TATT)
        return navn
