# Epic 6 Context: Klar for sensor

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->
<!-- Kompilert 26.11.2026, etter at Epic 1–5 er bygget (5.3 er til review, og 2.2 venter på mock-filene). -->

## Goal

Sensor skal kunne klone repoet, følge README-en alene, logge inn som en testbruker med ferdige data og kjøre hele kjerneflyten (notat → quiz → feilbank → lært) i testmodus uten API-nøkkel. Epicen har også sluttkontrollene som viser at appen holder kravene: at ingen ser andres data, at alle sider følger WCAG 2.2 A/AA og er KI-merket, at quizene fra ekte modell er gode nok og lages innen 120 sekunder, og en brukertest med medstudenter. 6.1–6.4 er kjerne, og 6.5 er «bør». Fristen er 15.12.2026 kl. 15:00.

## Stories

- Story 6.1: Testbruker med eksempeldata
- Story 6.2: README og test med ny klone
- Story 6.3: Sluttkontroll av tilgang og universell utforming
- Story 6.4: KI-kvalitet og genereringstid
- Story 6.5: Brukertest med medstudenter

## Requirements & Constraints

- **Testbruker:** e-post og passord står i README-en og på S1 i testmodus. Etter `seed_testdata` har testbrukeren emnet «Webutvikling» med minst tre notater fra `testdokumenter/`, quizer på minst to nivåer, leverte forsøk, en feilbank med minst ett lært og ett ikke lært spørsmål, og ett påbegynt forsøk.
- **Seed kan kjøres flere ganger:** finnes testbrukeren, slettes emnene hens og lages på nytt med samme resultat. Ingen nettverkskall. En test kjører kommandoen to ganger og teller hver ting.
- **README (SM-1):** kort om appen, hva som trengs (Python 3.14 og uv, eller pip), de fire oppstartsstegene, testbrukeren, at testmodus er på uten `.env` og hva banneret betyr, hvordan `.env.example` kopieres til `.env` med egen nøkkel og testmodus av, at `KI_MODELL` kan byttes, og hvordan `ALLOWED_HOSTS` utvides for mobil på samme nett (ikke hosting).
- **Test med ny klone:** en i gruppa som ikke skrev README-en, følger den ordrett på Windows og på macOS eller Linux, uten `.env`: logge inn som testbruker, laste opp et testdokument, ta quizen, levere, øve på feil og se dekningsgraden endre seg. Avvik rettes i README-en eller koden, og testen dokumenteres i sesjonsloggen.
- **Tilgang (SM-5):** hver URL med ID gir 404 med GET og POST som en annen bruker, og testen feiler når en ny URL med ID ikke er med. Utloggede sendes til Logg inn fra alle sider unntatt de offentlige. Merk: storyen sier «unntatt Logg inn og Registrer», men personvernerklæringen (S15) er også offentlig og må unntas.
- **Universell utforming (SM-7):** axe uten brudd på WCAG 2.2 A/AA på S1–S16 med S1b, S6b og S6c, i tilstandene tom, påbegynt, feil, generering, resultat og øving, dokumentert med dato og verktøyversjon. Manuell test av kjerneflyten med bare tastatur og med skjermleser (NVDA eller VoiceOver): synlig fokus, stegene på S8 og poengsummen leses som status, S1b holder fokus, feilmeldinger leses opp, og 320 px og 200 % tekst gir ingen vannrett rulling. Funn rettes eller føres som åpne punkter med begrunnelse.
- **KI-merking (SM-8):** S7, S9 og S12 har «Laget av KI» med modellnavnet fra quizen, også i testmodus.
- **KI-kvalitet (SM-2, SM-4):** de fem testdokumentene på alle tre nivåer mot ekte modell. Nøyaktig valgt antall, tre ulike alternativer, ett riktig og ingen like spørsmål. Spørsmålene er på notatets språk, og `Quiz.sprak` stemmer (`javascript-og-dom.txt` er engelsk). Minst 90 % er relevante, har riktig fasit og er ikke tvetydige etter manuell vurdering. Dokumenteres med modell, dato, `PROMPT_VERSJON` og eksempler på dårlige spørsmål.
- **Genereringstid:** 30 spørsmål fra tekst-PDF-en (`html-struktur-og-semantikk.pdf`) måles flere ganger. Typisk og lengste tid dokumenteres, og `effort` settes så genereringen holder seg godt under 120 s, ellers foreslås en PRD-endring. Valget hel PDF mot uttrukket tekst og Sonnet mot Haiku begrunnes. Raskere må ikke gå på bekostning av kvaliteten.
- **Brukertest (SM-6):** 3–5 medstudenter får oppgaver fra UJ-1 til UJ-3 uten hjelp. Gruppa noterer hvor de stopper, hva de misforstår og hva de sier, og minst én tar et påbegynt forsøk videre på mobil. Funnene dokumenteres med alvorlighet og rettes eller føres som åpne punkter.

## Technical Decisions

