# Brukertest 6.5: medstudenter tester FåreQuiz

Story 6.5. Krav: SM-6, NFR-1, FR-18. Gruppa lar 3–5 medstudenter løse oppgaver fra brukerreisene UJ-1 til UJ-3 uten hjelp. Gruppa noterer hvor de stopper, hva de misforstår og hva de sier. Minst én av dem tar et påbegynt forsøk videre på mobil. Funnene dokumenteres med alvorlighet og blir enten rettet eller ført som åpent punkt med begrunnelse.

Dokumentet har tre deler: forberedelse, gjennomføring og funn. Kopier observasjonsskjemaet én gang per deltaker.

## 1. Forberedelse

### Sjekkliste før første deltaker

- [ ] Appen er klonet fra `main` og startet etter README-en. Testmodus er nok, og banneret vises. Med ekte modell må `.env` ha nøkkelen og `TESTMODUS=0`.
- [ ] Databasen er tom for deltakerne. Hver deltaker lager sin egen konto, så det blir ingen spor etter forrige deltaker.
- [ ] Testdokumentene ligger klare på skrivebordet: `html-struktur-og-semantikk.pdf`, `css-layout-lysbilder.pdf` og `javascript-og-dom.txt` fra `testdokumenter/`.
- [ ] Mobilen er satt opp etter README-avsnittet «Mobil på samme nett». Maskinens IP-adresse står i `ALLOWED_HOSTS`, og serveren kjører med `runserver 0.0.0.0:8000`. Prøv adressen på mobilen før testen.
- [ ] Nettleseren på PC-en er i vanlig vindu, med zoom 100 % og ingen lagrede innlogginger for appen.
- [ ] Rollene er fordelt: én **leder** som leser opp og gir oppgavene, og én eller to **observatører** som skriver. Lederen hjelper ikke. Svaret på spørsmål er «Hva ville du gjort hvis du var alene?»
- [ ] Hver deltaker har sagt ja til å være med. Navn skrives ikke ned. Deltakerne kalles D1–D5.

### Hvem

| Deltaker | Studieprogram og år | Har brukt quiz-apper før | Enhet for mobiloppgaven | Dato |
|---|---|---|---|---|
| D1 | | | | |
| D2 | | | | |
| D3 | | | | |
| D4 | | | | |
| D5 | | | | |

Minst én deltaker gjør oppgave 7 på mobil (SM-6).

## 2. Gjennomføring

### Introduksjon (lederen leser opp)

> Takk for at du vil være med. Vi tester appen, ikke deg, så det finnes ingen gale svar. Tenk gjerne høyt: si hva du ser etter, hva du tror skjer og hva som overrasker deg. Vi hjelper deg ikke underveis, fordi vi vil se hvor appen ikke forklarer seg selv. Hvis du står fast, kan du si «jeg gir opp», så går vi videre. Det tar cirka 25 minutter.

### Oppgavene

Oppgavene beskriver hva deltakeren vil oppnå, ikke hvilke knapper de skal trykke. Lederen gir én oppgave om gangen og leser den ordrett.

| # | Oppgave (leses opp) | Reise | Observatøren ser etter |
|---|---|---|---|
| 1 | «Du har hørt om en app som lager quizer fra forelesningsnotater. Lag deg en bruker.» | UJ-1 | Finner registreringen, forstår feilmeldinger og vilkår/personvern-dialogen |
| 2 | «Du tar faget Webutvikling. Gjør klar et sted i appen for det faget.» | UJ-1 | Finner «Nytt emne», forstår ordet «emne» |
| 3 | «Legg inn forelesningsnotatet om HTML. Det ligger på skrivebordet.» | UJ-1 | Finner opplastingen, forstår vilkårene før første opplasting, ser fremdriften |
| 4 | «Lag en quiz på middels nivå med 10 spørsmål.» | UJ-1 | Valg av nivå og antall, forstår stegene mens quizen lages og at knappen er låst |
| 5 | «Ta quizen og lever. Fortell hvor mange du fikk riktig, og hvilke du svarte feil på.» | UJ-1 | Navigering mellom spørsmål, «Se over og lever», forstår resultatet uten fasit, ser KI-merket |
| 6 | «Du skal teste deg på samme notat en gang til. Svar på omtrent halvparten av spørsmålene og lukk fanen, som om du må gå.» | UJ-3 | Finner «Ta på nytt», tør å lukke fanen |
| 7 | «Senere åpner du appen på mobilen. Fortsett der du slapp, og lever.» (Minst én deltaker gjør dette på mobil, de andre på PC-en.) | UJ-3 | Logger inn på mobilen, finner «Fortsett der du slapp» eller «Påbegynt», ser at svarene er lagret, kan lese og trykke på liten skjerm |
| 8 | «Øv på spørsmålene du har svart feil på. Finn ut hva som skjer når du svarer riktig.» | UJ-2 | Finner «Øv på feil», forstår regelen om to riktige på rad og at fasiten vises når et spørsmål er lært |
| 9 | «Legg inn ett notat til, om CSS eller JavaScript, og lag en quiz på et annet nivå.» | UJ-2 | Gjenbruker det de lærte i oppgave 3–4 |
| 10 | «Hvor mye av faget har du øvd på nå? Og når tok du quizene?» | UJ-2 | Finner dekningsgraden for notat og emne, og historikken |
| 11 | (Valgfri) «Du synes et av spørsmålene var uklart. Si fra om det.» | UJ-2 | Finner «Meld som feil eller uklart» og forstår at det ikke kan angres |

