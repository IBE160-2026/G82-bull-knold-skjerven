# Epic 1 Context: Konto og emner

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Studenten kan registrere seg, logge inn og ut, opprette emner, gi dem nytt navn og slette dem, og ser bare sine egne data. Epicen legger også grunnmuren som resten av gruppa (tre personer som jobber parallelt) bygger på. Det er et kjørbart Django-prosjekt med hele datamodellen migrert fra start, testmodus på som standard, eierhjelpere som alle senere views må bruke, og CI på hver pull request. I tillegg kommer felles sidemal med Tailwind-tokens, meny og 404-side. Kjerne: FR-1–FR-4 og FR-29 (`.env`-delen). Bør: nytt navn (FR-5) og sletting (FR-6).

## Stories

- Story 1.1: Prosjektskjelett med datamodell og CI
- Story 1.2: Registrere konto og logge inn og ut
- Story 1.3: Topplinje, meny og felles sidemal
- Story 1.4: Opprette emne og se Mine emner
- Story 1.5: Gi emne nytt navn
- Story 1.6: Slette emne

## Requirements & Constraints

- **Registrering:** e-post og passord på minst 8 tegn. Ugyldig e-post, for kort passord og en e-post som er registrert fra før (uansett store og små bokstaver) gir feilmelding ved feltet, og ingen konto lages. Den utfylte e-posten står igjen. Passord lagres bare som hash.
- **Innlogging:** feil passord og ukjent e-post gir samme melding, «Feil e-post eller passord.». Utlogging skjer med POST. Alle sider unntatt Logg inn og Registrer sender ikke-innloggede til Logg inn.
- **Bare egne data:** en annen brukers ID i URL eller skjema gir «Fant ikke siden» (404) uten å avsløre om dataene finnes. Gjelder alle sider og alle handlinger som endrer data, og skal testes for hver modell.
- **Emne:** navnet kan ikke være tomt og må være unikt hos brukeren, uten å skille store og små bokstaver. To brukere kan ha samme navn. Ved nytt navn godtas samme navn med andre store og små bokstaver på samme emne, og notater, quizer og historikk er uendret.
- **Sletting:** bare etter bekreftelse. Emnet slettes med alle notater, filer, quizer, økter, svar, feilbankrader og jobber. Andre emner påvirkes ikke. Dette er den eneste måten å slette data på i v1.
- **Kjøring:** en ny klone uten `.env` skal starte med `uv sync`, `python manage.py migrate` og `python manage.py runserver`. Da er `DEBUG=True`, `SECRET_KEY` en fast utviklingsnøkkel merket usikker, `ALLOWED_HOSTS=localhost,127.0.0.1` og testmodus på. Ingen database-server og ingen betalte tjenester.
- **Universell utforming (WCAG 2.2 A/AA)** er akseptansekriterier i hver story med grensesnitt. Det gjelder tastatur, synlig fokus, klikkflater på minst 44 px, synlige etiketter, feilmeldinger ved feltet med `role="alert"` eller fokus, `lang="nb"`, én `<h1>`, og 320 px og 200 % tekst uten vannrett rulling. Innlogging skal godta innliming og passordbehandlere og ha `autocomplete="email"` og `current-password`/`new-password`, uten kognitiv test.

## Technical Decisions

