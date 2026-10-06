# Tilbakemelding på product brief

| | |
|---|---|
| **Gruppe** | G82 – G82-bull-knold-skjerven |
| **Product brief** | `_bmad-output/planning-artifacts/briefs/brief-G82-bull-knold-skjerven-2026-09-16/brief.md` (commit 22f88be) |
| **Tilbakemelding fra** | Faglærer i IBE160 (utarbeidet med KI-støtte) |
| **Dato** | 2026-10-06 |

## Samlet vurdering

- **Godt utgangspunkt med justeringer.** Gruppen kan gå videre og innarbeide punktene under.

**Det som er bra:**

1. Kjerneflyten er tydelig og avgrenset: logg inn → last opp notater → velg detaljnivå, vanskelighetsgrad og antall spørsmål → få sammendrag, begrepsliste og quiz med tre svaralternativer og fasit. Det er lett å se for seg skjermbildene.
2. Dere er ærlige om at dette ikke er teknisk unikt, og har bevisst valgt «en stram, velfungerende kjerneopplevelse fremfor mange halvferdige funksjoner». [ASSUMPTION]-markeringene og lista over åpne spørsmål viser at dere vet hva som må avklares.

**De viktigste endringene:**

1. Omfanget er lite for en gruppe på fire. Et prosjekt på nivå med forslag 8 kan bli ferdig raskt. Utvid v1 med noe som gir egen logikk og mer å teste, for eksempel at studenten tar quizen i appen, får poeng, og kan øve på nytt på spørsmålene hen svarte feil på, med historikk per opplastet notat.
2. Gjør suksesskriteriene testbare. «Fullt fungerende», «dekker kursets definerte data inn/ut» og «oppleves som representative» er ikke sjekkbare. Skriv for eksempel «en PDF på 10 sider gir en quiz med det valgte antall spørsmål, hver med nøyaktig tre alternativer og ett riktig svar».
3. Planlegg språkmodellen og kjørbarheten nå: hvilken modell, hvor nøkkelen ligger, og en testmodus med mock-svar, slik at sensor kan kjøre appen uten deres nøkkel. Fjern også henvisningen til `C:\IBE160\backend` på en lokal maskin. Den sier ingenting for andre som leser briefen.

## Vanskelighetsgrad og gjennomførbarhet

### Vurdert vanskelighetsgrad

- **Enkel**

**Sammenlignbart med:** 8) Foredragsnotater – sammendrag og quizgenerator (enkel). Briefen følger forslaget tett, med innlogging i tillegg.

**Begrunnelse:**

| Faktor | Nivå (lav / middels / høy) | Kommentar |
|---|---|---|
| Domenelogikk – hvor mange og hvor kompliserte regler og beregninger må stemme? | Lav | Lite egen logikk i dag. Regler for quizformat (tre alternativer, ett riktig) er det som finnes. Quizretting og ny øving på feil vil gi mer. |
| Datamodell – antall entiteter og relasjoner mellom dem | Lav–middels | Bruker, opplastet notat, preferanser, sammendrag, begreper og quizspørsmål. |
| Brukere, roller og innlogging | Middels | Innlogging er med, men mekanismen er ikke valgt. Feide/SSO er mye mer krevende enn enkel e-post og passord. |
| KI-funksjonalitet i appen, f.eks. kall til språkmodell, prompts i koden og håndtering av usikre svar | Middels | Tre typer generert innhold med strukturert utdata for quiz. Må håndtere svar som ikke følger formatet. |
| Integrasjoner og eksterne tjenester, f.eks. API-er, betaling og e-post | Middels | LLM-API med nøkkel og kostnad. Modell er ikke valgt. |
| Sanntid, samtidighet eller flere brukere som påvirker hverandre | Lav | Ingen. |
| Filhåndtering, f.eks. opplasting, PDF-lesing og eksport | Middels | PDF, tekst og Word må leses. Lysbildebaserte PDF-er gir ofte rotete tekst. |
| Sikkerhet og personvern | Lav–middels | Notater kan være kursbeskyttet. Innlogging skal beskytte dem, og innholdet sendes til en ekstern KI-tjeneste. |

**Hva vanskelighetsgraden betyr for dere:**

