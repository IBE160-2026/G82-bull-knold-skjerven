---
title: 'Story 2.5: Feil, timeout og «Prøv igjen»'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 1
baseline_commit: 'd4dd53a31ee5b7abd06b5d63cd6580d6737a966b'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Når genereringen feiler, viser S8 bare «Klarte ikke å lage quizen.». Brukeren får ikke vite hva som gikk galt eller hva hen kan gjøre, og må tilbake til S7 for å prøve igjen. Slettes notatet underveis, gir stegendepunktet 500 (FR-13, FR-15, TF-4).

**Approach:** Én feiltekst per feilkode, «Prøv igjen» med samme fil og samme valg, tidsfristen også når S8 lastes, og et sluttfragment når jobben eller notatet er borte.

## Boundaries & Constraints

**Always:**
- **Tekster i `farequiz/feilmeldinger.py`**, én per feilkode. Henvisningen `GENERERING_FEILET` erstattes.
  - `timeout`: «Genereringen tok for lang tid. Filen er lagret, så du kan prøve igjen.»
  - `format`: «Klarte ikke å lage en gyldig quiz. Prøv igjen, eller velg færre spørsmål.»
  - `api_feil`: «KI-tjenesten svarte ikke. Prøv igjen.»
  - `for_lite_innhold`: «Filen har for lite tekst til å lage en quiz. Last opp et notat med mer innhold.»
  - `for_stor`: «Filen er for stor til at KI-tjenesten kan lese den. Del opp notatet og last opp delene hver for seg.»
  - `api_nokkel`: «KI-tjenesten godtok ikke API-nøkkelen. Sjekk nøkkelen i .env, eller slå på testmodus.»
  - Tom eller ukjent kode gir teksten for `api_feil`.
- **S8 ved feilet jobb**, både ved GET og som HTMX-svar:
  - Stegene i `#fremdrift` byttes ut med teksten i `role="alert"`.
  - For `format`, `api_feil` og `api_nokkel` står «Filen er lagret, så du trenger ikke laste den opp på nytt.» under (fra prototypen, S8b). Den står ikke for `timeout`, `for_lite_innhold` eller `for_stor` (beslutning 25.11 etter review, B3: setningen sa imot tekstene som ber om ny opplasting).
  - Hjelpeteksten og den låste «Lag quiz» byttes ut med knappen «Prøv igjen», som har `autofocus`, og lenken «Tilbake til notatet».
  - Ingen spørring går etter dette.
- **«Prøv igjen»** er et vanlig POST-skjema mot S7 (`/notater/<id>/`) med jobbens `vanskelighetsgrad` og `antall` i skjulte felt. `opprett_jobb` gir en ny jobb, eller den aktive jobben hvis den finnes, og brukeren sendes til S8 for den. Det virker også uten JavaScript.
- **Tidsfrist:** S8 (GET) kaller `aktiv_jobb(notat)` før visning. En jobb eldre enn 120 s vises derfor straks som `timeout`.
- **Sluttfragment:** POST til `/jobber/<id>/steg/` for en jobb som ikke finnes (aldri fantes, eller er slettet sammen med notatet eller emnet, også midt i et steg) gir status 200.
  - `#fremdrift` får «Notatet finnes ikke lenger, så quizen ble ikke laget.» i `role="alert"` og lenken «Gå til Oversikt» (S3). Ingen ny spørring, og ingen quiz.
  - En annen brukers jobb gir fortsatt 404.
- Feilede jobber logges med jobb-ID og kode, aldri med filinnhold (finnes fra 2.4).
- **Beslutning 25.11 (Christian): nettfeil, serverfeil og utløpt økt er med i 2.5.**
  - **Serverfeil og nettfeil:** feiler spørringen fra `#spor` (`htmx:responseError` eller `htmx:sendError`), viser `#fremdrift` «Fikk ikke kontakt med serveren. Last inn siden på nytt.» i `role="alert"`, og spørringen stopper.
    - Koden ligger i en egen statisk fil, `static/js/fremdrift.js`, som lastes på S8. Ikke inline-skript.
    - Teksten kommer fra `feilmeldinger.py` via et `data-*`-attributt.
  - **Utløpt økt:** en HTMX-forespørsel (`HX-Request: true`) som ville fått en omdirigering til innloggingen eller `/vilkar/`, får i stedet status 200 med tom kropp og `HX-Redirect` til samme side (innloggingen eller `/vilkar/`). `next` er siden brukeren står på, altså `HX-Current-URL` (bare stien, for eksempel `/jobber/<id>/`), ikke endepunktet forespørselen gikk til. Mangler headeren, sendes ingen `next` (beslutning 25.11 etter review, B1: `next=/jobber/<id>/steg/` ga 405 etter innlogging). Da byttes siden i nettleseren, og innloggingssiden byttes ikke inn i S8.
    - Gjøres av ny mellomvare i `kontoer/middleware.py`, som ligger før `LoginRequiredMiddleware` i `MIDDLEWARE`.
