# Epic 1 Context: Konto og emner

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->
<!-- Kompilert på nytt 23.11.2026 etter at Martins design ble felles UX. -->

## Goal

Studenten kan registrere seg, logge inn og ut, godta vilkårene ved første innlogging, opprette emner, gi dem nytt navn og slette dem, og ser bare sine egne data. Epicen legger også grunnmuren som resten av gruppa (tre personer som jobber parallelt) bygger på: et kjørbart Django-prosjekt med hele datamodellen migrert fra start, testmodus på som standard, eierhjelpere som alle senere views må bruke, CI på hver pull request, og en felles sidemal etter Martins design. Kjerne: FR-1–FR-4, FR-7 og FR-29 (`.env`-delen). Bør: nytt navn (FR-5) og sletting (FR-6).

## Stories

- Story 1.1: Prosjektskjelett med datamodell og CI (ferdig)
- Story 1.2: Registrere konto, logge inn og godta vilkårene (bygget 24.11)
- Story 1.3: Toppfelt, brødsmuler og felles sidemal
- Story 1.4: Opprette emne og se Oversikt
- Story 1.5: Gi emne nytt navn
- Story 1.6: Slette emne

## Requirements & Constraints

- **Registrering:** e-post og passord på minst 8 tegn. Ugyldig e-post, for kort passord og en e-post som er registrert fra før (uansett store og små bokstaver) gir feilmelding, og ingen konto lages. Den utfylte e-posten står igjen. Passord lagres bare som hash.
- **Innlogging:** feil passord og ukjent e-post gir samme melding, «Feil e-post eller passord.». Utlogging skjer med POST. Etter innlogging sendes brukeren til `next` hvis hen kom fra en annen side.
- **Offentlige sider:** bare Logg inn (forsiden), Registrer og Personvernerklæringen. Alle andre sider sender en utlogget bruker til innlogging.
- **Vilkår:** en innlogget bruker som ikke har godtatt vilkårene, kommer ikke videre før hen har bekreftet personvern-dialogen. Tidspunktet lagres på brukeren, og dialogen vises bare én gang. Opplasting avvises i tjenesten hvis vilkårene ikke er godtatt.
- **Bare egne data:** en annen brukers ID i URL eller skjema gir «Fant ikke siden» (404) uten å avsløre om dataene finnes.
- **Emne:** navnet kan ikke være tomt og må være unikt hos brukeren, uten å skille store og små bokstaver. To brukere kan ha samme navn. Ved nytt navn er notater, quizer og historikk uendret.
- **Sletting:** bare etter bekreftelse på egen side. Emnet slettes med alt innhold og filer. Det er den eneste måten å slette data på i v1.
- **Universell utforming (WCAG 2.2 A/AA)** er akseptansekriterier i hver story med grensesnitt: tastatur, synlig fokus, klikkflater på minst 44 px, synlige etiketter, feilmeldinger koblet til feltet og med fokus, `lang="nb"`, én `<h1>`, og 320 px og 200 % tekst uten vannrett rulling. Innlogging godtar innliming og passordbehandlere, med `autocomplete="email"` og `current-password`/`new-password`, uten kognitiv test.

## Technical Decisions

