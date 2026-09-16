---
title: "Product Brief: Foredragsnotater → Sammendrag & Quiz"
status: draft
created: 2026-09-16
updated: 2026-09-16
---

# Product Brief: Foredragsnotater → Sammendrag & Quiz

## Executive Summary

Studenter samler på store mengder foredragsnotater gjennom et semester, men å faktisk repetere dem effektivt før eksamen er en annen sak. Dette prosjektet er en nettapplikasjon hvor en student laster opp foredragsnotater (PDF eller tekst/Word), og får tilbake et sammendrag, en begrepsliste og et sett med quizspørsmål — automatisk generert av en KI-modell. Målet er ikke bare å spare tid, men å gi en mer aktiv, testbasert måte å repetere pensum på enn å lese notatene på nytt.

Prosjektet er punkt 8 på IBE160-kursets liste over godkjente prosjekttyper ("Foredragsnotater → Sammendrag & Quizgenerator"), og gruppen (G82: Christian R Bull, Henrik L Knold, Martin Skjerven, + ett medlem) bygger det som semesteroppgave i "Programmering med KI", med innlevering midt i desember 2026 **[ASSUMPTION: eksakt dato ikke bekreftet, antatt 15. desember 2026]**. Utviklingen gjøres med Claude Code som verktøy. Skulle produktet vise seg solid, vurderer gruppen å videreføre det som noe reelt studenter kan bruke — ikke bare et engangsprosjekt for karakteren.

## Problemet

Studenter møter forelesningsnotater i et format som er godt for å *ta imot* informasjon, men dårlig for å *repetere* den. Å lese gjennom lange PDF-er på nytt før eksamen er tidkrevende og passivt — det gir gjenkjenning, ikke nødvendigvis forståelse. Aktiv gjenkalling (f.eks. gjennom quizspørsmål) er en velkjent, effektiv læringsteknikk, men å lage gode quizspørsmål fra egne notater manuelt tar tid de færreste har midt i et travelt semester.

Resultatet: mange studenter repeterer mindre effektivt enn de kunne, eller venter til det er for sent til å bearbeide stoffet grundig.

## Løsningen

En webapplikasjon der studenten:

1. Logger inn (kontobeskyttet, se **Scope** for detaljer om hvorfor)
2. Laster opp forelesningsnotater som PDF eller tekst/Word-fil
3. Angir preferanser: ønsket lengde/detaljnivå på sammendraget, vanskelighetsgrad, og antall quizspørsmål
4. Får generert og presentert:
   - Et sammendrag av notatene
   - En begrepsliste (sentrale fagbegreper fra notatene)
   - Et sett quizspørsmål, hver med tre svaralternativer hvorav ett er riktig, med fasit

Genereringen drives av en KI-modell **[ASSUMPTION: leverandør/modell ikke valgt ennå — avgjøres i arkitekturfasen; naturlig kandidat er Claude siden gruppen allerede jobber i Claude-økosystemet via Claude Code, men dette er ikke bestemt]**.

## Hva gjør dette annerledes

Dette er ikke ment å konkurrere med generelle "last opp PDF, få sammendrag"-verktøy som allerede finnes. Differensieringen er:

- **Tett kobling mellom sammendrag og quiz** — quizspørsmålene er generert fra samme kilde og samme forståelse av stoffet som sammendraget, ikke to løsrevne verktøy.
- **Kursspesifikt fokus** — bygget for hvordan studenter faktisk jobber med pensum (forelesningsnotater, ikke generelle dokumenter), med begrepsliste som en eksamensrettet funksjon.
- **Enkel, lav terskel** — vanskelighetsgraden er vurdert som "enkel" i kursets egen prosjektliste; ambisjonen er en stram, velfungerende kjerneopplevelse fremfor mange halvferdige funksjoner.

Vi later ikke som dette er teknisk unikt — verdien ligger i at det er godt tilpasset studenthverdagen, ikke i en hemmelig algoritme.

## Hvem dette er for

