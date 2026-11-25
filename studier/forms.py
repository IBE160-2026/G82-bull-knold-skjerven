"""Skjema for emner (FR-4), notater (FR-8) og ny quiz (FR-11)."""

from django import forms

from farequiz import feilmeldinger
from studier.models import Emne, Vanskelighetsgrad
from studier.services.generering import MAKS_ANTALL, MIN_ANTALL
from studier.services.notater import valider_fil


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


class NotatForm(forms.Form):
    """Ett filfelt. Reglene for filen ligger i `valider_fil`, som også `last_opp` kjører."""

    # Ikke påkrevd og tom fil tillatt her, slik at `valider_fil` gir alle feiltekstene.
    fil = forms.FileField(
        label="Velg fil",
        required=False,
        allow_empty_file=True,
        error_messages={
            "invalid": feilmeldinger.VELG_FIL,
            "missing": feilmeldinger.VELG_FIL,
        },
        widget=forms.FileInput,
    )

    def clean_fil(self):
        fil = self.cleaned_data.get("fil")
        valider_fil(fil)
        return fil


class NyQuizForm(forms.Form):
    """Vanskelighetsgrad og antall for en ny quiz (FR-11). Malen skriver feltene selv."""

    vanskelighetsgrad = forms.ChoiceField(
        label="Vanskelighetsgrad",
        choices=Vanskelighetsgrad.choices,
        initial=Vanskelighetsgrad.MIDDELS,
        widget=forms.RadioSelect,
    )
    antall = forms.IntegerField(
        label="Antall spørsmål",
        min_value=MIN_ANTALL,
        max_value=MAKS_ANTALL,
        initial=10,
        error_messages={
            "required": feilmeldinger.ANTALL_UGYLDIG,
            "invalid": feilmeldinger.ANTALL_UGYLDIG,
            "min_value": feilmeldinger.ANTALL_UGYLDIG,
            "max_value": feilmeldinger.ANTALL_UGYLDIG,
        },
    )
