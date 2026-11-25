"""
Hele datamodellen for FåreQuiz (AD-3, AD-6, AD-7, AD-9, AD-14).

Bare `Emne` kan lagres rett fra skjema. All annen skriving skjer i
`studier/services/` (AD-1), og sletting skjer bare via `slett_emne` (AD-14).
"""

import uuid
from pathlib import Path

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils import timezone


class Vanskelighetsgrad(models.TextChoices):
    LETT = "lett", "Lett"
    MIDDELS = "middels", "Middels"
    VANSKELIG = "vanskelig", "Vanskelig"


class Filtype(models.TextChoices):
    PDF = "pdf", "PDF"
    DOCX = "docx", "Word (DOCX)"
    TXT = "txt", "Tekst (TXT)"


class Jobbstatus(models.TextChoices):
    LESER = "leser", "Leser"
    LAGER = "lager", "Lager"
    SJEKKER = "sjekker", "Sjekker"
    FERDIG = "ferdig", "Ferdig"
    FEILET = "feilet", "Feilet"


class Feilkode(models.TextChoices):
    TIMEOUT = "timeout", "Tidsavbrudd"
    FORMAT = "format", "Feil format"
    FOR_LITE_INNHOLD = "for_lite_innhold", "For lite innhold"
    FOR_STOR = "for_stor", "For stor"
    API_NOKKEL = "api_nokkel", "API-nøkkel"
    API_FEIL = "api_feil", "API-feil"


class Okttype(models.TextChoices):
    FORSOK = "forsok", "Forsøk"
    OVING = "oving", "Øving"


class Oktstatus(models.TextChoices):
    PABEGYNT = "pabegynt", "Påbegynt"
    LEVERT = "levert", "Levert"


class Hendelse(models.TextChoices):
    LAGT_I = "lagt_i", "Lagt i feilbanken"
    NULLSTILT = "nullstilt", "Nullstilt"
    OPP = "opp", "Opp"
    LAERT = "laert", "Lært"
    INGEN = "ingen", "Ingen"


def notatfil_sti(instance, filnavn):
    """`notater/<eier-id>/<uuid4><endelse>`. Originalnavnet lagres i `originalnavn`."""
    endelse = Path(filnavn).suffix.lower()
    return f"notater/{instance.emne.eier_id}/{uuid.uuid4()}{endelse}"


class Emne(models.Model):
    eier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="emner"
    )
    navn = models.CharField(max_length=100)
    opprettet = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "emne"
        verbose_name_plural = "emner"
        constraints = [
            models.UniqueConstraint(
                Lower("navn"), "eier", name="emne_unikt_navn_per_eier"
            ),
        ]

    def __str__(self):
        return self.navn


class Notat(models.Model):
    emne = models.ForeignKey(Emne, on_delete=models.CASCADE, related_name="notater")
    fil = models.FileField(upload_to=notatfil_sti, max_length=255)
    originalnavn = models.CharField(max_length=255)
    filtype = models.CharField(max_length=4, choices=Filtype.choices)
    storrelse = models.PositiveIntegerField(help_text="Størrelse i byte.")
    opprettet = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "notat"
        verbose_name_plural = "notater"

    def __str__(self):
        return self.originalnavn


class Genereringsjobb(models.Model):
    notat = models.ForeignKey(Notat, on_delete=models.CASCADE, related_name="jobber")
    vanskelighetsgrad = models.CharField(
        max_length=9, choices=Vanskelighetsgrad.choices
    )
    antall = models.PositiveSmallIntegerField()
    startet = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=7, choices=Jobbstatus.choices, default=Jobbstatus.LESER
    )
    runde = models.PositiveSmallIntegerField(default=1)
    i_gang = models.BooleanField(default=False)
    feilkode = models.CharField(
        max_length=16, choices=Feilkode.choices, blank=True, default=""
    )
    raatt_svar = models.TextField(blank=True, default="")
    forhandslagret = models.BooleanField(default=False)
    modell = models.CharField(max_length=100, blank=True, default="")
    prompt_versjon = models.CharField(max_length=20, blank=True, default="")

    class Meta:
        verbose_name = "genereringsjobb"
        verbose_name_plural = "genereringsjobber"

    def __str__(self):
        return f"Jobb {self.pk} ({self.status})"


class Quiz(models.Model):
    notat = models.ForeignKey(Notat, on_delete=models.CASCADE, related_name="quizer")
    jobb = models.OneToOneField(
        Genereringsjobb, on_delete=models.CASCADE, related_name="quiz"
    )
    vanskelighetsgrad = models.CharField(
        max_length=9, choices=Vanskelighetsgrad.choices
    )
    sprak = models.CharField("språk", max_length=35, help_text="BCP 47-kode.")
    modell = models.CharField(max_length=100)
    prompt_versjon = models.CharField(max_length=20)
    forhandslagret = models.BooleanField(default=False)
    opprettet = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "quiz"
        verbose_name_plural = "quizer"

    def __str__(self):
        return f"Quiz {self.pk} ({self.vanskelighetsgrad})"


