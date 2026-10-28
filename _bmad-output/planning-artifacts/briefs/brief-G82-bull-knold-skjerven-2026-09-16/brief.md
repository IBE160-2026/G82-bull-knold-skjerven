---
title: "Product Brief: Foredragsnotater → Sammendrag & Quiz"
status: v2
created: 2026-09-16
updated: 2026-10-28
---

# Product Brief v2: Foredragsnotater → Sammendrag & Quiz

## Executive Summary

En webapp der studenter laster opp forelesningsnotater under egne emner og får sammendrag, begrepsliste og quiz generert av KI. Quizen tas i appen og gir poeng. Feilsvar havner i en feilbank til de er lært, og en vektet dekningsgrad viser hvor godt studenten kan stoffet. Gruppe G82 lager appen som semesteroppgave i IBE160 (forslag 8), med BMAD og Claude Code.

## Problemet

Å lese notater på nytt før eksamen gir gjenkjenning, ikke forståelse. Aktiv gjenkalling virker bedre, men å lage gode quizspørsmål selv tar tid studenter sjelden har. Studenten vet heller ikke hva hen faktisk ikke kan.

## Løsningen

1. **Innlogging** med e-post og passord. Hver bruker ser bare sine egne data.
2. **Emner** opprettes av studenten, og notatene legges under dem.
3. **Opplasting** av PDF, DOCX eller TXT på maks 5 MB, uansett sideantall. PDF-en sendes hel til modellen, så lysbilder og skannede sider fungerer. Fra DOCX og TXT hentes teksten ut. Siden minner om at innholdet sendes til en ekstern KI-tjeneste.
4. **Preferanser:** detaljnivå, vanskelighetsgrad (lett, middels eller vanskelig) og antall spørsmål. Studenten kan lage flere quizer per notat.
5. **Generering med trinnvis fremdrift.** Sammendraget vises mens quizen lages, og knappen er låst mens appen jobber. Ved timeout vises «Prøv igjen». Originalfilen er lagret, så studenten slipper å laste opp på nytt.
6. **Quiz i appen:** tre alternativer og ett riktig svar. Studenten må svare på alle spørsmålene før levering, og ser bare riktig eller galt, ikke fasiten.
7. **Feilbank per notat.** «Øv på feil» gir spørsmålene i feilbanken med alternativene i ny rekkefølge og uten fasit. To riktige på rad gjør et spørsmål «lært», og da vises fasiten. Et nytt feilsvar nullstiller telleren.
8. **Dekningsgrad og historikk.** Et spørsmål er dekket når det er besvart riktig og ikke ligger i feilbanken. Dekningen regnes samlet per nivå, også på tvers av quizer. Dekningsgraden for et notat er 20 % × lett + 30 % × middels + 50 % × vanskelig. Historikken viser alle forsøk med dato og poengsum.
9. **Sletting** av et notat fjerner filen og alle data som hører til.

Quiz, feilbank og historikk fungerer på mobilskjerm. Genereringen gjøres av Claude Sonnet 5.5, og modellen kan byttes i konfigurasjonen. Nøkkelen ligger i `.env`, og repoet har `.env.example`. **Testmodus** bruker mock-svar som er lagret fra ekte kjøringer på faste testdokumenter. Den har også en testbruker, slik at hele flyten kan kjøres uten API-nøkkel.

## Hva gjør dette annerledes

Sammendrag, quiz og øving bygger på samme notat. Appen følger opp feilene til de er lært, og dekningsgraden belønner at studenten mestrer de vanskelige spørsmålene. Appen er ikke teknisk unik. Verdien ligger i en stram læringssløyfe.

## Hvem dette er for

Studenter generelt, men appen designes og testes med medstudenter. Grensesnittet er på norsk, og innholdet genereres på notatets språk. En typisk bruker forbereder seg på pc og øver på mobilen.

## Suksesskriterier

- **Innlogging:** Feil passord avvises, og en e-post som allerede er registrert, gir feilmelding. Ingen bruker ser andres data, heller ikke ved å endre ID-er i URL-en.
- **Opplasting:** Alle de faste testdokumentene gir generert innhold, også lysbilde-PDF-en og en skannet PDF. En fil over 5 MB eller i feil format avvises med en melding.
- **Quiz:** En PDF på 10 sider gir det valgte antallet spørsmål, hvert med tre ulike alternativer og ett riktig svar. Et svar i feil format genereres på nytt én gang og gir ellers en feilmelding.
- **Feilbank:** Et feilsvar havner i feilbanken. To riktige på rad fjerner spørsmålet derfra, og et nytt feilsvar nullstiller telleren. Fasiten vises ikke før spørsmålet er lært.
- **Dekningsgrad:** Lett 100 %, middels 50 % og vanskelig ikke tatt gir 35 %.
- **Ventetid:** Sammendraget vises før quizen er ferdig. Ved timeout får studenten «Prøv igjen» uten ny opplasting.
- **Sletting:** Når et notat slettes, forsvinner alle data som hører til det, og andre notater påvirkes ikke.
- **Mobil:** Quiz og feilbank kan brukes på en skjerm som er 360 px bred, uten vannrett rulling.
- **Kjørbarhet:** Med en ny klone og README-en kjører hele kjerneflyten i testmodus uten API-nøkkel.
- **KI-kvalitet:** Testdokumentene kjøres med ekte modell. Minst 90 % av spørsmålene skal være relevante, ha riktig fasit og ikke være tvetydige. Resultatet dokumenteres med modell, dato og prompt-versjon.
- **Brukertest:** 3–5 medstudenter har testet appen, og funnene er dokumentert.

## Scope

**Inn i v1:** Alt under Løsningen.

**Ut av v1:** Kurs-FAQ-chatbot, Feide/SSO, PPTX og bilder (studenten eksporterer til PDF), bakgrunnsjobb, ZIP-opplasting, intervall-repetisjon, flagging av spørsmål, automatisk faktasjekk og offentlig hosting **[ASSUMPTION: lokal kjøring, avklares med faglærer]**.

## Visjon

Målet for semesteret er en solid, testet og dokumentert app som sensor kan kjøre selv.

**Videre arbeid:**
- KI-genererte oppfølgingsquizer med nye spørsmål om temaene studenten bommet på
- flagg der studenten markerer et tema som vanskelig, som kan styre oppfølgingsquizene
- en egen KI-modell som kontrollerer spørsmålene automatisk
- bakgrunnsjobb, slik at genereringen fortsetter når fanen lukkes
- samlet øving per emne
- hosting med bruksgrense (f.eks. 10 genereringer per døgn) og utgiftstak
- intervall-repetisjon

## Åpne spørsmål

- **Til faglærer:** Er testmodus med mock-svar nok, og kan det være valgfritt for sensor å legge inn egen nøkkel?
- **Til faglærer:** Er lokal kjøring nok, eller forventes en hostet versjon?
- **Til faglærer:** Hva er den eksakte fristen? Vi antar 15. desember 2026.
- **Hva er billigst og best:** å sende hele PDF-en eller å hente ut teksten? Og holder Haiku 5.5 kvaliteten mot Sonnet 5.5? Begge deler avgjøres i testfasen.
- **Hvordan regnes dekningsgraden for et emne?** **[ASSUMPTION: snittet av notatene]**
- **Hvilke testdokumenter kan brukes uten å bryte opphavsretten?**