Merknader til oppgavene:

- I testmodus kommer spørsmålene fra mock-svar, og «Ta på nytt» gir de samme spørsmålene. Si det til deltakeren hvis de lurer.
- En fil som ikke er et testdokument, gir en quiz fra standarddokumentet og en merknad om det. Gi bare testdokumentene til deltakerne.
- Timeout og «Prøv igjen» (feiltilfellet i UJ-3) kan ikke testes med mock-svar. Det står ikke på oppgavelisten.
- Ett spørsmål blir lært først etter to riktige svar på rad etter at det kom i feilbanken. I oppgave 8 holder det at deltakeren forstår regelen. Det trenger ikke å skje.

### Spørsmål etterpå (lederen spør)

1. Hva var lettest, og hva var vanskeligst?
2. Var det noe du ikke skjønte, eller ord du ikke forstod?
3. Hva tenkte du om merket «Laget av KI» og at spørsmålene kan inneholde feil?
4. Ville du brukt appen før en eksamen? Hvorfor eller hvorfor ikke?
5. Hvis du kunne endre én ting, hva ville det vært?

### Observasjonsskjema (ett per deltaker)

Deltaker: D__ · Dato: ____ · Leder: ____ · Observatør: ____ · Enhet i oppgave 7: PC / mobil (modell og nettleser: ____)

| # | Løst? (ja / med nøling / gav opp) | Tid (ca.) | Hvor stoppet de? | Hva misforstod de? | Hva sa de? (sitat) |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |
| 6 | | | | | |
| 7 | | | | | |
| 8 | | | | | |
| 9 | | | | | |
| 10 | | | | | |
| 11 | | | | | |

Svar på spørsmålene etterpå:

1.
2.
3.
4.
5.

## 3. Funn

Samle funnene etter alle testene. Ett funn per problem. Skriv hvor mange deltakere som møtte det.

Alvorlighet:

- **Kritisk:** deltakeren kom ikke videre eller mistet data. Rettes før levering.
- **Alvorlig:** deltakeren kom videre, men med stor nøling eller feil forståelse. Bør rettes.
- **Mindre:** kort nøling eller en kommentar. Rettes hvis det er enkelt.
- **Kosmetisk:** ordvalg, utseende. Føres som åpent punkt hvis det ikke rettes.

| # | Skjermbilde og oppgave | Funn | Deltakere (av N) | Alvorlighet | Rettet (commit) eller åpent punkt med begrunnelse |
|---|---|---|---|---|---|
| F1 | | | | | |
| F2 | | | | | |
| F3 | | | | | |

Åpne punkter føres også i `.logs/<bruker>/issues.md` med lenke til dette dokumentet.

## 4. Oppsummering (SM-6)

| | |
|---|---|
| Antall deltakere | *(3–5)* |
| Datoer | |
| Påbegynt forsøk videreført på mobil | *(hvilke deltakere, enhet)* |
| Antall funn per alvorlighet | *(kritisk / alvorlig / mindre / kosmetisk)* |
| Rettet | *(antall, commits)* |
| Åpne punkter | *(antall, med begrunnelse i tabellen over)* |
| Konklusjon | *(er kjerneflyten forståelig uten hjelp, og hva er viktigst å rette)* |