**Primær bruker:** Studenter som ønsker å repetere pensum mer effektivt — i utgangspunktet studenter ved egen høyskole/kurs, men løsningen er ikke teknisk begrenset til dette **[ASSUMPTION: "hvem som helst om behovet er der" tolket som at appen bygges uten harde antagelser om institusjonstilhørighet, ikke som et krav om offentlig lansering i denne omgang]**.

Suksess for brukeren ser slik ut: de laster opp notater fra en forelesning, og på under et minutt har de et sammendrag og en quiz de kan teste seg selv med — og opplever at det faktisk reflekterer hva forelesningen handlet om, ikke generiske eller feilaktige spørsmål.

**Sekundær bruker (strekkmål, betinget):** Studenter med generelle spørsmål om kurset, betjent av en Kurs-FAQ-chatbot (punkt 7 i kursets prosjektliste) — bygges kun dersom hovedproduktet er solid med god margin til fristen.

## Suksesskriterier

Siden dette primært er en vurdert semesteroppgave, er suksess todelt:

**For karakteren / leveransen:**
- Punkt 8 er fullt fungerende: opplasting → sammendrag + begrepsliste + quiz, end-to-end
- Løsningen dekker kursets definerte data inn/ut og beslutningspunkter (se Scope)
- Innlogging fungerer og beskytter brukerens notater

**For produktet (dersom gruppen velger å gå videre):**
- Genererte sammendrag og quizspørsmål oppleves som *faktisk representative* for notatene (ikke generiske eller hallusinerte) — dette bør valideres manuelt av gruppen mot ekte forelesningsnotater før innlevering
- En student klarer å gå fra opplastet PDF til ferdig quiz uten å måtte forstå noe teknisk

## Scope

**Inn (MVP — punkt 8):**
- Brukerkonto/innlogging **[ASSUMPTION: mekanisme (enkel e-post/passord vs. Feide/SSO) ikke bestemt ennå — åpent spørsmål til arkitekturfasen]**
- Opplasting av forelesningsnotater som PDF eller tekst/Word
- Preferanser ved generering: lengde/detaljnivå på sammendrag, vanskelighetsgrad, antall quizspørsmål
- Generert sammendrag, begrepsliste og quiz med fasit (3 svaralternativer per spørsmål, ett riktig)
- Ingen kjøp/salg over nettet (bekreftet av kursspec — ikke relevant for dette produktet)

**Ut (eksplisitt, for nå):**
- Kurs-FAQ chatbot (punkt 7) — kun hvis god margin til frist, egen vurdering senere
- PowerPoint/bilde-opplasting — kun tekst/Word og PDF støttes i første versjon
- Offentlig/institusjonsbred lansering — bygges teknisk åpent, men lansering utover kursgruppen er ikke i scope nå
- Valg av spesifikk KI-modell/leverandør for produksjon — avgjøres i arkitekturfasen, ikke låst her

**Kjent, ikke-bundet ressurs:** Det finnes en tom Python-prosjektskjelett i en nabomappe (`C:\IBE160\backend`, separat git-repo). Den er *ikke* koblet til dette prosjektet i dag, men kan tas i bruk senere dersom den passer den valgte teknologistacken.

## Visjon

Dersom punkt 8 blir et solid produkt innen fristen, ser gruppen for seg å bygge videre med Kurs-FAQ-chatboten (punkt 7) som et naturlig neste steg — et verktøy som dekker både *repetisjon av konkret pensuminnhold* (sammendrag/quiz) og *spørsmål om kurset* (chatbot med kildehenvisning) i én sammenhengende studieassistent. På lengre sikt er ambisjonen at dette blir noe som faktisk brukes av studenter, ikke bare en innlevert oppgave — men denne brief'en dekker bevisst kun det gruppen har forpliktet seg til foran fristen i desember.

## Åpne spørsmål

- Hvilken KI-modell/leverandør skal brukes i produksjon for sammendrag- og quizgenerering?
- Hvilken innloggingsmekanisme (enkel konto vs. institusjonell SSO)?
- Eksakt innleveringsfrist (antatt midt/15. desember 2026 — bør bekreftes mot emneplanen)
- Skal `backend`-skjelettet i nabomappen tas i bruk, og i så fall hvordan?