- _Enkel:_ Et enkelt prosjekt gir stor sjanse for å bli ferdig. Vanskelighetsgraden inngår likevel i vurderingen, så for å nå helt opp må dere vise mer i gjennomføringen. Det betyr særlig et gjennomarbeidet design, grundig testing, en tydelig dokumentert prosess og en README som virker. Med fire medlemmer bør dere i tillegg vurdere en tydelig utvidelse av kjerneflyten.

### Gjennomførbarhet med BMAD og Claude Code

Dere skal planlegge med BMAD (product brief → PRD → arkitektur → epics og stories) og implementere med Claude Code. Vurderingen under tar hensyn til at det må være tid til hele denne flyten, og til testing, retting og README til slutt.

| Spørsmål | Vurdering (OK / risiko / stor risiko) | Kommentar |
|---|---|---|
| **Tid og omfang** – kan v1 realistisk bli ferdig og stabil i løpet av semesteret, med tid til flere iterasjoner? | OK | Omfanget er godt innenfor rekkevidde. Risikoen er heller at det blir for lite å vise. Git-loggen viser foreløpig bare briefen og testskript, så PRD bør komme snart. |
| **BMAD-flyten** – er briefen konkret nok til at PRD, arkitektur og stories kan lages uten store hull, og blir det overkommelig mange stories? | OK | Flyten og funksjonene er konkrete. De åpne spørsmålene (modell, innlogging) er riktige å ta i arkitekturen. |
| **Egnet for Claude Code** – bruker løsningen en vanlig, godt dokumentert teknologistakk som Claude Code håndterer godt, eller krever den nisjeteknologi, spesialmaskinvare eller mye manuell konfigurasjon? | OK | Webapp med innlogging, filopplasting og LLM-API er godt dokumentert. Unngå Feide/SSO i v1. |
| **Kontroll på KI-ens arbeid** – kan gruppen selv avgjøre om koden gjør det riktige? Krever domenet kunnskap gruppen ikke har, f.eks. avanserte beregninger eller fagregler, så er det vanskelig å kvalitetssikre. | OK | Dere foreslår selv å validere sammendrag og quiz manuelt mot ekte forelesningsnotater. Gjør det med faste testdokumenter og dokumenter resultatet. |
| **Testbarhet** – finnes det tydelige regler og forventede resultater som tester kan skrives mot? | Risiko | Quizformatet kan testes, men suksesskriteriene i dag gir få testtilfeller. Quizretting og poeng gir tydelige regler. |
| **Kjørbar for sensor** – kan appen kjøres lokalt etter README, uten gruppens nøkler, betalte kontoer eller egen infrastruktur? | Stor risiko | Uten testmodus eller mock-svar kan ikke sensor prøve kjernefunksjonene. |
| **Avhengigheter og kostnader** – krever løsningen betalte API-er, f.eks. språkmodeller, og finnes det en plan for kostnad, testmodus eller mock-data? | Risiko | Modellvalg er utsatt, og kostnad og testmodus er ikke nevnt. |

**Konklusjon om gjennomførbarhet:**

- **Gjennomførbart med justert omfang.** Se forslagene under.

**Forslag til justering av omfang eller vanskelighetsgrad:**

1. Utvid v1 med interaktiv quiz med poeng, lagring av resultater og «øv på feil»-modus. Det gir egen logikk, mer å teste og bedre grunnlag for design.
2. Dropp Kurs-FAQ-chatboten (forslag 7) som strekkmål. Den er et helt eget, middels vanskelig produkt med kunnskapsbase og retrieval. Bruk heller ekstra tid på kvalitet, testing og utvidelsen over.

## Hvorfor product brief er viktig for mappen

Product brief er utgangspunktet for PRD, arkitektur, stories og til slutt koden. Del 1 av mappen vurderes blant annet på om sensor kan følge en sporbar vei fra plan til ferdig app. Den vurderes også på om appen gjør det dere har beskrevet, om den er testet, om den er godt designet, og om den kan kjøres etter README. Et uklart, for stort eller for lite brief gjør alt dette vanskeligere senere. Det er mye enklere å rette nå enn sent i semesteret.

## 1. Gjennomgang av briefens deler

