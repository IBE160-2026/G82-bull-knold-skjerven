# Tilbakemelding på PRD

| | |
|---|---|
| **Gruppe** | G82 – G82-bull-knold-skjerven |
| **PRD vurdert** | `_bmad-output/planning-artifacts/prds/prd-G82-bull-knold-skjerven-2026-11-11/prd.md` (status `final`, sist endret 2026-11-11, commit e5cf6bc) |
| **Dato** | 2026-11-12 |
| **Type** | Formativ tilbakemelding, ikke karakter |

## 1. Samlet inntrykk

Dette er en sterk PRD med en tydelig tese (læringssløyfen notat → quiz → feilbank → lært), testbare krav og ærlig avgrensning. Den største risikoen er ikke manglende kvalitet, men to sammenhenger som ikke er tenkt helt til ende: hva som skjer når KI-en lager en feil fasit, og hva et «spørsmål» er når det kan gå igjen i flere quizer. Begge treffer kjernen i appen, og begge bør avklares før arkitektur og epics.

## 2. Dette fungerer godt

- **Testbare krav.** FR-ene har konsekvenser som kan bli testtilfeller direkte, og regneeksempler brukes der det trengs: «Lett 100 %, middels 50 % og vanskelig uten quiz gir 35 %» (FR-24), «80 % og 40 % gir 60 %» (FR-25). SM-3 kobler dette til automatiske tester.
- **KI, kostnad og kjørbarhet er tenkt gjennom.** Testmodus med mock-svar, testbruker, `.env`, formatsjekk med én ny generering, manuell kvalitetsvurdering med 90 %-grense (SM-2) og sporbar modell/prompt (NFR-7). Dette svarer direkte på briefen-tilbakemeldingen.
- **Ærlig scope.** §6 og §7.2 sier hva appen ikke er, FR-10 er fjernet med ID beholdt, og sammendrag er bevisst tatt ut. Motmålene (SM-C1 til SM-C3) er knyttet til faktiske risikoer, ikke pynt.

## 3. Oversikt per dimensjon

| Dimensjon | Vurdering | Kort begrunnelse |
|---|---|---|
| Beslutningsklarhet | sterk | Valg er tatt og begrunnet (addendum, kap. 9 og 10), åpne spørsmål er reelt åpne. |
| Substans | sterk | Persona, ordliste og NFR-er er produktspesifikke, ikke boilerplate. |
| Strategisk sammenheng | sterk | Alle funksjoner tjener samme sløyfe; dekningsgraden er vektet mot tesen. |
| Testbarhet | god | Nesten alle FR-er har konsekvenser. Hull: ugyldig innhold, API-feil og tvetydig spørsmålsidentitet. |
| Scope og avgrensning | god | Tydelige utelatelser, men v1 er stort for tre personer og ca. fem uker, og har ingen kuttrekkefølge. |
| Brukbarhet for neste fase | god | Ordliste og ID-er er stort sett konsekvente. Noen motsigelser i begrepsbruk (se kap. 5). |
| Formtilpasning | sterk | UJ-er med navngitt hovedperson passer en brukerrettet app. |

## 4. Viktigste forbedringer

### 4.1 Skjult fasit + mulig feil fra KI = student som sitter fast
- **Alvorlighet:** høy
- **Hvor:** FR-19 «Fasiten vises ikke for spørsmål som er besvart feil», FR-23 «Fasiten vises ikke før spørsmålet er lært», SM-2 (≥ 90 % riktige)
- **Problem og hvorfor det betyr noe:** Dere godtar selv at opptil 10 % av spørsmålene kan ha feil fasit. Hvis studenten svarer riktig, men KI-ens fasit er feil, havner spørsmålet i feilbanken, og den eneste veien ut er å velge det gale svaret to ganger på rad. Studenten kan heller aldri se hvorfor. Motsatt: med tre alternativer er sjansen for å «lære» et spørsmål ved ren gjetning 1/9. Begge deler svekker tesen om aktiv gjenkalling, og ingen krav beskriver hvordan feil oppdages i appen. Begrunnelsen for å skjule fasiten står heller ikke i PRD-en.
- **Forslag:** Legg til et FR, for eksempel: «FR-31: Melde spørsmål. En bruker kan markere et spørsmål som feil eller uklart. Konsekvenser: spørsmålet tas ut av feilbanken, teller ikke i nevneren i dekningsgraden, og vises ikke i nye økter. Meldingen lagres med spørsmål-ID og tidspunkt.» Vurder også en kort begrunnelse per fasit som vises når spørsmålet er lært, og skriv i kap. 9 hvorfor fasiten skjules.

