---
name: FåreQuiz
status: arkivert
created: 2026-11-15
updated: 2026-11-15
author: Christian
sources:
  - ../../briefs/brief-G82-bull-knold-skjerven-2026-09-16/brief.md
  - ../../prds/prd-G82-bull-knold-skjerven-2026-11-11/prd.md
  - ../../prds/prd-G82-bull-knold-skjerven-2026-11-11/addendum.md
---

# FåreQuiz – opplevelse og oppførsel

Christians individuelle UX-versjon, laget uavhengig av gruppeversjonen. Ordene fra PRD-ens ordliste (emne, notat, quiz, forsøk, feilbank, lært, dekket, dekningsgrad, historikk, testmodus) brukes med samme betydning her. Tokens i `{krøllparentes}` viser til [DESIGN.md](DESIGN.md).

Skissene i [mockups/](mockups/) viser nøkkelskjermene. Ved konflikt gjelder dette dokumentet og `DESIGN.md`, ikke skissene.

## Foundation

- **Flate:** Responsiv web, lik prioritet på pc og mobil. Samme sider og samme oppsett på begge, bare bredden endrer seg.
- **Teknikk:** Django-maler. Litt HTMX/JS til fremdriften under generering (FR-14) og lagring av svar underveis (FR-18), som i addendumet. Alt annet virker som vanlige lenker og skjemaer.
- **Visuell identitet:** [DESIGN.md](DESIGN.md).
- **Språk:** Grensesnittet er på norsk. Spørsmål og svar vises på notatets språk.
- **Ingen mørk modus i v1.**

## Information Architecture