- **Stack:** Python 3.14, Django ≥ 5.2.19 < 6, uv, SQLite. Datamodellen er ferdig migrert i story 1.1, med `kontoer.Bruker` (e-post som brukernavn, `vilkar_godtatt` nullbart tidspunkt) og alle modellene i `studier`. Nye stories lager ikke nye migreringer for disse modellene.
- **Lag:** views → `studier.tilgang`/`studier.services` → modeller, og services → `ki`. `ki` importerer aldri fra `studier` eller `kontoer` (en test sjekker det). All domeneskriving, også `Bruker.vilkar_godtatt`, skjer i `studier/services/`. Bare `Emne` kan lagres rett fra skjema, med `eier` i konstruktøren, og skjemaet sjekker selv at navnet er unikt uten å skille store og små bokstaver.
- **Testmodus:** `ki.er_testmodus()` er eneste kilde, og malene får flagget fra en context processor. Testene kjører med testmodus tvunget på.
- **Tilgang:** `LoginRequiredMiddleware`, med `@login_not_required` bare på innlogging, registrering og personvernerklæringen. `hent_egen`/`egne` i `studier/tilgang.py` for alle ID-er fra URL, GET og POST. Veien til eieren står bare i `EIERVEI` der, og et rått pk-oppslag i views er forbudt. Andres data gir 404, og det testes for hver modell og hver ny URL med ID. Det finnes ingen URL-rute til `MEDIA_ROOT`.
- **Sletting (story 1.6):** `services.emner.slett_emne(emne)` samler filstiene, sletter emnet med notater, filer, quizer, økter, svar, feilbankrader og jobber med cascade i `transaction.atomic`, og sletter filene i `transaction.on_commit`. Filer som mangler, ignoreres. Ingen andre steder sletter `Notat`, `Quiz`, `Okt` eller `Feilbankrad`.
- **Vilkår (AD-23):** `VilkarMiddleware` etter `LoginRequiredMiddleware` sender en innlogget bruker med tom `vilkar_godtatt` til `/vilkar/` med `next`. Unntatt er `/vilkar/`, `/personvern/`, utlogging og statiske filer. POST på `/vilkar/` kaller `studier.services.vilkar.godta_vilkar(bruker)` og sender til `next`. `/vilkar/` er en vanlig side uten JavaScript, og JavaScript gjør den til en modal med fokusfelle.
- **URL-er og konvensjoner:** `/` (Oversikt), `/logg-inn/`, `/registrer/`, `/logg-ut/`, `/emner/ny/`, `/emner/<id>/`, `/emner/<id>/slett/`, `/vilkar/`, `/personvern/`. Heltalls-pk. POST/redirect/GET. HTMX-fragmenter ligger i `templates/<app>/_<navn>.html`, og CSRF-tokenet ligger i `hx-headers` på `<body>`. Feiltekster i `farequiz/feilmeldinger.py`. `<title>` følger formen «HTML-forelesning – Webutvikling – FåreQuiz».
- **CSS og JS (story 1.3):** Tailwind v4 frittstående CLI med `@theme` fra Martins DESIGN.md, bygget til `static/css/app.css`, som committes. htmx 2.0.11 som lokal fil. `favicon.svg` og `kart.svg` fra prototypen i `static/img/`.
- **CI:** ruff, `makemigrations --check` og `manage.py test` i testmodus ved PR mot `main` og push til `main`.

## UX & Interaction Patterns

- **Tokens:** varm palett (sand, krem og brunt), `accent-strong` #5C3A21 som hovedfarge, `error` #A34420 og `success` #3F624D bare til tilbakemelding. Systemfonter i `rem`, `content-max` 768 px, `tap-min` 44 px. Kort med lett skygge. Ingen mørk modus.
- **Toppfelt:** mørkt, med logoen (fåret i ballongen) og «FåreQuiz» til S3. Til høyre «‹ Tilbake» (lenke til forelderen, med `aria-label`, vises ikke på S3), «Meny» (`<details>` med Oversikt, Nytt emne og Personvernerklæring) og «Logg ut». De tre vises bare etter innlogging. Brødsmulesti under toppfeltet, og testmodus-banneret «Testmodus: quizene bruker mock-svar, ingen KI kalles» mellom dem. Fotlinje med opphavsrett og lenke til personvernerklæringen. «Hopp til innhold» først.
- **Forside (S1):** hero med «Registrer deg» og tre dekorative flashcards, tre informasjonskort, og innloggingsskjemaet under. I testmodus står testbrukerens e-post og passord her.
- **Personvern-dialog (S1b):** vises én gang etter første innlogging. Fire punkter (notater til Anthropic, ikke del personopplysninger, KI kan ta feil, vilkår og loggføring), lenke til personvernerklæringen og «Jeg har forstått og godtar». Esc lukker den ikke.
- **Oversikt (S3):** «Fortsett der du slapp» øverst (Epic 3), kortet «Nytt emne» først og emnekortene alfabetisk. Tom tilstand: «Ingen emner ennå. Opprett ditt første emne.» Ingen «Øv på feil»-kort.
- **Nytt emne (S16), Gi nytt navn (skjema på S4), Slett emne (S13):** feilmeldingene «Navnet kan ikke være tomt.» og «Du har allerede et emne med dette navnet.». Slettesiden sier nøyaktig hva som slettes, og «Avbryt» kommer før «Slett emnet og alt innhold».
- **Tone:** norsk bokmål, du-form, kort og saklig, uten utropstegn og emojier.

## Cross-Story Dependencies

- Story 1.1 er ferdig. 1.2–1.6 og `ki`-arbeidet i Epic 2 kan bygges parallelt.
- Story 1.2 lager sider før sidemalen i 1.3 finnes. Malene bør derfor arve en enkel `base.html` som 1.3 fyller med toppfelt, tokens og fotlinje.
- Story 1.2 sender til en enkel startside `/`, som story 1.4 gjør til Oversikt.
- Story 1.3 setter opp Tailwind, htmx, grunnmalen og 404-siden som 1.4–1.6 og alle senere grensesnitt bruker.
- Emnesiden fra 1.4 får «Gi nytt navn» (1.5), «Slett emne» (1.6) og «Last opp notat» (2.3).
- Opplastingen i story 2.3 forutsetter vilkårsregelen fra 1.2.
- `hent_egen`/`egne` og `slett_emne` brukes av alle senere epics. `seed_testdata` (Epic 6) bruker `slett_emne` for å kunne kjøres flere ganger.