- **Stack:** Python 3.14, Django ≥ 5.2.19 < 6, uv ≥ 0.13 (`pyproject.toml`, `uv.lock`, og `requirements.txt` fra `uv export --no-hashes`), `anthropic` ≥ 2.8 < 3, `python-docx` 1.2.0, `python-dotenv` 1.2.4 og SQLite. Prosjektet settes opp med `django-admin startproject`, uten startmal.
- **Struktur:** appene `farequiz` (settings, urls, `feilmeldinger.py`), `kontoer`, `studier` (`models.py`, `services/`, `tilgang.py`) og `ki`. Avhengigheter går bare nedover: views → `studier.tilgang`/`studier.services` → modeller, og services → `ki`. `ki` importerer aldri fra `studier` eller `kontoer`.
- **Brukermodell:** `kontoer.Bruker` arver `AbstractUser` med `username = None`, unik `email` som `USERNAME_FIELD`, `REQUIRED_FIELDS = []` og `vilkar_godtatt` (nullbart tidspunkt). `BrukerManager.create_user(email, password)` lagrer e-posten med små bokstaver. `AUTH_USER_MODEL = "kontoer.Bruker"` settes før første `migrate`.
- **Hele datamodellen lages og migreres i story 1.1**, slik at de andre storyene slipper migreringskonflikter. Faste verdier er `TextChoices`, og migreringene committes.
  - `Emne`: `eier`, navn.
  - `Notat`: `emne`, `fil` (`notater/<eier-id>/<uuid4><endelse>`), `originalnavn`, `filtype` ∈ {`pdf`, `docx`, `txt`}, `storrelse`.
  - `Genereringsjobb`: `notat`, `vanskelighetsgrad`, `antall`, `startet`, `status` (`leser`/`lager`/`sjekker`/`ferdig`/`feilet`), `runde`, `i_gang`, `feilkode`, `raatt_svar`, `forhandslagret`, `modell`, `prompt_versjon`.
  - `Quiz`: `notat`, `jobb` (`OneToOneField`), `vanskelighetsgrad` ∈ {`lett`, `middels`, `vanskelig`}, `sprak`, `modell`, `prompt_versjon`, `forhandslagret`.
  - `Sporsmal`: `quiz`, `tekst`, `begrunnelse`, og det nullbare `meldt_tidspunkt`. Feltet brukes først i story 4.3, men lages nå.
  - `Alternativ`: `sporsmal`, `tekst`, `er_riktig`.
  - `Okt`: `notat` (alltid satt), `quiz` (satt hvis og bare hvis `type=forsok`, med `CheckConstraint`), `type` ∈ {`forsok`, `oving`}, `status` ∈ {`pabegynt`, `levert`}, `opprettet`, `sist_endret`, `levert_tidspunkt`, `poengsum`, `antall` og `innhold` (`JSONField`). Betinget `UniqueConstraint` gir høyst én påbegynt `forsok` per quiz og høyst én påbegynt `oving` per notat.
  - `Svar`: `okt`, `sporsmal`, `alternativ`, `hendelse` ∈ {`lagt_i`, `nullstilt`, `opp`, `laert`, `ingen`}, med `UniqueConstraint(okt, sporsmal)`.
  - `Feilbankrad`: unik `sporsmal`, teller for riktige svar på rad, `laert_tidspunkt` og tidspunkt for opprettelse. Rader slettes aldri utenom emnesletting.
  - Feilkoder: `timeout`, `format`, `for_lite_innhold`, `for_stor`, `api_nokkel`, `api_feil`.
- **Innstillinger:** `ATOMIC_REQUESTS` av. SQLite med `OPTIONS = {"transaction_mode": "IMMEDIATE", "timeout": 20}`, `USE_TZ=True` og `TIME_ZONE="Europe/Oslo"`. `settings.py` leser `.env`. `.env.example` har `ANTHROPIC_API_KEY`, `KI_MODELL=claude-sonnet-5-5`, `TESTMODUS`, `SECRET_KEY`, `DEBUG` og `ALLOWED_HOSTS` uten ekte verdier. `.env`, `db.sqlite3` og `media/` står i `.gitignore`. `.gitattributes` har `testdokumenter/** binary` og `ki/mock/** -text`.
- **Testmodus:** `ki.er_testmodus()` er eneste kilde. Den er sann når `TESTMODUS` er `1`/`true`/`yes`/`on`, eller når `ANTHROPIC_API_KEY` mangler. `ki.tving_testmodus()` brukes i tester. Malene får flagget fra en context processor.
- **Tilgang:** `LoginRequiredMiddleware`, med `@login_not_required` bare på innlogging og registrering. `studier/tilgang.py` har `hent_egen(modell, pk, bruker)` (`Http404` for andres data) og `egne(modell, bruker)`. Veien til eieren står bare her, for eksempel `notat__emne__eier` for `Okt` og `okt__notat__emne__eier` for `Svar`. Alle ID-er fra URL, GET og POST går gjennom hjelperne, og et rått pk-oppslag i views er forbudt. Det finnes ingen URL-rute til `MEDIA_ROOT`.
- **Skrivinger:** bare `Emne` kan lagres rett fra skjema. Skjemaet får `eier` i konstruktøren og sjekker selv at navnet er unikt uten å skille store og små bokstaver. All annen domeneskriving skjer i `studier/services/`.
- **Sletting:** `services.emner.slett_emne(emne)` samler filstiene, sletter med cascade i `transaction.atomic` og sletter filene i `transaction.on_commit`. Filer som mangler, ignoreres. Ingen andre steder sletter `Notat`, `Quiz`, `Okt` eller `Feilbankrad`.
- **Konvensjoner:** norske identifikatorer uten æ/ø/å. URL-er bruker heltalls-pk, for eksempel `/emner/<id>/`. POST/redirect/GET. HTMX-fragmenter ligger i `templates/<app>/_<navn>.html`, og CSRF-tokenet ligger i `hx-headers` på `<body>`. Feiltekster står i `farequiz/feilmeldinger.py`.
- **CSS og JS (story 1.3):** Tailwind v4 frittstående CLI (4.3.x). `static/src/app.css` med `@theme` bygges med `tailwindcss -i static/src/app.css -o static/css/app.css --minify`, og resultatet committes. htmx 2.0.11 ligger som `static/js/htmx.min.js`, aldri via CDN.
- **CI og tester:** `.github/workflows/test.yml` kjører `ruff check`, `ruff format --check` og `python manage.py test` uten nøkkel og med testmodus på, på hver pull request mot `main`. Rød CI merges ikke.