### 4.2 «Spørsmål» er definert to ulike steder
- **Alvorlighet:** høy
- **Hvor:** Ordliste «Spørsmål: Hører til én quiz», FR-16 «Spørsmål kan gå igjen på tvers av quizer om samme notat», FR-21 «Et spørsmål ligger høyst én gang i feilbanken», FR-24 «alle spørsmålene på det nivået i notatets quizer»
- **Problem og hvorfor det betyr noe:** Hvis samme spørsmålstekst finnes i to quizer, er det da ett eller to spørsmål? Svaret avgjør datamodellen, om feilbanken kan inneholde duplikater og hva nevneren i dekningsgraden er. Arkitektur og stories må gjette.
- **Forslag:** Velg og skriv det i ordlisten, for eksempel: «Spørsmål hører til én quiz og telles separat, også når teksten er lik et spørsmål i en annen quiz. Feilbanken har høyst én rad per spørsmål-ID.» Legg til en konsekvens i FR-21: «Et feilsvar på spørsmål A i quiz 1 påvirker ikke spørsmål A' med lik tekst i quiz 2.» (eller omvendt, hvis dere velger identitet på tekst).

### 4.3 Mangler krav for innhold som ikke kan bli en god quiz, og for API-feil
- **Alvorlighet:** medium
- **Hvor:** FR-12 «En PDF på 10 sider gir nøyaktig det valgte antallet spørsmål», FR-8 «uansett sideantall», FR-13, FR-15
- **Problem og hvorfor det betyr noe:** Bare formatfeil og timeout er håndtert. Hva skjer med en TXT på tre setninger når brukeren ber om 30 spørsmål uten duplikater, en PDF uten lesbart innhold, en veldig lang PDF (modellen har trolig en sidegrense, sjekk den), eller en ugyldig nøkkel, brukt opp kvote eller nettfeil? Dette er de feilene sensor og medstudenter faktisk treffer.
- **Forslag:** Ett FR med konsekvenser: «Er det valgte antallet spørsmål ikke mulig å lage fra filen, eller svarer API-et med feil, vises en melding som sier hva som gikk galt og hva brukeren kan gjøre. Ingen quiz lagres, og knappen låses opp.» Test med minst én kort fil og én ugyldig nøkkel.

### 4.4 V1 mangler kuttrekkefølge
- **Alvorlighet:** medium
- **Hvor:** §7.1 «Alt i kap. 4», NFR-8, SM-6, SM-7; frist 15.12 (kap. 9)
- **Problem og hvorfor det betyr noe:** 30 FR, full WCAG 2.2 A/AA med skjermleser- og tastaturtest, 3–5 brukertester, mobil, automatiske tester og README skal gjøres av tre personer på rundt fem uker. SM-C3 sier at en stram sløyfe veier tyngre, men ikke hva som kuttes først når tiden går.
- **Forslag:** Merk kravene i tre grupper: «kjerne» (FR-1 til FR-4, FR-7 til FR-9, FR-11 til FR-13, FR-17, FR-19, FR-21, FR-23, FR-27 til FR-30), «bør» og «kan kuttes først» (for eksempel FR-18 fortsette fra annen enhet, FR-25, FR-22 med ny stokking). Da kan epics ordnes slik at kjerneløpet er ferdig tidlig.

