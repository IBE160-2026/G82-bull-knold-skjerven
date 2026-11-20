"""Lager testdata direkte med ORM-en. Bare for tester."""

from django.contrib.auth import get_user_model

from studier.models import (
    Alternativ,
    Emne,
    Feilbankrad,
    Genereringsjobb,
    Notat,
    Okt,
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