- **Seed (AD-21, AD-1):** `studier/management/commands/seed_testdata.py` kaller `ki.tving_testmodus()` først (den gjelder for resten av prosessen) og skriver aldri rett til modellene. Den bruker `last_opp` med filer fra `testdokumenter/`, `generering.generer_synkront(notat, vanskelighetsgrad, antall)` (gir `Quiz` eller hever `KIFeil`), `start_eller_fortsett_okt`, `lagre_svar` og `lever_okt` med faste svar, og `slett_emne` ved ny kjøring. Testbrukeren lages med `create_user`, emnet med `services.emner.opprett_emne`, og vilkårene godtas med `services.vilkar.godta_vilkar`, fordi `last_opp` avviser opplasting uten godtatte vilkår (AD-23). De tre siste står ikke i akseptansekriteriene, men er tjenester og følger AD-1.
- **Lært i seed:** et spørsmål blir lært etter to riktige svar på rad etter at det kom i feilbanken. Det samme spørsmålet trenger derfor et feilsvar i én levert økt og to riktige i senere leverte økter (nye forsøk eller øvingsøkter).
- **Mock-filene mangler:** `ki/mock/` er ikke committet før Magnus kjører `lag_mocksvar` (2.2). Til da feiler generering i testmodus med `api_feil`, og dermed også seed og et CI-steg med seed. Tester av seed kan patche `ki.generering.MOCK_MAPPE` med en midlertidig mock-mappe, slik `ki/tests_generering.py` gjør. Når `ki/mock/` committes, skal vakten med `skipTest` i `EkteMockfilerTest` fjernes. Mock-svarene er faste (de første N spørsmålene), så seed gir samme resultat hver gang.
- **Testbrukerens innlogging:** e-post og passord er ikke bestemt i planleggingen. S1 viser dem ikke ennå. Hent dem fra ett sted, så S1, README og seed ikke kan bli ulike.
- **README og oppstart (AD-22):** README-en har i dag bare gruppa og et avsnitt om testmodus og mock-svar. Stegene skal være nøyaktig `uv sync` (eller `pip install -r requirements.txt`), `python manage.py migrate`, `python manage.py seed_testdata`, `python manage.py runserver`, i README og kode.
- **CI:** `.github/workflows/test.yml` får `migrate` og `seed_testdata` på en tom database, så en ødelagt seed stopper merge.
- **Tilgangstesten (AD-8):** `studier/tests/test_tilgang.py` tester i dag bare `hent_egen` og `egne`, ikke URL-ene. Den nye testen går gjennom URL-mønstrene med `<int:pk>`, også `/okter/<id>/meld/<nr>/` (4.3) og `/jobber/<id>/steg/`, og kan bruke `studier/tests/fabrikk.py`. Offentlige sider er Logg inn, Registrer og S15.
- **axe og JavaScript:** repoet har ikke noe testoppsett for JavaScript. Utsatt arbeid foreslår Playwright sammen med axe-testen, og det vil også dekke `opplasting.js` (S6b, S6c) og `fremdrift.js` (S8). Kravet er at resultatet er dokumentert, ikke at testen er automatisk. S1b krever en bruker som ikke har godtatt vilkårene, og testbrukeren har godtatt dem.
- **KI (AD-11, AD-12):** `lag_mocksvar` kjører alle fem dokumentene på alle tre nivåene med 30 spørsmål mot ekte modell, og kan være grunnlaget for vurderingen i 6.4. Risiko: med `MAKS_TOKENS = 16000` kan 30 spørsmål bli avkuttet og gi `format`. 4.3 logger meldte spørsmål med spørsmål-ID, quiz-ID og modell, som kan brukes i 6.4. Bytte til uttrukket tekst eller annen modell endrer bare `ki.les_fil` eller `KI_MODELL`. Endres prompt, skjema eller `effort`, økes `PROMPT_VERSJON`, og mock-svarene lages på nytt hvis skjemaet er endret.

## UX & Interaction Patterns

- **Testmodus:** banneret «Testmodus: quizene bruker mock-svar, ingen KI kalles» på alle sider (finnes). S1 viser i tillegg testbrukerens e-post og passord. En quiz fra en fil som ikke er et testdokument, har merknaden om forhåndslagret testdokument på S7 og S9.
- **Testdataene skal fylle skjermbildene:** emnekort med stolpe og prosent og «Fortsett der du slapp» på S3, tallfliser på S4, og nivåfordeling, «Øv på feil (N)», quizkort med «Påbegynt – spørsmål X av Y» og historikk på S7.
- **Tone:** norsk bokmål, du-form, kort og saklig, uten utropstegn og emojier. Gjelder også README-en.

## Cross-Story Dependencies

- 6.1 bygger på tjenestene fra Epic 1–5 og trenger mock-filene fra 2.2 for å kjøre ende til ende.
- 6.2 trenger 6.1 (seed-steget i README og CI) og mock-filene for at CI-steget og testen med ny klone skal virke.
- 6.3 bruker testbrukerens data til tilstandene i axe-testen og bør kjøres når grensesnittet er ferdig. Nytt emne med filer (S16, UX-DR34) er skilt ut og ikke bygget, så axe på S16 dekker siden som den er.
- 6.4 krever en API-nøkkel og hører sammen med `lag_mocksvar` i 2.2. Endrer 6.4 prompt, skjema eller `effort`, må mock-svarene lages på nytt, og seed og testen med ny klone kjøres igjen.
- 6.5 bør komme etter 6.1–6.3 og bruker oppsettet for mobil på samme nett fra 6.2.