- «Prøv igjen» vises for alle feilkoder (AC-ene og TF-4), også der et nytt forsøk trolig feiler igjen (`for_lite_innhold`, `for_stor`, `api_nokkel`). Teksten sier hva brukeren kan gjøre.

**Never:**
- Ikke endre `ki`, modellene, migreringene, skjemaet på S7 eller quizkortene.
- Ingen automatiske nye forsøk utover runde 2 for `format` (2.4).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Hver feilkode | `ki`-stub hever `KIFeil(kode)` for hver av de seks kodene | `feilet`/kode, ingen quiz, S8-fragment med kodens tekst og «Prøv igjen» med `autofocus` | Logget med ID og kode |
| Timeout ved S8 | aktiv jobb, `startet` 121 s siden, GET S8 | Timeout-tekst og «Prøv igjen», ingen `hx-post` | N/A |
| Prøv igjen | POST fra S8 for feilet jobb (lett, 7) | Ny jobb `leser`, lett, 7, samme notat, redirect til ny S8 | N/A |
| Prøv igjen med aktiv jobb | en annen aktiv jobb finnes | Ingen ny jobb, redirect til den aktive | N/A |
| Notat slettet underveis | emnet slettes mens steget kjører eller mellom kall | Status 200, sluttfragment med lenke til `/`, ingen `#spor`, ingen quiz | N/A |
| Jobb finnes ikke | POST steg for ukjent ID | Som over | N/A |
| Annens jobb | POST steg eller GET S8 | Ingenting endres | 404 |
| Kort TXT | ekte opplasting av `kort.txt` («Hei.»), `generer` hever `for_lite_innhold` | Teksten for `for_lite_innhold` | N/A |
| Ugyldig nøkkel | testmodus av, nøkkel satt, klienten hever `AuthenticationError` | `feilet`/`api_nokkel`, teksten for nøkkel | Ingen nettverkskall |
| Utløpt økt under spørring | utlogget klient, POST steg med `HX-Request: true` og `HX-Current-URL` lik S8 | Status 200, `HX-Redirect` til innloggingen med `next=/jobber/<id>/` | N/A |
| Uten HTMX | utlogget vanlig GET | Vanlig 302 til innloggingen, som før | N/A |
| Serverfeil eller nettfeil | `/steg/` svarer 500, eller nettet faller ut | Meldingen om serverkontakt i `#fremdrift`, spørringen stopper | Kontrolleres i nettleser |

</frozen-after-approval>

## Code Map

- `studier/services/generering.py` -- `aktiv_jobb`, `opprett_jobb`, `kjor_steg` (gir `True`/`False`). `_feilet` logger allerede. Trenger trolig ingen endring.
- `studier/views.py:240-279` -- `_fremdrift_kontekst` (bruker `GENERERING_FEILET`), `jobb` (S8) og `steg` (`hent_egen`, så `kjor_steg` og `refresh_from_db`, som gir `DoesNotExist` hvis jobben slettes midt i steget). `notat` (S7 POST) tar imot «Prøv igjen».
- `templates/studier/jobb.html` -- hjelpetekst og låst knapp står utenfor `#fremdrift` i dag. De må kunne byttes ut ved feil, for eksempel i en egen region som byttes med `hx-swap-oob`. Ikke legg dem inne i `aria-live`-regionen.
- `templates/studier/_steg.html` (innhold i `#fremdrift`) og `_fremdrift.html` (svaret: `#spor` og oob-`#fremdrift` når `endret`).
- `farequiz/feilmeldinger.py` -- `GENERERING_FEILET` fra 2.4.
- `studier/tilgang.py` -- `hent_egen` gir 404 både når jobben mangler og når den tilhører en annen. Skill dem fra hverandre i `steg`: jobben finnes ikke → sluttfragment, finnes men er en annens → 404.
- `studier/services/emner.py:57-58` -- `slett_emne` sletter med kaskade og fjerner filene etter commit.
- `ki/generering.py:186-227` og `ki/tests_generering.py:300` -- `_klient(timeout)` og hvordan `AuthenticationError` blir `api_nokkel` (`statusfeil`-hjelperen). Testmodus er tvunget i tester (`ki._tvunget`). Testen for ugyldig nøkkel må patche `ki._tvunget=False`, `ANTHROPIC_API_KEY` og `generering._klient`.
- `studier/tests/test_generering.py` -- `GenereringTestCase`, `_kjor_alle`, `_raatt`. 2.4-testene som sjekker `GENERERING_FEILET`, må oppdateres.
- `static/js/htmx.min.js` -- fokuserer `[autofocus]` i nytt innhold etter bytte (`Ne`), så det trengs ingen egen JavaScript for fokus.
- `kontoer/middleware.py` (`VilkarMiddleware` omdirigerer til `/vilkar/`) og `farequiz/settings.py:68-79` (`MIDDLEWARE`). Django 5.2 `LoginRequiredMiddleware` gir 302 til `LOGIN_URL` med `next`.
- `templates/studier/last_opp.html` og `static/js/opplasting.js` -- mønster for statisk JS med tekster fra `data-*`.
- Prototype S8b: `_bmad-output/planning-artifacts/ux-designs/ux-G82-bull-knold-skjerven-2026-11-11/prototype/index.html:429-439`.