### 4.5 Dekningsgraden oppfører seg på måter som ikke er skrevet ned
- **Alvorlighet:** lav
- **Hvor:** FR-24 «Et nivå uten quiz teller som 0 %», FR-19
- **Problem og hvorfor det betyr noe:** Konsekvensene er riktige, men uventede for studenten: dekningsgraden faller når en ny quiz lages (flere ubesvarte spørsmål i nevneren), og over 50 % krever quizer på alle tre nivåer. Det er fint hvis det er bevisst, men UX og tester bør få det som krav. FR-19 sier heller ikke om fasiten vises for riktige svar.
- **Forslag:** Legg til to konsekvenser i FR-24: «Lager brukeren en ny quiz, regnes dekningsgraden på nytt og kan gå ned» og «Uten quiz på vanskelig kan dekningsgraden ikke bli over 50 %». I FR-19: «Fasiten vises for spørsmål som er besvart riktig.»

## 5. Mekaniske funn

- **Forsøk og økt:** Ordlisten definerer *Forsøk* som en gjennomføring av en quiz, men kap. 10 sier at «Øv på feil» «lagres underveis som et forsøk», mens FR-22 sier økten ikke vises i historikken. Bruk ett begrep (for eksempel «øvingsøkt») og si eksplisitt at den ikke er et forsøk.
- **UJ-dekning:** FR-2, FR-5, FR-6, FR-9 og FR-20 refereres ikke fra noen UJ. Det er greit for støttekrav, men FR-6 og FR-20 kunne vært en linje i UJ-2.
- **UJ-3:** Feiltilfellet med timeout hører mer naturlig hjemme i en egen UJ eller under UJ-1.
- **FR-9 og kap. 9, spørsmål 1:** FR-9 fastslår at PDF sendes hel, mens åpent spørsmål 1 spør om den bør det. Velg én, eller skriv at FR-9 er «foreløpig».
- **Teknologi i krav:** Modellnavnet i FR-29 og én-modul-kravet i NFR-5 er arkitekturvalg. De fungerer, men kunne stått i addendum.
- ID-ene FR-1 til FR-30 er sammenhengende, og kryssreferansene løser seg. Ingen sensitive opplysninger funnet.

## 6. Før dere går videre

**Må avklares før UX, arkitektur og epics:**
1. Spørsmålsidentitet (4.2): påvirker datamodellen.
2. Hva skjer ved feil fasit (4.1): påvirker skjermbilder for resultat og feilbank.
3. Kjerne vs. kan-kuttes (4.4): påvirker rekkefølgen på epics.

**Kan vente:** Åpne spørsmål 1–3 i kap. 9 (modell, testdokumenter, genereringstid). Kravene for feilhåndtering (4.3) kan skrives sammen med arkitekturen.

**Oppfølging av briefen-tilbakemeldingen: ja.** Interaktiv quiz med poeng og «øv på feil» er med, kravene er testbare, modell/`.env`/testmodus/testbruker er beskrevet, og chatboten er utelatt. Merk at PRD-en har tatt sammendrag og begrepsliste ut av v1, mens briefen fortsatt beskriver dem. Oppdater briefen, eller skriv at PRD-en erstatter den på dette punktet.

## 7. Refleksjonsspørsmål

1. Hvilke deler av PRD-en kom fra KI-forslag, og hvilke kom fra gruppens egne diskusjoner (for eksempel valget om å skjule fasiten)? Hvordan sjekket dere at valget faktisk hjelper læring?
2. Hvordan ville dere oppdaget at KI-en hadde laget en feil fasit hvis dere ikke hadde brukt SM-2? Hva sier det om hva appen selv bør kunne gjøre?

_Vurdert mot kvalitetsrubrikken i bmad-prd. Dette er veiledning, ikke sensur._