| Skjerm | Nås fra | Formål | Skisse |
|---|---|---|---|
| **Logg inn** | Åpning av appen uten innlogging | E-post og passord. Lenke til Registrer. | – |
| **Registrer** | Logg inn | E-post og passord (minst 8 tegn). | – |
| **Mine emner** (startside) | Logg inn, logo, Tilbake fra Emneside | Emneliste med dekningsgrad. «Fortsett der du slapp» nederst. | [key-startside](mockups/key-startside.html) |
| **Nytt emne** | «+ Nytt emne» på startsiden og i menyen, «Opprett ditt første emne» | Ett felt for navn og knappen «Opprett». | – |
| **Emneside** | Mine emner, menyen | Emnets dekningsgrad, notatliste, «+ Last opp notat», «Gi emnet nytt navn», «Slett emne». | [key-emneside](mockups/key-emneside.html) |
| **Gi nytt navn** | Emneside | Samme skjema som Nytt emne, ferdig utfylt. | – |
| **Slett emne** | Emneside | Bekreftelsesside. | [key-emneside](mockups/key-emneside.html#slett) |
| **Last opp notat** | Emneside | Fil, vanskelighetsgrad, antall, KI-merknad, vilkår (første gang) og «Lag quiz» på én side. | [key-last-opp](mockups/key-last-opp.html) |
| **Notatside** | Emneside | Dekningsgrad med fordeling per nivå, feilbank, quizer, «Lag ny quiz», historikk, under hverandre. | [key-notatside](mockups/key-notatside.html) |
| **Quiz** | Notatside, Fortsett der du slapp, etter generering | Ett spørsmål per skjerm med Forrige/Neste og Lever på siste. | [key-quiz](mockups/key-quiz.html) |
| **Resultat** | Lever i Quiz | Poengsum, riktig/feil per spørsmål, «Øv på feil». | [key-resultat](mockups/key-resultat.html) |
| **Øv på feil** | Notatside, Resultat, Fortsett der du slapp | Samme oppsett som Quiz, oransje aksent. | [key-ov-pa-feil](mockups/key-ov-pa-feil.html) |
| **Øv-resultat** | Lever i Øv på feil | Poengsum, «Lært! ✓» med fasit, riktig/feil og telleren for resten. | [key-ov-pa-feil](mockups/key-ov-pa-feil.html) |

**Hierarki:** Mine emner → Emne → Notat → Quiz / Øv på feil → Resultat.

**Navigasjon:**
- **Topplinje** på alle sider etter innlogging: Tilbake (ikke på startsiden), logoen og menyknappen.
- **Tilbake** går alltid ett nivå opp i hierarkiet, ikke til forrige side i nettleseren. Emneside → Mine emner, Notatside og Last opp → emnet, Quiz, Resultat og Øv på feil → notatet. Da havner studenten et forutsigbart sted, også når hen kom inn via «Fortsett der du slapp». Nettleserens egen tilbakeknapp virker som vanlig.
- **Menyen** (menyknapp på både pc og mobil) har: *Mine emner* (alle emnene som lenker), *+ Nytt emne*, *Fortsett der du slapp* og *Logg ut*.
- **Brødsmuler** over overskriften viser hvor studenten er, for eksempel «Mine emner › Webutvikling › HTML».
- **Logoen** går til Mine emner.

## Voice and Tone

Kort, vennlig og direkte. Du-form. Appen snakker som en medstudent som hjelper til, ikke som et system.

| Gjør | Ikke gjør |
|---|---|
| «Lager quiz, håper du er klar!» | «Vennligst vent mens forespørselen behandles.» |
| «7 av 10» – «riktige svar» | «Din score: 70 %» |
| «3 spørsmål er lagt i feilbanken. Øv på dem til du kan dem.» | «Du hadde 3 feil.» |
| «Lært! ✓» | «Gratulerer!!! 🎉🎉» |
| «Du har ikke svart på alle spørsmålene. Disse mangler: spørsmål 4, spørsmål 7.» | «Feil: skjemaet er ugyldig.» |
| «Bare PDF, DOCX og TXT på maks 5 MB kan lastes opp.» | «Ugyldig filtype.» |
| «Slette «Webutvikling»? Dette sletter 4 notater og alle quizene …» | «Er du sikker?» uten å si hva som slettes. |
| Knapper sier hva som skjer: «Lag quiz», «Lever», «Øv på feil», «Prøv igjen». | «OK», «Send», «Fortsett» når noe annet er ment. |

## Component Patterns

Oppførsel. Utseendet står i `DESIGN.md` under Components.

| Komponent | Brukes på | Regler |
|---|---|---|
| **Topplinje** | Alle sider etter innlogging | Fast øverst i dokumentflyten (ikke klistret). Tilbake vises på alle sider unntatt Mine emner. |
| **Tilbake-knapp** | Alle sider unntatt startsiden | Vanlig lenke til forelderen i hierarkiet. `aria-label` sier hvor: «Tilbake til HTML». |
| **Menyknapp og menypanel** | Topplinje | Åpnes og lukkes med klikk, Enter eller mellomrom. Esc lukker og setter fokus tilbake på knappen. Klikk utenfor lukker. Virker uten JS (`<details>`). |
| **Listerad** | Mine emner, Emneside, Fortsett der du slapp, Notatside | Hele raden er én lenke. Emner sorteres alfabetisk. Notater sorteres alfabetisk. Quizer og historikk sorteres med nyeste øverst. |
| **Dekningsstolpe og dekningskort** | Mine emner, Emneside, Notatside | Viser alltid prosenttall. Emne uten notater viser «Ingen dekningsgrad» i stedet. Nivå uten quiz viser «Ingen quiz» (teller som 0 %, FR-24). |
| **Fortsett-boks** | Mine emner | Viser alle påbegynte forsøk og alle påbegynte øvingsøkter, nyeste først. Hver rad lenker rett til spørsmålet studenten kom til. Finnes det ingen, vises ikke boksen i det hele tatt. |
| **Valgknapper (nivå)** | Last opp, Notatside | Radioknapper. Middels er valgt på forhånd (FR-11). |
| **Antall spørsmål** | Last opp, Notatside | Tallfelt, 5–30, standard 10. Verdi utenfor gir feilmelding ved feltet. |
| **Filvelger** | Last opp | Vanlig `<input type=file>`, ingen dra-og-slipp (2.5.7). Sjekker format og størrelse før opplasting når det går, og alltid på serveren. |
| **Vilkårsboks** | Last opp | Vises bare til studenten har godtatt én gang (FR-7). Må være krysset av før «Lag quiz» virker. Mangler krysset, vises feilmelding ved boksen. |
| **«Lag quiz»-knapp** | Last opp, Notatside | Låses fra den trykkes til genereringen er ferdig eller feilet (FR-14). Ved suksess åpnes Quiz på spørsmål 1. |
| **Ventepanel** | Last opp, Notatside | Erstatter skjemaet mens quizen lages. Overskriften står fast. Steglinjen oppdateres: «Steg 1 av 3: Leser filen» → «Steg 2 av 3: Lager spørsmål» → «Steg 3 av 3: Sjekker quizen». |
| **Quizfremdrift** | Quiz, Øv på feil | «Spørsmål N av M» og stolpe. KI-merket står alltid ved siden av. |
| **Spørsmålsboks og svaralternativer** | Quiz, Øv på feil | Spørsmålet er `<legend>` for en gruppe med tre radioknapper. Hele alternativboksen er klikkbar (`<label>`). Studenten kan endre svar fritt før levering. |
| **Forrige / Neste / Lever** | Quiz, Øv på feil | Neste og Forrige lagrer svaret og går videre. Det går an å gå videre uten å svare. På siste spørsmål er Neste byttet ut med Lever. |
| **KI-merke** | Notatside (hver quiz), Quiz, Øv på feil | Står alltid på disse stedene (NFR-9). Sier modellnavnet fra quizen (NFR-7) og «kan inneholde feil». Vises også i testmodus. |
| **Påbegynt-merkelapp** | Notatside, Fortsett-boks | «Påbegynt 5/10». Knappen ved siden av heter «Fortsett» i stedet for «Ta på nytt». |
| **Feilbank-rad** | Notatside | «N spørsmål å øve på» og knappen «Øv på feil». Tom feilbank gir låst knapp og teksten «Ingen feil å øve på» (FR-22). |
| **Historikktabell** | Notatside | Alle leverte forsøk, nyeste øverst (FR-26). Øvingsøkter vises ikke (FR-22). |
| **Resultatrad** | Resultat, Øv-resultat | «✓ Riktig» eller «✗ Feil» og spørsmålsnummer. Ingen fasit for feil svar (FR-19). |
| **Lært-boks** | Øv-resultat | Vises for hvert spørsmål som ble lært i økten, øverst i listen. Viser spørsmålet og fasiten (FR-23). |
| **Feilmelding** | Alle skjemaer, Quiz | Står ved feltet eller knappen den gjelder. Får fokus eller leses opp med `role="alert"`. Lenker i meldingen hopper rett til feltet eller spørsmålet. |
| **Bekreftelsesside** | Slett emne | Egen side, ikke popup. Sier hva som slettes og antall notater. «Avbryt» er like lett å nå som «Ja, slett emnet». |

## State Patterns

| Tilstand | Skjerm | Visning |
|---|---|---|
| **Ny bruker uten emner** | Mine emner | Velkomstkort: «Velkommen til FåreQuiz», én setning om hva appen gjør og den store knappen «Opprett ditt første emne». |
| **Ingen påbegynte** | Mine emner | Fortsett-boksen vises ikke. |
| **Emne uten notater** | Emneside | «Ingen notater ennå» og knappen «+ Last opp notat». Ingen dekningsgrad. |
| **Første opplasting** | Last opp | Vilkårsboksen vises. |
| **Avvist fil** | Last opp | Feilmelding ved filfeltet: for stor fil oppgir grensen på 5 MB, feil format oppgir PDF, DOCX og TXT (FR-8). |
| **Quizen lages** | Last opp, Notatside | Ventepanel med steg. «Lag quiz» låst. |
| **Timeout (120 s)** | Last opp, Notatside | «Det tok for lang tid å lage quizen. Filen er lagret, så du trenger ikke laste den opp på nytt.» og knappen «Prøv igjen» med samme valg (FR-15). |
| **Feil format fra KI to ganger** | Last opp, Notatside | «Vi klarte ikke å lage en gyldig quiz. Prøv igjen, eller velg færre spørsmål.» Ingen quiz lagres (FR-13). |
| **Påbegynt forsøk** | Notatside, Quiz | Påbegynt-merkelapp. Quiz åpner på spørsmålet studenten kom til, med tidligere svar valgt. |
| **Manglende svar ved levering** | Quiz, Øv på feil | Feilmelding ved Lever med lenker til spørsmålene som mangler (FR-17). Ingenting leveres. |
| **Lagring feiler** | Quiz, Øv på feil | «Svaret ble ikke lagret. Sjekk nettet og prøv igjen.» ved knappen. Studenten blir på samme spørsmål. **[ASSUMPTION]** |
| **Tom feilbank** | Notatside | Låst «Øv på feil» og «Ingen feil å øve på». |
| **Spørsmål lært** | Øv-resultat | Lært-boks med fasit. |
| **Alle feil lært** | Øv-resultat | «Feilbanken er tom. Godt jobba!» og «Tilbake til HTML». **[ASSUMPTION]** |
| **Testmodus** | Alle sider | Smal stripe øverst: «Testmodus – quizene er forhåndslagret og laget av KI tidligere.» **[ASSUMPTION]** |
| **Ukjent fil i testmodus** | Notatside, Quiz | Merknad: «Testmodus: denne quizen er laget fra et forhåndslagret testdokument, ikke fra filen din.» (FR-27). **[ASSUMPTION om ordlyd]** |
| **Ikke funnet** | Alle sider med ID | «Fant ikke siden» og lenke til Mine emner. Sier ikke om dataene finnes hos noen andre (FR-3). |
| **Ikke innlogget** | Alle sider unntatt Logg inn og Registrer | Sendes til Logg inn (FR-2). |
| **Feil innlogging** | Logg inn | «Feil e-post eller passord.» Samme melding for begge (FR-2). |

## Interaction Primitives

- **Klikk og trykk** er hovedmåten å bruke appen på. Alle handlinger er knapper eller lenker med tekst.
- **Tastatur:** Tab følger leserekkefølgen. Piltastene flytter mellom svaralternativene (vanlig radiogruppe). Enter på Neste går videre. Esc lukker menyen.
- **Ingen hurtigtaster**, ingen dra-og-slipp, ingen sveiping og ingen funksjoner som bare finnes ved hover.
- **Lagring underveis:** Svaret lagres hver gang studenten trykker Neste, Forrige eller Lever (FR-18). Det trengs ingen egen lagreknapp.
- **Ingen popup-vinduer.** Bekreftelser og vilkår er egne sider eller en del av siden.

## Accessibility Floor

WCAG 2.2 A og AA på alle sider (NFR-8). Kontrast står i `DESIGN.md`.

| Krav | Slik oppfylles det |
|---|---|
| Bare tastatur (2.1.1) | Hele kjerneflyten er vanlige lenker, knapper, radioknapper og skjemaer. Menyen er `<details>`. |
| Synlig fokus (2.4.7, 2.4.11) | Fokusring på 3 px i `{colors.primary}` (oransje i Øv på feil) med 2 px avstand. Topplinjen er ikke klistret, så ingenting dekker fokus. |
| Klikkflater (2.5.8) | Minst 44 px, svaralternativer 56 px. |
| Ikke bare farge (1.4.1) | ✓/✗ og tekst på riktig og feil. Prosenttall ved alle stolper. Påbegynt har tekst. |
| Skjermleser og statusmeldinger (4.1.3) | Steglinjen i ventepanelet har `role="status"` og `aria-live="polite"`. Poengsummen på Resultat har `role="status"`. Feilmeldinger har `role="alert"`. |
| Skjema og feil (3.3.1, 3.3.2) | Alle felt har synlig etikett. Hjelpetekst er koblet med `aria-describedby`. Feil står ved feltet. |
| Innlogging (3.3.8) | Vanlige felt med `autocomplete="email"` og `current-password`/`new-password`. Innliming og passordbehandlere virker. Ingen kognitiv test. |
| Språk (3.1.1, 3.1.2) | `lang="no"` på alle sider. Spørsmål og alternativer får `lang` fra notatets språk når det ikke er norsk. |
| Overskrifter og landemerker (1.3.1, 2.4.6) | Én `<h1>` per side. `<header>`, `<nav aria-label="Hovedmeny">` og `<main>`. |
| Forstørrelse og bredde (1.4.4, 1.4.10) | 200 % tekst og 320 px bredde uten vannrett rulling. |
| Ingen dra-og-slipp (2.5.7) | Opplasting med vanlig filvelger. |
| Sidetittel (2.4.2) | `<title>` sier side og sted, for eksempel «Spørsmål 3 av 10 – HTML – FåreQuiz». |

## Responsive & Platform

| Bredde | Oppførsel |
|---|---|
| Over 760 px | Innholdet er sentrert i en 760 px bred kolonne med luft på sidene. |
| 400–760 px | Kolonnen fyller bredden med 16 px marg. Knapper i en rad brytes til ny linje ved behov. |
| Under 480 px | Overskrifter og store tall blir litt mindre. |
| Under 400 px | Logoen skjules i topplinjen. Tilbake og Meny står igjen. |
| 320 px | Laveste bredde. Ingen vannrett rulling (NFR-1, 1.4.10). |

Det er ingen egen mobilversjon. Alt studenten kan gjøre på pc, kan hen gjøre på mobil, og omvendt.

## KI-merking (AI Act)

Gjelder NFR-9. KI-merket «Laget av KI (Claude Sonnet 5.5) · kan inneholde feil» står:
- ved hver quiz på Notatside
- over spørsmålet på hver skjerm i Quiz
- over spørsmålet på hver skjerm i Øv på feil

I tillegg står KI-tjenesten nevnt i merknaden på Last opp og i vilkårene. Merket vises også i testmodus. Modellnavnet hentes fra quizen (NFR-7), ikke fra gjeldende konfigurasjon.

## Key Flows

Reisene er de samme som i PRD-en (UJ-1 til UJ-5) og følger Tore og sensor gjennom skjermene.

### UJ-1. Tore tester seg selv på en forelesning for første gang

1. Tore registrerer seg på **Registrer** og havner på **Mine emner**. Han ser velkomstkortet og trykker «Opprett ditt første emne».
2. På **Nytt emne** skriver han «Webutvikling» og trykker «Opprett». Han havner på **Emneside**, som viser «Ingen notater ennå».
3. Han trykker «+ Last opp notat». På **Last opp notat** velger han PDF-en om HTML. Middels og 10 er valgt på forhånd. Han leser KI-merknaden, krysser av for «Jeg godtar vilkårene» og trykker «Lag quiz».
4. Skjemaet byttes ut med ventepanelet: «Lager quiz, håper du er klar!» Steglinjen går fra «Leser filen» til «Lager spørsmål» til «Sjekker quizen». Knappen er låst.
5. **Quiz** åpner på spørsmål 1 av 10. Han huker av og trykker Neste ti ganger. På spørsmål 10 trykker han Lever.
6. **Klimaks:** **Resultat** viser **7 av 10** i stort. Under ser han hvilke tre som var feil, uten fasit, og «3 spørsmål er lagt i feilbanken».

**Feilvei:** Har han glemt et spørsmål, får han en melding ved Lever med lenke rett til det.

### UJ-2. Tore lager quizer for resten av forelesningene og følger progresjonen

1. Tore laster opp CSS, JavaScript og UX-design på **Last opp notat**. Vilkårene vises ikke lenger.
2. På **Notatside** for HTML bruker han «Lag ny quiz» til å lage en lett og en vanskelig quiz, uten å laste opp på nytt.
3. **Emneside** viser dekningsgraden for hvert notat og 48 % for hele emnet. På **Notatside** ser han fordelingen per nivå og historikken med dato og poengsum.
4. Kvelden før eksamen åpner han appen på mobilen, går til HTML og trykker den oransje «Øv på feil». Skjermen blir oransje, og han kjenner igjen spørsmålene med alternativene i ny rekkefølge.
5. Han svarer på alle og leverer.
6. **Klimaks:** **Øv-resultat** viser «Lært! ✓» og fasiten for spørsmålet han nå har svart riktig på to ganger på rad. Det er tatt ut av feilbanken.

### UJ-3. Tore blir avbrutt midt i en quiz

1. Tore er på spørsmål 5 av 10 og lukker fanen.
2. Senere åpner han appen på mobilen. Nederst på **Mine emner** står «Fortsett der du slapp» med «Webutvikling › HTML · Middels · 5 av 10 besvart».
3. **Klimaks:** Han trykker på raden og havner rett på spørsmål 6, med de fem første svarene lagret. Han svarer og leverer.

**Feilvei:** Hvis genereringen får timeout, ser Tore «Det tok for lang tid å lage quizen» og «Prøv igjen». Filen er lagret, så han slipper å laste den opp på nytt.

### UJ-4. Tore laster opp en fil appen ikke kan lese

1. På **Last opp notat** velger Tore et opptak som MP4 og trykker «Lag quiz».
2. **Klimaks:** En feilmelding ved filfeltet sier at bare PDF, DOCX og TXT på maks 5 MB kan lastes opp. Valgene hans står igjen, så han kan velge en annen fil med en gang.

### UJ-5. Sensor kjører appen uten API-nøkkel

1. Sensor følger README-en og åpner appen. Testmodus-stripen vises øverst på alle sider.
2. Sensor logger inn som testbrukeren på **Logg inn**. **Mine emner** viser et emne med dekningsgrad, og nederst «Fortsett der du slapp».
3. På **Emneside** og **Notatside** ser sensor dekningsgrad, fordeling per nivå, quizer med KI-merke og historikk.
4. Sensor laster opp et testdokument. Ventepanelet vises, og **Quiz** åpner med spørsmål fra mock-svarene.
5. Sensor tar quizen, leverer og trykker «Øv på feil».
6. **Klimaks:** Tilbake på **Notatside** ser sensor at dekningsgraden har endret seg. Hele flyten virker uten nøkkel.

## Åpne punkter

Antakelser som ikke er avklart med gruppa. Ingen av dem blokkerer arkitektur eller stories.

1. **[ASSUMPTION]** Etter generering åpnes Quiz direkte på spørsmål 1, ikke Notatside.
2. **[ASSUMPTION]** Logg inn, Registrer, Nytt emne og Gi nytt navn er enkle skjemaer uten egne skisser.
3. **[ASSUMPTION]** Testmodus vises som en stripe øverst på alle sider. Ordlyden er ikke bestemt.
4. **[ASSUMPTION]** Meldingen når lagring feiler, og meldingen når feilbanken er tom etter øving.
5. **Viktig for arkitekturen:** CSS-rammeverk er ikke valgt i denne versjonen. Tokens i `DESIGN.md` kan brukes med vanlig CSS eller Tailwind.