## UX & Interaction Patterns

- **Tokens:** tema «Frisk grønn» med `primary` #047857 og practice-familien (oransje, bare i «Øv på feil»). Systemfonter, alle størrelser i `rem`, radius 4/8/10/full, avstander 4–48 px, `content-max` 760 px, `gutter` 16 px, `target-min` 44 px. Flatt uttrykk uten skygger utenom menypanelet, og ingen mørk modus.
- **Grunnmal etter innlogging:** topplinje som ikke er klistret, med Tilbake, logoen «FåreQuiz» (lenke til Mine emner) og «☰ Meny». Brødsmuler over `<h1>`, landemerkene `<header>`, `<nav aria-label="Hovedmeny">` og `<main>`, og `<title>` på formen «Side – sted – FåreQuiz». Logg inn og Registrer har `<title>` som «Logg inn – FåreQuiz».
- **Tilbake:** vanlig lenke ett nivå opp i hierarkiet (Emneside → Mine emner), med `aria-label` som sier hvor. Den vises ikke på Mine emner.
- **Meny:** `<details>` som virker uten JS. Esc lukker og setter fokus tilbake på knappen, og klikk utenfor lukker. Panelet er 260 px bredt. Innhold: *Mine emner* (alle emnene som lenker), *+ Nytt emne*, *Fortsett der du slapp* (kommer i Epic 3) og *Logg ut* (POST).
- **Knapper:** primær (grønn), sekundær (grønn kant), øve (oransje), fare (rød, bare «Ja, slett emnet») og låst (grå). Ett fylt hovedvalg per skjerm. Fokusring på 3 px i primærfargen med 2 px avstand.
- **Testmodus-stripe** øverst på alle sider: «Testmodus – quizene er forhåndslagret og laget av KI tidligere.»
- **Mine emner:** egne emner sortert alfabetisk som listerader der hele raden er én lenke, med plass til dekningsgrad. Ny bruker ser velkomstkortet «Velkommen til FåreQuiz», én setning om appen og knappen «Opprett ditt første emne». Emneside uten notater viser «Ingen notater ennå».
- **Nytt emne / Gi nytt navn:** samme enkle skjema, ett felt og «Opprett». Ved nytt navn er feltet utfylt med dagens navn.
- **Slett emne:** egen bekreftelsesside, ikke popup: «Slette «<navn>»? Dette sletter N notater og alle quizene …». «Avbryt» skal være like lett å nå som «Ja, slett emnet».
- **Responsivt:** under 480 px blir overskriftene mindre, og under 400 px skjules logoen.
- **Tone:** kort, vennlig, du-form. Knappetekster sier hva som skjer.

## Cross-Story Dependencies

- Story 1.1 blokkerer alt. Når den er ferdig, kan 1.2–1.6 og `ki`-arbeidet i Epic 2 (story 2.1 og 2.2) bygges parallelt.
- Story 1.2 sender til en enkel startside `/`, som story 1.4 gjør til Mine emner.
- Story 1.3 setter opp Tailwind, htmx, grunnmalen og 404-siden som 1.4–1.6 og alle senere grensesnitt bruker. Menypunktene legges til av storyene som lager sidene.
- Emnesiden fra 1.4 får knappene «Gi emnet nytt navn» (1.5), «Slett emne» (1.6) og «+ Last opp notat» (story 2.3).
- Testene for 1.6 lager notat med fil direkte i testoppsettet, fordi opplasting først kommer i 2.3.
- `hent_egen`/`egne` og `slett_emne` brukes av alle senere epics. `seed_testdata` (Epic 6) bruker `slett_emne` for å kunne kjøres flere ganger.
