"""Views for emner og notater: Nytt emne (S16), emnesiden (S4), Slett emne (S13),
Last opp notat (S5/S6), notatsiden (S7), generering (S8), Ta quiz (S9) og Se over og
lever (S10). Oversikt (S3) ligger i farequiz/views.py."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

import ki
from farequiz import feilmeldinger
from studier.forms import EmneForm, NotatForm, NyQuizForm
from studier.models import (
    Alternativ,
    Emne,
    Feilkode,
    Genereringsjobb,
    Jobbstatus,
    Notat,
    Okt,
    Oktstatus,
    Quiz,
    Sporsmal,
    Svar,
)
from studier.services.emner import gi_nytt_navn, opprett_emne
from studier.services.emner import slett_emne as slett_emne_tjeneste
from studier.services.generering import aktiv_jobb, kjor_steg, opprett_jobb
from studier.services.notater import MAKS_STORRELSE
from studier.services.notater import last_opp as last_opp_tjeneste
from studier.services.okter import (
    OktErLevert,
    SvarAvvist,
    besvarte,
    element,
    forste_ubesvarte,
    lagre_svar,
    start_eller_fortsett_okt,
)
from studier.tilgang import egne, hent_egen, hent_egen_eller_none


def _oversikt_brodsmule():
    return [{"tekst": "Oversikt", "url": reverse("startside")}]


@require_http_methods(["GET", "HEAD", "POST"])
def ny_emne(request):
    form = EmneForm(
        request.POST if request.method == "POST" else None, eier=request.user
    )
    if request.method == "POST" and form.is_valid():
        try:
            emne = opprett_emne(request.user, form.cleaned_data["navn"])
        except IntegrityError:
            form.add_error("navn", feilmeldinger.NAVN_TATT)
        else:
            return redirect("studier:emne", pk=emne.pk)
    return render(
        request,
        "studier/ny_emne.html",
        {
            "form": form,
            "tilbake_url": reverse("startside"),
            "tilbake_tekst": "Tilbake til Oversikt",
            "brodsmuler": [*_oversikt_brodsmule(), {"tekst": "Nytt emne"}],
        },
    )


def _vis_emne(request, objekt, form):
    return render(
        request,
        "studier/emne.html",
        {
            "emne": objekt,
            "notater": objekt.notater.order_by("-opprettet", "-pk"),
            "navn_form": form,
            "tilbake_url": reverse("startside"),
            "tilbake_tekst": "Tilbake til Oversikt",
            "brodsmuler": [*_oversikt_brodsmule(), {"tekst": objekt.navn}],
        },
    )


@require_http_methods(["GET", "HEAD"])
def emne(request, pk):
    objekt = hent_egen(Emne, pk, request.user)
    form = EmneForm(initial={"navn": objekt.navn}, eier=request.user, emne=objekt)
    return _vis_emne(request, objekt, form)


@require_http_methods(["POST"])
def endre_navn(request, pk):
    objekt = hent_egen(Emne, pk, request.user)
    form = EmneForm(request.POST, eier=request.user, emne=objekt)
    if form.is_valid():
        try:
            gi_nytt_navn(objekt, form.cleaned_data["navn"])
        except IntegrityError:
            objekt.refresh_from_db(fields=["navn"])
            form.add_error("navn", feilmeldinger.NAVN_TATT)
        else:
            return redirect("studier:emne", pk=objekt.pk)
    return _vis_emne(request, objekt, form)


@require_http_methods(["GET", "HEAD", "POST"])
def slett_emne(request, pk):
    objekt = hent_egen(Emne, pk, request.user)
    if request.method == "POST":
        slett_emne_tjeneste(objekt)
        return redirect("startside")
    emne_url = reverse("studier:emne", args=[objekt.pk])
    return render(
        request,
        "studier/slett_emne.html",
        {
            "emne": objekt,
            "antall_notater": objekt.notater.count(),
            "antall_quizer": Quiz.objects.filter(notat__emne=objekt).count(),
            "tilbake_url": emne_url,
            "tilbake_tekst": f"Tilbake til {objekt.navn}",
            "brodsmuler": [
                *_oversikt_brodsmule(),
                {"tekst": objekt.navn, "url": emne_url},
                {"tekst": "Slett emne"},
            ],
        },
    )


def _emne_kontekst(objekt, siste, notat=None):
    """Tilbake og brødsmuler for en side under emnet: Oversikt › emne › `siste`.

    Med `notat` står notatet mellom emnet og `siste`, og Tilbake går til notatet.
    """
    emne_url = reverse("studier:emne", args=[objekt.pk])
    kontekst = {
        "emne": objekt,
        "tilbake_url": emne_url,
        "tilbake_tekst": f"Tilbake til {objekt.navn}",
        "brodsmuler": [
            *_oversikt_brodsmule(),
            {"tekst": objekt.navn, "url": emne_url},
            {"tekst": siste},
        ],
    }
    if notat is not None:
        notat_url = reverse("studier:notat", args=[notat.pk])
        kontekst["tilbake_url"] = notat_url
        kontekst["tilbake_tekst"] = f"Tilbake til {notat.originalnavn}"
        kontekst["brodsmuler"].insert(
            -1, {"tekst": notat.originalnavn, "url": notat_url}
        )
    return kontekst


@require_http_methods(["GET", "HEAD", "POST"])
def last_opp(request, pk):
    """S5 første gang (ingen notater i noen emner), ellers S6. Virker uten JavaScript (AD-13)."""
    objekt = hent_egen(Emne, pk, request.user)
    if request.method == "POST":
        form = NotatForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                notat = last_opp_tjeneste(
                    objekt, form.cleaned_data["fil"], request.user
                )
            except ValidationError as feil:
                form.add_error("fil", feil)
            else:
                return redirect("studier:notat", pk=notat.pk)
    else:
        if request.GET.get("videre") != "1" and not egne(Notat, request.user).exists():
            return render(
                request,
                "studier/bekreft_opplasting.html",
                _emne_kontekst(objekt, "Last opp notat"),
            )
        form = NotatForm()
    return render(
        request,
        "studier/last_opp.html",
        {
            **_emne_kontekst(objekt, "Last opp notat"),
            "form": form,
            "maks_storrelse": MAKS_STORRELSE,
            "feil": {
                "ingen": feilmeldinger.VELG_FIL,
                "for_stor": feilmeldinger.FIL_FOR_STOR,
                "format": feilmeldinger.FIL_FEIL_FORMAT,
                "tom": feilmeldinger.FIL_TOM,
                "avbrutt": feilmeldinger.OPPLASTING_AVBRUTT,
            },
        },
    )


@require_http_methods(["GET", "HEAD", "POST"])
def notat(request, pk):
    """S7: quizkortene og skjemaet for ny quiz (FR-11). POST lager eller gjenbruker jobben (FR-14)."""
    objekt = hent_egen(Notat, pk, request.user)
    if request.method == "POST":
        form = NyQuizForm(request.POST)
        if form.is_valid():
            jobb = opprett_jobb(
                objekt,
                form.cleaned_data["vanskelighetsgrad"],
                form.cleaned_data["antall"],
            )
            return redirect("studier:jobb", pk=jobb.pk)
    else:
        form = NyQuizForm()
    quizer = list(
        objekt.quizer.annotate(antall_sporsmal=Count("sporsmal")).order_by(
            "-opprettet", "-pk"
        )
    )
    # Modellen som laget quizen, aldri gjeldende innstilling (AD-11).
    for quiz in quizer:
        quiz.modellnavn = ki.visningsnavn(quiz.modell)
    return render(
        request,
        "studier/notat.html",
        {
            "notat": objekt,
            "form": form,
            "nivaer": NyQuizForm.base_fields["vanskelighetsgrad"].choices,
            "quizer": quizer,
            "testmodus_forhandslagret": feilmeldinger.TESTMODUS_FORHANDSLAGRET,
            "aktiv_jobb": aktiv_jobb(objekt),
            **_emne_kontekst(objekt.emne, objekt.originalnavn),
        },
    )


# De tre stegene på S8, i rekkefølge, med statusen som betyr at steget pågår.
_STEG = (
    (Jobbstatus.LESER, "Leser filen"),
    (Jobbstatus.LAGER, "Lager spørsmål"),
    (Jobbstatus.SJEKKER, "Sjekker quizen"),
)
_IKONER = {"ferdig": "✓", "pågår": "…", "venter": "○"}
# Feilkodene der S8 sier at filen er lagret (spec 2.5, B3).
_FIL_ER_LAGRET_KODER = (Feilkode.FORMAT, Feilkode.API_FEIL, Feilkode.API_NOKKEL)


def _fremdrift_kontekst(jobb, vent=False):
    rekkefolge = [status for status, _ in _STEG]
    if jobb.status == Jobbstatus.FERDIG:
        naa = len(_STEG)
    elif jobb.status in rekkefolge:
        naa = rekkefolge.index(jobb.status)
    else:
        naa = -1
    steg = []
    for nr, (_, tekst) in enumerate(_STEG):
        tilstand = "ferdig" if nr < naa else "pågår" if nr == naa else "venter"
        steg.append({"tekst": tekst, "tilstand": tilstand, "ikon": _IKONER[tilstand]})
    kontekst = {"jobb": jobb, "steg": steg, "vent": vent}
    if jobb.status == Jobbstatus.FEILET:
        kontekst["feilmelding"] = feilmeldinger.generering_feilet(jobb.feilkode)
        # Ikke for timeout (teksten sier det selv) eller koder som ber om ny opplasting.
        if jobb.feilkode in _FIL_ER_LAGRET_KODER:
            kontekst["fil_er_lagret"] = feilmeldinger.FIL_ER_LAGRET
    return kontekst


@require_http_methods(["GET", "HEAD"])
def jobb(request, pk):
    """S8: fremdriften. HTMX driver ett steg om gangen via `steg`.

    Ved feil står kodens tekst og «Prøv igjen», som virker uten JavaScript.
    """
    objekt = hent_egen(Genereringsjobb, pk, request.user)
    notat_objekt = objekt.notat
    # Setter jobben til `feilet`/`timeout` hvis fristen er ute (FR-15).
    aktiv_jobb(notat_objekt)
    objekt.refresh_from_db()
    if objekt.status == Jobbstatus.FERDIG:
        return redirect("studier:notat", pk=objekt.notat_id)
    return render(
        request,
        "studier/jobb.html",
        {
            **_fremdrift_kontekst(objekt),
            **_emne_kontekst(notat_objekt.emne, "Lager quiz", notat=notat_objekt),
            "ingen_serverkontakt": feilmeldinger.INGEN_SERVERKONTAKT,
        },
    )


def _sluttfragment(request):
    """Svaret når jobben ikke finnes lenger, for eksempel fordi notatet er slettet."""
    return render(
        request,
        "studier/_slutt.html",
        {"melding": feilmeldinger.NOTAT_FINNES_IKKE},
    )


@require_POST
def steg(request, pk):
    """Kjører ett steg og gir fremdriftsfragmentet. En ferdig jobb gir `HX-Redirect` til S9.

    `vist` er statusen siden sist viste. Er den uendret, byttes ikke #fremdrift.
    Finnes ikke jobben (aldri, eller slettet med notatet, også midt i et steg),
    gis et sluttfragment med status 200. En annens jobb gir 404.
    """
    objekt = hent_egen_eller_none(Genereringsjobb, pk, request.user)
    if objekt is None:
        return _sluttfragment(request)
    kjort = kjor_steg(objekt.pk)
    try:
        objekt.refresh_from_db()
    except Genereringsjobb.DoesNotExist:
        return _sluttfragment(request)
    # #fremdrift byttes bare når statusen er en annen enn den siden viser.
    endret = objekt.status != request.POST.get("vist") or objekt.status in (
        Jobbstatus.FERDIG,
        Jobbstatus.FEILET,
    )
    svar = render(
        request,
        "studier/_fremdrift.html",
        {**_fremdrift_kontekst(objekt, vent=not kjort), "endret": endret},
    )
    if objekt.status == Jobbstatus.FERDIG:
        # Quizen åpnes på spørsmål 1. En annen fane som spør etterpå, får samme økt.
        okt = start_eller_fortsett_okt(objekt.quiz)
        svar["HX-Redirect"] = reverse("studier:sporsmal", args=[okt.pk, 1])
    return svar


@require_POST
def start_quiz(request, pk):
    """«Ta quiz» på S7: fortsetter det påbegynte forsøket eller starter et nytt (AD-6)."""
    quiz = hent_egen(Quiz, pk, request.user)
    okt = start_eller_fortsett_okt(quiz)
    return redirect("studier:sporsmal", pk=okt.pk, nr=forste_ubesvarte(okt))


_NORSK = {"nb", "no", "nn"}


def _lang(sprak):
    """`lang`-verdien for spørsmål og alternativer. Tom for norsk, som sidemalen har."""
    hoved = (sprak or "").split("-")[0].lower()
    return "" if not hoved or hoved in _NORSK else sprak


def _vis_sporsmal(request, okt, nr, feil=False):
    """S9 for spørsmål `nr`. Aldri `er_riktig` eller `begrunnelse` i konteksten (AD-20)."""
    rad = element(okt, nr)
    sporsmal = (
        egne(Sporsmal, request.user)
        .select_related("quiz")
        .only("pk", "tekst", "quiz__modell", "quiz__sprak")
        .get(pk=rad["sporsmal"])
    )
    tekster = dict(
        egne(Alternativ, request.user)
        .filter(pk__in=rad["alternativer"])
        .values_list("pk", "tekst")
    )
    # Rekkefølgen kommer fra den stokkede listen, aldri fra databasen.
    alternativer = [{"id": pk, "tekst": tekster[pk]} for pk in rad["alternativer"]]
    valgt = (
        egne(Svar, request.user)
        .filter(okt=okt, sporsmal_id=sporsmal.pk)
        .values_list("alternativ_id", flat=True)
        .first()
    )
    notat = okt.notat
    antall = len(okt.innhold)
    posisjon = f"Spørsmål {nr} av {antall}"
    return render(
        request,
        "studier/sporsmal.html",
        {
            "okt": okt,
            "nr": nr,
            "antall": antall,
            "posisjon": posisjon,
            "notat": notat,
            "sporsmalstekst": sporsmal.tekst,
            "alternativer": alternativer,
            "valgt": valgt,
            "lang": _lang(sporsmal.quiz.sprak),
            "modellnavn": ki.visningsnavn(sporsmal.quiz.modell),
            "feilmelding": feilmeldinger.SVAR_IKKE_LAGRET if feil else "",
            **_emne_kontekst(notat.emne, posisjon, notat=notat),
        },
        status=400 if feil else 200,
    )


@require_http_methods(["GET", "HEAD", "POST"])
def sporsmal(request, pk, nr):
    """S9: ett spørsmål. POST lagrer svaret (hvis valgt) og går til Forrige, Neste eller S10 (AD-13).

    Virker uten JavaScript. Neste på siste spørsmål og «Se over og lever» går til S10.
    """
    okt = hent_egen(Okt, pk, request.user)
    rad = element(okt, nr)
    if rad is None:
        raise Http404("Fant ikke siden.")
    if request.method != "POST":
        return _vis_sporsmal(request, okt, nr)

    lever_url = reverse("studier:lever", args=[okt.pk])
    if okt.status != Oktstatus.PABEGYNT:
        # Story 3.3 sender til resultatsiden i stedet.
        return redirect(lever_url)
    retning = request.POST.get("retning")
    if retning not in ("forrige", "neste", "lever"):
        return HttpResponseBadRequest("Ukjent retning.")
    alternativ_id = request.POST.get("alternativ")
    if alternativ_id:
        alternativ = hent_egen(Alternativ, alternativ_id, request.user)
        if alternativ.pk not in rad["alternativer"]:
            return _vis_sporsmal(request, okt, nr, feil=True)
        sporsmal_objekt = hent_egen(Sporsmal, rad["sporsmal"], request.user)
        try:
            lagre_svar(okt, sporsmal_objekt, alternativ)
        except OktErLevert:
            return redirect(lever_url)
        except SvarAvvist:
            return _vis_sporsmal(request, okt, nr, feil=True)
    if retning == "forrige":
        return redirect("studier:sporsmal", pk=okt.pk, nr=max(nr - 1, 1))
    if retning == "lever" or nr >= len(okt.innhold):
        return redirect(lever_url)
    return redirect("studier:sporsmal", pk=okt.pk, nr=nr + 1)


@require_http_methods(["GET", "HEAD"])
def lever(request, pk):
    """S10 (skall): én lenke per spørsmål til S9 med «besvart» eller «ikke besvart».

    Levering kommer i story 3.3.
    """
    okt = hent_egen(Okt, pk, request.user)
    svart = besvarte(okt)
    notat = okt.notat
    sporsmal_liste = [
        {
            "nr": nr,
            "besvart": rad["sporsmal"] in svart,
            "url": reverse("studier:sporsmal", args=[okt.pk, nr]),
        }
        for nr, rad in enumerate(okt.innhold, start=1)
    ]
    return render(
        request,
        "studier/lever.html",
        {
            "okt": okt,
            "notat": notat,
            "sporsmal_liste": sporsmal_liste,
            **_emne_kontekst(notat.emne, "Se over og lever", notat=notat),
        },
    )
