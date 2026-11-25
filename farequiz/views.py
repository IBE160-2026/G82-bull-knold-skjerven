"""Oversikt (S3): emnene og boksen «Fortsett der du slapp»."""

from django.db.models import Count, Prefetch
from django.db.models.functions import Lower
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from studier.models import Emne, Okt, Oktstatus, Okttype, Svar
from studier.tilgang import egne


def _fortsett_rader(bruker):
    """Påbegynte forsøk og øvingsøkter, nyeste først, for «Fortsett der du slapp» (FR-18).

    Svarene hentes med én ekstra spørring uansett antall rader.
    """
    okter = (
        egne(Okt, bruker)
        .filter(status=Oktstatus.PABEGYNT)
        .select_related("quiz", "notat__emne")
        .prefetch_related(
            Prefetch("svar", queryset=Svar.objects.only("okt_id", "sporsmal_id"))
        )
        .order_by("-sist_endret", "-pk")
    )
    rader = []
    for okt in okter:
        svart = {svar.sporsmal_id for svar in okt.svar.all()}
        # Samme regel som `studier.services.okter.forste_ubesvarte` (alle besvart gir 1),
        # men uten en spørring per økt.
        forste = next(
            (
                nr
                for nr, rad in enumerate(okt.innhold, start=1)
                if rad["sporsmal"] not in svart
            ),
            1,
        )
        oving = okt.type == Okttype.OVING
        tittel = (
            f"Øv på feil, {len(okt.innhold)} spørsmål"
            if oving
            else f"{okt.quiz.get_vanskelighetsgrad_display()}, {len(okt.innhold)} spørsmål"
        )
        rader.append(
            {
                "okt": okt,
                "tittel_id": f"fortsett-{okt.pk}",
                "fremdrift_id": f"fortsett-fremdrift-{okt.pk}",
                "tittel": tittel,
                "lenketekst": "Fortsett øvingen" if oving else "Fortsett quizen",
                "emne": okt.notat.emne.navn,
                "notat": okt.notat.originalnavn,
                "n": max(len(svart), 1),
                "m": len(okt.innhold),
                "url": reverse("studier:sporsmal", args=[okt.pk, forste]),
            }
        )
    return rader


@require_http_methods(["GET", "HEAD"])
def startside(request):
    """Oversikt (S3): boksen «Fortsett der du slapp» og emnene til innlogget bruker, alfabetisk."""
    emner = (
        egne(Emne, request.user)
        .annotate(antall_notater=Count("notater"))
        .order_by(Lower("navn"))
    )
    return render(
        request,
        "studier/oversikt.html",
        {
            "emner": emner,
            "fortsett_rader": _fortsett_rader(request.user),
            "brodsmuler_oversikt": [{"tekst": "Oversikt"}],
        },
    )