| Del av brief | Status | Kommentar |
|---|---|---|
| Executive Summary – er det klart hva appen er, og hvilket problem den løser? | OK | Klart hva appen gjør og hvorfor aktiv repetisjon er bedre enn å lese på nytt. |
| The Problem – er problemet konkret, med reelle situasjoner og brukere? | OK | Godt forklart forskjellen mellom å ta imot og å repetere informasjon. |
| The Solution – beskriver løsningen brukeropplevelsen, ikke bare teknologi? | Juster | Fire tydelige steg. Beskriv også hva studenten gjør med quizen etterpå: tas den i appen, og får hen tilbakemelding? |
| What Makes This Different – er vurderingen ærlig og realistisk? | OK | Ærlig og realistisk om at verdien ligger i tilpasningen til studenthverdagen. |
| Who This Serves – er primærbrukerne tydelige, og vet vi hva de trenger? | OK | Primærbruker og suksess for brukeren («på under et minutt») er tydelig beskrevet. |
| Success Criteria – kan kriteriene faktisk sjekkes eller testes? | Endre | Kriteriene er generelle og viser til «kursets definerte data inn/ut». Legg til konkrete, sjekkbare kriterier per funksjon. |
| Scope – er det klart hva som er med i første versjon, og hva som ikke er det? | Juster | Tydelig inn/ut. Fjern avsnittet om `backend`-skjelettet i en lokal mappe, og bestem innloggingsmekanisme. |
| Vision – henger visjonen sammen med resten uten å blåse opp omfanget? | Juster | Chatboten er holdt utenfor v1, og det er riktig. Vurder å ta den helt ut av planene for dette semesteret. |

## 2. Utgangspunkt for del 1 av mappen

Punktene følger kriteriene i sensorveiledningen for del 1. Vektene i parentes viser hvor mye hvert kriterium teller i del 1.

| Kriterium i del 1 | Hva briefen bør legge til rette for | Status | Kommentar |
|---|---|---|---|
| **1. Prosess og KI-styring** (30 %) | Brief som er presis nok til at PRD og stories kan bygges direkte på den, slik at krav kan spores fra brief til kode. | OK | Briefen gir et godt grunnlag. Lukk [ASSUMPTION]-punktene og oppdater briefen, slik at historikken viser utviklingen. |
| **2. Funksjonalitet og omfang** (20 %) | Realistisk omfang for gruppen og semesteret: en tydelig kjerneflyt som kan bli ferdig og stabil, og nok innhold til å vise reell funksjonalitet. | Juster | Realistisk, men lite for fire personer. Utvid som foreslått over. |
| **3. Kvalitetssikring og testing** (15 %) | Suksesskriterier og funksjoner som er konkrete nok til å bli testtilfeller. | Juster | Quizformat og innlogging kan testes. Planlegg mock-svar og faste testdokumenter. |
| **4. Design og brukeropplevelse** (10 %) | Tydelige brukere og brukssituasjoner som designet kan bygges rundt, gjerne med de viktigste skjermbildene eller flytene skissert. | OK | Flyten i fire steg gjør det enkelt å skissere skjermbildene. Tenk på ventetid mens KI genererer. |
| **5. Kodekvalitet og arkitektur** (10 %) | Teknologivalg som er begrunnet og ikke mer komplekse enn appen trenger. | OK | Teknologivalg er riktig utsatt til arkitekturen. Hold det enkelt, og samle LLM-kall i én modul. |
| **6. README og kjørbarhet** (10 %) | Løsning som andre kan kjøre lokalt uten betalte kontoer, og uten tilgang til gruppens egne tjenester og nøkler. | Endre | Avhengig av LLM-nøkkel. Planlegg `.env.example`, testmodus, testbruker og et eksempeldokument. |
| **7. Ryddighet i repoet** (5 %) | En plan for hvor hemmeligheter, testdata og dokumentasjon skal ligge. | Juster | Det ligger et løst testskript (`hello.py`) i roten. Rydd bort slike filer, og planlegg hvor testdokumenter og nøkler (utenfor repoet) skal ligge. |

## 3. Neste steg for gruppen

1. Utvid v1 med interaktiv quiz med poeng og «øv på feil», og skriv testbare suksesskriterier for hver funksjon.
2. Velg språkmodell og enkel innlogging (e-post og passord), og beskriv testmodus med mock-svar.
3. Fjern lokale stier og avklarte [ASSUMPTION]-punkter fra briefen, og gå videre til PRD.

Oppdater product brief i repoet når dere har gjort endringene, slik at historikken viser hvordan planen utviklet seg. Det er en del av prosessen sensor ser etter.
