"""Lager testdata direkte med ORM-en. Bare for tester."""

from django.contrib.auth import get_user_model
from django.utils import timezone

from studier.models import (
    Alternativ,
    Emne,
    Feilbankrad,
    Genereringsjobb,
    Notat,
    Okt,
    Oktstatus,
    Okttype,
    Quiz,
    Sporsmal,
    Svar,
)


def lag_bruker(email="ola@eks.no"):
    return get_user_model().objects.create_user(email, "hemmelig-passord")


def lag_kjede(bruker, emnenavn="HTML"):
    """Én rad av hver modell i `studier`, alle eid av `bruker`."""
    emne = Emne.objects.create(eier=bruker, navn=emnenavn)
    notat = Notat.objects.create(
        emne=emne,
        fil=f"notater/{bruker.pk}/test.pdf",
        originalnavn="forelesning.pdf",
        filtype="pdf",
        storrelse=1234,
    )
    jobb = Genereringsjobb.objects.create(
        notat=notat, vanskelighetsgrad="middels", antall=3
    )
    quiz = Quiz.objects.create(
        notat=notat,
        jobb=jobb,
        vanskelighetsgrad="middels",
        sprak="nb",
        modell="claude-sonnet-5-5",
        prompt_versjon="1",
    )
    sporsmal = Sporsmal.objects.create(
        quiz=quiz, tekst="Hva står HTML for?", begrunnelse="Det er standard."
    )
    riktig = Alternativ.objects.create(
        sporsmal=sporsmal, tekst="HyperText Markup Language", er_riktig=True
    )
    Alternativ.objects.create(sporsmal=sporsmal, tekst="High Tech Modern Language")
    okt = Okt.objects.create(notat=notat, quiz=quiz, type=Okttype.FORSOK)
    svar = Svar.objects.create(okt=okt, sporsmal=sporsmal, alternativ=riktig)
    feilbankrad = Feilbankrad.objects.create(sporsmal=sporsmal)
    return {
        Emne: emne,
        Notat: notat,
        Genereringsjobb: jobb,
        Quiz: quiz,
        Sporsmal: sporsmal,
        Alternativ: riktig,
        Okt: okt,
        Svar: svar,
        Feilbankrad: feilbankrad,
    }


def lag_olas(bruker):
    """`lag_kjede` med innhold i økten, og et levert forsøk med ett feil svar."""
    kjede = lag_kjede(bruker)
    sporsmal = kjede[Sporsmal]
    alternativer = list(
        sporsmal.alternativer.order_by("pk").values_list("pk", flat=True)
    )
    innhold = [{"sporsmal": sporsmal.pk, "alternativer": alternativer}]
    okt = kjede[Okt]
    okt.innhold = innhold
    okt.save(update_fields=["innhold"])
    feil = sporsmal.alternativer.get(er_riktig=False)
    levert = Okt.objects.create(
        notat=kjede[Notat],
        quiz=kjede[Quiz],
        type=okt.type,
        status=Oktstatus.LEVERT,
        levert_tidspunkt=timezone.now(),
        poengsum=0,
        antall=1,
        innhold=innhold,
    )
    Svar.objects.create(okt=levert, sporsmal=sporsmal, alternativ=feil)
    return {**kjede, "levert": levert, "feil": feil}


def godta(*brukere):
    """Godtatte vilkår, så VilkarMiddleware ikke svarer i stedet for viewet."""
    for bruker in brukere:
        bruker.vilkar_godtatt = timezone.now()
        bruker.save(update_fields=["vilkar_godtatt"])