class SporsmalQuerySet(models.QuerySet):
    def ikke_meldt(self):
        """Spørsmålene som ikke er meldt som feil (FR-31). Eneste filter for meldte spørsmål."""
        return self.filter(meldt_tidspunkt__isnull=True)


class Sporsmal(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="sporsmal")
    tekst = models.TextField()
    begrunnelse = models.TextField()
    # Skrives bare av `services.sporsmal.meld_sporsmal` (FR-31).
    meldt_tidspunkt = models.DateTimeField(null=True, blank=True)

    objects = SporsmalQuerySet.as_manager()

    class Meta:
        verbose_name = "spørsmål"
        verbose_name_plural = "spørsmål"
        ordering = ["id"]

    def __str__(self):
        return self.tekst


class Alternativ(models.Model):
    sporsmal = models.ForeignKey(
        Sporsmal, on_delete=models.CASCADE, related_name="alternativer"
    )
    tekst = models.TextField()
    er_riktig = models.BooleanField(default=False)

    class Meta:
        verbose_name = "alternativ"
        verbose_name_plural = "alternativer"
        constraints = [
            models.UniqueConstraint(
                fields=["sporsmal"],
                condition=Q(er_riktig=True),
                name="alternativ_hoyst_ett_riktig",
            ),
        ]

    def __str__(self):
        return self.tekst


class Okt(models.Model):
    """Forsøk (`forsok`) eller øvingsøkt (`oving`) (AD-6, AD-16)."""

    notat = models.ForeignKey(Notat, on_delete=models.CASCADE, related_name="okter")
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, null=True, blank=True, related_name="okter"
    )
    type = models.CharField(max_length=6, choices=Okttype.choices)
    status = models.CharField(
        max_length=8, choices=Oktstatus.choices, default=Oktstatus.PABEGYNT
    )
    opprettet = models.DateTimeField(auto_now_add=True)
    sist_endret = models.DateTimeField(default=timezone.now)
    levert_tidspunkt = models.DateTimeField(null=True, blank=True)
    poengsum = models.PositiveSmallIntegerField(null=True, blank=True)
    antall = models.PositiveSmallIntegerField(null=True, blank=True)
    innhold = models.JSONField(default=list)

    class Meta:
        verbose_name = "økt"
        verbose_name_plural = "økter"
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(type=Okttype.FORSOK, quiz__isnull=False)
                    | Q(type=Okttype.OVING, quiz__isnull=True)
                ),
                name="okt_quiz_hvis_og_bare_hvis_forsok",
            ),
            models.UniqueConstraint(
                fields=["quiz"],
                condition=Q(type=Okttype.FORSOK, status=Oktstatus.PABEGYNT),
                name="okt_ett_pabegynt_forsok_per_quiz",
            ),
            models.UniqueConstraint(
                fields=["notat"],
                condition=Q(type=Okttype.OVING, status=Oktstatus.PABEGYNT),
                name="okt_en_pabegynt_oving_per_notat",
            ),
        ]

    def __str__(self):
        return f"Økt {self.pk} ({self.type}, {self.status})"


class Svar(models.Model):
    okt = models.ForeignKey(Okt, on_delete=models.CASCADE, related_name="svar")
    sporsmal = models.ForeignKey(
        Sporsmal, on_delete=models.CASCADE, related_name="svar"
    )
    alternativ = models.ForeignKey(
        Alternativ, on_delete=models.CASCADE, related_name="svar"
    )
    hendelse = models.CharField(
        max_length=9, choices=Hendelse.choices, blank=True, default=""
    )

    class Meta:
        verbose_name = "svar"
        verbose_name_plural = "svar"
        constraints = [
            models.UniqueConstraint(
                fields=["okt", "sporsmal"], name="svar_ett_per_sporsmal_per_okt"
            ),
        ]

    def __str__(self):
        return f"Svar {self.pk}"


class Feilbankrad(models.Model):
    """Høyst én per spørsmål. Slettes aldri utenom emnesletting (AD-3)."""

    sporsmal = models.OneToOneField(
        Sporsmal, on_delete=models.CASCADE, related_name="feilbankrad"
    )
    riktige_pa_rad = models.PositiveSmallIntegerField(default=0)
    laert_tidspunkt = models.DateTimeField(null=True, blank=True)
    opprettet = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "feilbankrad"
        verbose_name_plural = "feilbankrader"

    def __str__(self):
        return f"Feilbankrad for spørsmål {self.sporsmal_id}"
