---
title: "Product Brief v2 (individuelt utkast): Foredragsnotater → Sammendrag & Quiz"
status: individual-draft
author: "Magnus"
created: 2026-10-26
---

## Executive Summary

En webapp der studenter laster opp forelesningsnotater og får sammendrag, begrepsliste og en quiz generert av KI. Quizen tas i appen, og feilsvar gir oppfølgingsquizer til stoffet er dekket, målt som *coverage*. Trinn 2 lar studenten laste opp et helt emne som en ZIP-fil og få quizer for hele pensum. IBE160, forslag 8, gruppe G82.

## Problemet

Å lese notater på nytt gir gjenkjenning, ikke forståelse. Aktiv gjenkalling virker, men å lage quizspørsmål selv tar tid studenter ikke har.

## Løsningen

**Trinn 1 (MVP):**
1. Studenten logger inn med e-post og passord.
2. Studenten laster opp et notat (PDF, DOCX eller TXT) og velger detaljnivå, antall spørsmål og vanskelighetsgrad (glidebryter).
3. Appen viser stegvis fremdrift, og sammendraget vises mens quizen lages.
4. Studenten tar quizen og får poeng.
5. Feilsvar gir en oppfølgingsquiz med lignende spørsmål, de opprinnelige feilsvarene til slutt og en lesebeskjed om temaene.
6. Historikken per notat viser coverage per quiz.

**Trinn 2 (før fristen):** Studenten laster opp en ZIP-fil med et helt emne. KI-en deler alt innholdet i forelesninger, og støttefiler havner hos riktig forelesning. Hver forelesning blir ett notat med egen quiz, og emnet får samlet coverage. Studenten har ansvaret for at ZIP-filen bare inneholder PDF, DOCX og TXT.

Modellen er Sonnet 5.5. Nøkkelen ligger i `.env`, og repoet har `.env.example`. Testmodus med mock-svar, testbruker og faste testdokumenter gjør at appen kan kjøres uten nøkkel.

## Hva gjør dette annerledes

Sammendrag, quiz og oppfølging bygger på samme stoff, og appen følger opp feilene til de er rettet, både per forelesning og for hele emnet.

## Hvem dette er for

Studenter generelt, med åpen registrering. Innholdet genereres på notatets språk. Notatet bestemmer grunnivået, og glidebryteren justerer fra det.

## Suksesskriterier

- **Innlogging:** Feil passord avvises, og ingen bruker ser andres notater.
- **Quiz:** En PDF på 10 sider gir valgt antall spørsmål, hvert med nøyaktig tre alternativer og ett riktig svar. Svar i feil format genereres på nytt.
- **Avvisning:** Under ~200 tegn per side i snitt gir avvisning med melding.
- **Coverage:** 8 av 10 riktige gir 80 %. Ett gammelt spørsmål riktig i oppfølgingen gir 90 %. Senere feilsvar trekker ikke ned.
- **Oppfølging:** Alle feilsvar fra en runde kommer sist i neste quiz, og lesebeskjeden nevner temaet for hvert av dem.
- **Robusthet:** Resultatet er der etter at fanen er lukket. En feilet generering kan startes på nytt uten ny opplasting.
- **ZIP:** En test-ZIP med 3 kjente forelesninger og støttefiler gir 3 notater og 3 quizer, med hver støttefil hos riktig forelesning. Emnets coverage er snittet av quizene.
- **Kjørbarhet:** Appen kjører etter README i testmodus, uten API-nøkkel.
- **KI-kvalitet:** Vi tester 2 fag × 2 PDF-er, minst én av dem en lysbilde-PDF. Hvert spørsmål skal være relevant for temaet, ikke overlappe med andre og ha riktig fasit. Resultatet dokumenteres.
- **Sletting:** Når et notat slettes, forsvinner tekst, quizer og historikk.

## Scope

**Inn:** Trinn 1, deretter trinn 2, begge før fristen.

**Ut:** Kurs-FAQ-chatbot, Canvas-crawling, Feide/SSO, PPTX og bilder, OCR, lagring av original-PDF, flagging av spørsmål og repetisjon med intervaller.

## Visjon

En studieassistent som tar studenten fra et helt emne til mestring, synlig i coverage **[ASSUMPTION: frist ca. 15. desember 2026]**.

## Åpne spørsmål – mitt standpunkt

1. **Sonnet 5.5**, fordi den gir god ytelse per kostnad. Appen sjekker at det finnes ett riktig svar, ellers virker ikke poengene. Ellers sikres kvaliteten med testrammeverket. Studenten kan ikke flagge spørsmål, fordi fokus skal være på å svare. **[ASSUMPTION: antall alternativer er uviktig, men låses til 3 for testbarhet]**
2. **KI-generert oppfølgingsquiz** med lignende spørsmål og de opprinnelige feilsvarene til slutt, i ubegrenset antall runder. Vi antar at studenten heller leser seg opp enn å feile gang på gang. **[ASSUMPTION: lesebeskjeden er fritekst, ikke en lenke til sammendraget]**
3. **Prøv**, og avvis bare dokumenter nesten uten tekst. Modellen forstår tema og nivå og kan bruke egen fagkunnskap. Verst er en irrelevant quiz, ikke en avvisning.
4. **Stegvis fremdrift, med sammendraget først.** Forespørsel og svar lagres, så resultatet overlever en lukket fane. Det krever en bakgrunnsjobb, som også trengs for ZIP-opplasting.
5. **Ambisiøs:** emne → notater → quizer → oppfølgingsrunder, med coverage på hvert nivå. Bare uthentet tekst lagres. Coverage er appens egen logikk og det mest testbare vi har.
6. **Studenter generelt**, og notatets språk og nivå styrer. **[ASSUMPTION: det er ikke avklart om det skal være et tak på bruk per bruker. Med åpen registrering og ZIP-opplasting kan én bruker utløse mange KI-kall på vår nøkkel]**