## Tasks & Acceptance

**Execution:**
- [x] `farequiz/feilmeldinger.py` -- teksten per kode og et oppslag fra kode til tekst
- [x] `studier/views.py` -- feiltekst per kode, tidsfrist i `jobb`, sluttfragment i `steg`, kontekst for «Prøv igjen»
- [x] `templates/studier/jobb.html`, `_steg.html`, `_fremdrift.html` -- feiltilstand med «Prøv igjen», sluttfragment
- [x] `static/js/fremdrift.js` -- melding ved `htmx:responseError` og `htmx:sendError`
- [x] `kontoer/middleware.py`, `farequiz/settings.py` -- `HX-Redirect` i stedet for omdirigering til innloggingen eller vilkårene for HTMX-forespørsler
- [x] `studier/tests/test_feil.py` (og `kontoer/tests.py` for mellomvaren) -- én test per rad i matrisen, unntatt nettleserraden. Oppdater 2.4-testene som bruker `GENERERING_FEILET`.

**Acceptance Criteria:**
- Gitt S8 i en nettleser med JavaScript og en jobb som feiler, når feilen kommer, så står kodens tekst, og «Prøv igjen» har fokus.
- Gitt S8 uten JavaScript og en feilet jobb, når brukeren trykker «Prøv igjen», så lages en ny jobb med samme valg, og S8 vises for den.

## Implementation Notes

- **Tekster:** `feilmeldinger.GENERERING_FEIL` (én per kode) og `generering_feilet(kode)` (`api_feil` for tom eller ukjent kode). Nye tekster: `FIL_ER_LAGRET`, `NOTAT_FINNES_IKKE` og `INGEN_SERVERKONTAKT`.
- **Tilgang:** `studier.tilgang.hent_egen_eller_none` gir `None` når raden ikke finnes, og 404 når den tilhører en annen. `steg` bruker den, og fanger `DoesNotExist` etter `kjor_steg` (slettet midt i et steg).
- **S8:**
  - `#handlinger` (utenfor `aria-live`) har hjelpeteksten og den låste knappen, eller ved feil «Prøv igjen» og «Tilbake til notatet».
  - `_handlinger.html` byttes med oob ved feil. `_slutt.html` er sluttfragmentet.
  - `jobb` kaller `aktiv_jobb` før visning.
- **`static/js/fremdrift.js`:** viser `data-feil-server` i `#fremdrift`, tømmer `#handlinger` og fjerner `#spor` ved `htmx:responseError` eller `htmx:sendError` fra `#spor`.
- **`kontoer.middleware.HtmxOmdirigeringMiddleware`:** ligger før `LoginRequiredMiddleware`. `next` er stien i `HX-Current-URL`, bare hvis `url_has_allowed_host_and_scheme` godtar den. Ellers sendes ingen `next`.
- **Verifisert:**
  - ruff, `makemigrations --check` og 306 tester grønne, 1 hoppet over (`EkteMockfilerTest`).
  - Headless Edge via CDP mot en midlertidig server, med en stub der første `generer` feiler og `/steg/` svarer 500 én gang:
    - feilteksten vises, og fokus er på «Prøv igjen»
    - etter feil går ingen spørring
    - «Prøv igjen» gir ny S8 og ender på S7 med kortet
    - 500 gir meldingen om serverkontakt, og spørringen stopper
    - utløpt økt gir innloggingen med `next=/jobber/<id>/`

## Spec Change Log

- **25.11, pass 1, B1 og B3 (intent_gap):** Christian valgte to endringer i det frosne kravet:
  - `next` ved utløpt økt er siden brukeren står på (`HX-Current-URL`), ikke steg-endepunktet. Tidligere ga det 405 etter innlogging.
  - «Filen er lagret …» vises ikke for `for_lite_innhold` og `for_stor`. Tidligere sa setningen imot hovedteksten.
  
  Etter brukerens valg ble koden ikke rullet tilbake. Endringene rettes sammen med patchene fra pass 1 (B7 og B10). KEEP: tjenesten, viewene, malene, `fremdrift.js`, mellomvaren og alle testene, bortsett fra forventningene som disse beslutningene endrer.

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 25.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | `next` i `HX-Redirect` peker på `/jobber/<id>/steg/`, som bare tar POST. Etter innlogging gir det 405. Vilkårstilfellet ved POST mangler `next` | medium | Bekreftet i headless Edge: adressen ble `/logg-inn/?next=/jobber/3/steg/`. Det frosne punktet sier «`HX-Redirect` til samme adresse» | intent_gap |
| B2 | 200 for en jobb som ikke finnes, men 404 for en annens jobb, avslører hvilke jobb-ID-er som finnes | low | Stemmer, men ID-ene er fortløpende, og det lekker bare at ID-en finnes, ikke noe innhold. Det frosne punktet krever 404 for en annens jobb | avvist |
| B3 | «Filen er lagret, så du trenger ikke laste den opp på nytt» sier imot teksten for `for_lite_innhold` og `for_stor`, som ber om ny opplasting | low | Bekreftet: begge tekstene vises sammen. Regelen «utenom `timeout`» står i det frosne punktet | intent_gap |
| B4 | «Prøv igjen» vises også der et nytt forsøk ikke kan lykkes, og `format` sender samme antall | low | Det frosne punktet bestemmer «Prøv igjen» for alle koder (AC-ene, TF-4). Antallet kan endres via «Tilbake til notatet» | avvist |
| B5 | Teksten for `api_nokkel` gir driftsråd til sluttbrukeren | low | Teksten er godkjent i det frosne punktet. Appen kjøres lokalt, av den som selv setter `.env` | avvist |
| B6 | `api_feil` brukes som standard også for interne feil | low | Bevisst valg i 2.4 (uventet unntak gir `api_feil`) | avvist |
| B7 | Etter 500 eller nettfeil står hjelpeteksten og den låste «Lag quiz» fortsatt. Teksten for `responseError` er unøyaktig. `htmx:timeout` håndteres ikke | low | Bekreftet for `#handlinger`, og det er misvisende mens meldingen sier «Last inn siden på nytt». Direkte rettelse: tøm `#handlinger` i `fremdrift.js`. Tekst og timeout: htmx har ingen standard tidsavbrudd, og serveren svarer innen cirka 120 s | patch (`#handlinger`) |
| B8 | `fremdrift.js` har ingen automatisk test | medium | Samme som V1 | defer |
| B9 | GET og HEAD på S8 endrer tilstand, og `aktiv_jobb` sjekker kanskje ikke jobben med `pk` | false | Det frosne punktet krever tidsfristsjekk på S8. `aktiv_jobb` setter alle gamle aktive jobber på notatet til timeout, også den med `pk` | avvist |
| B10 | `TeksterTest` sammenligner med en hardkodet liste, ikke med `Feilkode.values` | low | En ny kode i modellen ville fått `api_feil`-teksten uten at noen test feiler. Direkte rettelse i testen | patch |
| B11 | Sammenligningen på sti feiler hvis `LOGIN_URL` er absolutt | false | `LOGIN_URL = "kontoer:logg_inn"`, så `resolve_url` gir en sti | avvist |
| B12 | `autofocus` på full sidelasting hopper over `<h1>` og kan avbryte opplesningen av varselet | low | UX-DR18 og det frosne punktet: «Prøv igjen» får fokus | avvist |
| E1 | `next` peker på POST-endepunktet | medium | Samme som B1 | intent_gap |
| E2 | Mellomvaren erstatter svaret, så headere og kapsler fra indre mellomvare forsvinner | low | Svaret har tom kropp og bare `HX-Redirect`. Økt- og CSRF-kapsler settes av ytre mellomvare etterpå. `X-Frame-Options` på en tom kropp har ingen verdi | avvist |
| E3 | S8 (GET) gir 500 hvis jobben slettes mellom `hent_egen` og `refresh_from_db` | low | Et vindu på millisekunder. Krever en ny vakt | avvist |
| E4 | ID-er avsløres med 200 og 404 | low | Samme som B2 | avvist |
| E5 | `htmx:timeout` håndteres ikke | low | Samme som B7 | avvist |
| E6 | «Prøv igjen» for koder som alltid feiler | low | Samme som B4 | avvist |
| V1 | Ingen automatisk test kjører `fremdrift.js` | medium | Godtatt slik den ble levert. Repoet har ikke noe testoppsett for JavaScript (som i 2.3). Kontrollert manuelt i headless Edge | defer |

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne

**Manual checks:**
- Headless Edge mot en midlertidig server med en `ki`-stub som feiler: feilteksten vises, «Prøv igjen» har fokus (`document.activeElement`), og et klikk gir ny S8 som ender på S7. La `/steg/` svare 500 én gang og se at meldingen om serverkontakt vises og at spørringen stopper.
