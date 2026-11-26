---
title: 'Story 6.3: Sluttkontroll av tilgang og universell utforming'
type: 'chore'
created: '2026-11-26'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'e0efaef4b30b320d310b356ea672e5e439a93bfb'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-6-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Ingen test viser at hver URL med ID er stengt for andre brukere (SM-5), at alle sider krever innlogging, eller at S7, S9 og S12 er KI-merket med modellnavnet (SM-8). Ingen har kjørt axe mot skjermbildene (SM-7), og den manuelle kontrollen med tastatur og skjermleser er ikke planlagt (NFR-1, NFR-2, NFR-8).

**Approach:** Én tilgangstest som går gjennom URL-mønstrene selv og feiler når et nytt mønster med ID ikke er dekket. En test av innloggingskravet og en samlet test av KI-merket. En nettlesertest med axe-core mot skjermbildene i tilstandene fra EXPERIENCE.md. Brudd rettes i malene. Resultatet og sjekklisten for den manuelle kontrollen dokumenteres i en egen fil. Den manuelle kontrollen gjøres av en i gruppa.

## Boundaries & Constraints

**Always:**
- Tilgangstesten leser mønstrene fra `get_resolver()`, så en ny URL med `<int:…>` uten testoppsett gir feil med navnet på mønsteret.
- «Annen bruker» har godtatt vilkårene, så `VilkarMiddleware` ikke skjuler svaret.
- Offentlige sider: Logg inn, Registrer og Personvern (S15). Alle andre sender en utlogget bruker til Logg inn med `?next=`.
- axe kjøres med taggene `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa`, og testen feiler ved brudd med regel, selector og URL i meldingen.
- Rettelser i malene endrer ikke tekst eller flyt som andre tester låser, uten at testene oppdateres med begrunnelse.
- Nettlesertesten har en egen tag og kjører ikke i vanlig `manage.py test`, så testene kan kjøres uten nettleser.

**Never:**
- Ingen `axe`-unntak (`disableRules`) uten begrunnelse i dokumentasjonen.
- Ingen nettverkskall i testene utenom den lokale testserveren.
- Ikke bygg S16 med filer (UX-DR34, utsatt). axe kjøres på S16 slik siden er.
- Ikke endre tilgangsmodellen (`hent_egen`, `egne`) med mindre testen avslører et hull.

**Beslutninger 26.11 (Magnus):**
- axe kjøres med Playwright for Python og axe-core som dev-avhengigheter. Testen kjøres lokalt med `--tag nettleser` og i et eget CI-steg som installerer Chromium, så nye brudd stopper merge.
- 405 godtas for metoder viewet ikke tar imot, når svaret er det samme som for en ID som ikke finnes. Det avslører ikke at data finnes. Avviket fra «404 hver gang» dokumenteres i `sluttkontroll-6-3.md`.
- Storyen beholdes som én spec (cirka 2 500 tokens).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Andres ID | Kari innlogget, Olas ID i hver URL, metodene viewet tar imot | 404 med S14-teksten, ingen endring i databasen | N/A |
| Metode viewet ikke tar imot | GET på en ren POST-URL, eller POST på en ren GET-URL, med Olas ID | Samme statuskode som med en ID som ikke finnes | N/A |
| Ny URL med ID | Mønster med `<int:…>` uten oppsett i testen | Testen feiler og navngir mønsteret | N/A |
| Utlogget | GET mot hver ikke-offentlig URL | 302 til Logg inn med `next` | N/A |
| Offentlig side utlogget | Logg inn, Registrer, Personvern | 200 | N/A |
| KI-merke | Quiz med `modell="claude-haiku-5-5"` i testmodus | «Laget av KI» og «Claude Haiku 5.5» på S7, S9 og S12 | N/A |
| axe-brudd | En side med brudd | Testen feiler med regel-ID, selector og URL | N/A |

</frozen-after-approval>

## Code Map

- `studier/urls.py` -- 14 mønstre. Med ID: `emne`, `endre_navn`, `slett_emne`, `last_opp`, `notat`, `ov_pa_feil`, `jobb`, `steg`, `start_quiz`, `sporsmal` (`pk`, `nr`), `lever`, `resultat` og `meld` (`pk`, `nr`). Uten ID: `ny_emne`.
- `kontoer/urls.py` -- `logg_inn`, `registrer` og `personvern` er `login_not_required`. `logg_ut` og `vilkar` krever innlogging.
- `farequiz/urls.py` -- `startside` (S3).
- `studier/views.py` -- metodene: ren POST er `endre_navn`, `ov_pa_feil`, `steg` og `start_quiz`. Ren GET/HEAD er `emne`, `jobb` og `resultat`. Resten tar imot GET, HEAD og POST.
- `farequiz/settings.py:68` -- `LoginRequiredMiddleware`, `VilkarMiddleware`, `HtmxOmdirigeringMiddleware`.
- `templates/404.html` -- S14. `LiveServerTestCase` kjører med `DEBUG=False`, så malen brukes.
- `studier/tests/test_tilgang.py` -- tester bare `hent_egen` og `egne`. Behold dem, og legg URL-testen i en ny `studier/tests/test_tilgang_urler.py`.
- `studier/tests/fabrikk.py` -- `lag_bruker` og `lag_kjede` (emne → notat → quiz → spørsmål → økt …). Gjenbrukes for ID-ene.
- `templates/studier/notat.html:59` og `templates/studier/sporsmal.html:18` -- KI-merket. S12 bruker `sporsmal.html`.
- `ki/generering.py` `visningsnavn` -- gir modellnavnet til KI-merket.
- `studier/management/commands/seed_testdata.py` -- testbrukerens data. Nettlesertesten kan kjøre `call_command("seed_testdata")` for tilstandene med data, siden `ki/mock/` nå er committet.
- `static/js/opplasting.js` (S6b, S6c) og `static/js/fremdrift.js` (S8) -- JavaScript-tilstandene. Playwright kan forsinke eller avbryte forespørsler med `page.route`.
- `farequiz/testrunner.py` -- `TestmodusRunner`. Nettlesertesten bruker `@tag("nettleser")`, og runneren utelater taggen med mindre den er bedt om.
- `.github/workflows/test.yml` -- CI. Får et eget steg for nettlesertesten.
- `pyproject.toml` / `uv.lock` / `requirements.txt` -- dev-avhengigheter legges i dev-gruppen, så `requirements.txt` (uten dev) er uendret.

## Tasks & Acceptance

**Execution:**
- [x] `studier/tests/test_tilgang_urler.py` -- `UrlTilgangTest`: oppsett per mønsternavn med Olas ID-er, Kari innlogget. GET og POST mot hver. Forventet svar etter matrisen. Sjekk at databasen er uendret etter POST. Test at alle mønstre med `<int:…>` har oppsett -- SM-5
- [x] `studier/tests/test_tilgang_urler.py` -- `InnloggingTest`: alle mønstre uten ID og med ID (gyldig ID) som utlogget. Offentlige gir 200, andre 302 til Logg inn med `next` -- FR-2
- [x] `studier/tests/test_ki_merke.py` -- S7, S9 og S12 med `modell="claude-haiku-5-5"` viser «Laget av KI» og «Claude Haiku 5.5» -- SM-8, NFR-9
- [x] `pyproject.toml`, `uv.lock` -- dev-avhengigheter for nettlesertesten: `playwright` og axe-core (som pakke eller fastlåst `axe.min.js`)
- [x] `farequiz/testrunner.py` -- utelat taggen `nettleser` som standard
- [x] `farequiz/tests_axe.py` -- `StaticLiveServerTestCase` med `@tag("nettleser")`. Én test per skjermbilde og tilstand: S1 (tom, feil innlogging), S1b, S2 (tom, feil), S3 (ny bruker, testbrukeren), S4 (uten notater, med notater), S5/S6 (tom, avvist fil), S6b, S6c, S7 (uten quiz, med quizer og påbegynt), S8 (pågår, timeout, feil format), S9 (spørsmål, manglende svar), S10, S11, S12 (spørsmål, resultat), S13, S14, S15, S16 (tom, feil) -- SM-7
- [x] `templates/**`, `static/css/app.css` -- rett bruddene axe finner. Bygg CSS på nytt med `sh scripts/bygg-css.sh` ved klasseendringer
- [x] `.github/workflows/test.yml` -- eget steg: `playwright install --with-deps chromium` og `manage.py test --tag nettleser`
- [x] `_bmad-output/implementation-artifacts/sluttkontroll-6-3.md` -- axe-resultatet med dato, axe-core- og nettleserversjon, hvilke tilstander som er dekket og eventuelle unntak. Sjekkliste for den manuelle kontrollen: kjerneflyten med bare tastatur og med NVDA eller VoiceOver, synlig fokus, S8-stegene og poengsummen som statusmeldinger, fokus i S1b, feilmeldinger som leses opp, 320 px og 200 % tekst uten vannrett rulling, med felt for hvem, dato og funn
- [x] `README.md` -- én linje under «For gruppa» om hvordan nettlesertesten kjøres

**Acceptance Criteria:**
- Given at en ny URL med `<int:pk>` legges til i `urls.py` uten oppsett i testen, when testene kjøres, then feiler tilgangstesten med mønsterets navn.
- Given `uv run python manage.py test --tag nettleser`, when den kjøres, then gir axe null brudd på alle tilstandene.
- Given vanlig `uv run python manage.py test`, when den kjøres uten installert nettleser, then er alle testene grønne, og nettlesertesten er ikke kjørt.

## Implementation Notes

- axe fant ingen brudd i de 44 tilstandene (5 av dem på 320 px), så ingen maler eller CSS er endret. Oppgaven om å rette brudd er krysset av uten endringer.
- Kartet bak siden (`.kart-bakgrunn`) tas bort mens axe kjører, ellers blir `color-contrast` «incomplete» for nesten all tekst. Linjene er sjekket for seg i `sluttkontroll-6-3.md`. `text-error` gir 4,14:1 mot linjene og er ført som åpent punkt der, ikke rettet.
- axe-core kommer fra `axe-playwright-python` 0.1.9 (axe-core 4.14.0). Bare `axe.min.js` leses, pakken importeres ikke.
- `DJANGO_ALLOW_ASYNC_UNSAFE` settes i nettlesertestens klasse, fordi Playwrights synkrone API har en hendelsesløkke i testtråden.
- `TestmodusRunner` utelater taggen `nettleser` med mindre den er gitt med `--tag`. Testmodulen tåler at Playwright mangler (pip uten dev).

## Spec Change Log

## Review Triage Log

| # | Funn | Verdict | Bevis | Rute |
|---|------|---------|-------|------|
| V1 | axe-steget i CI blir grønt når testene hoppes over (SkipTest ved manglende pakke) | medium | `setUpClass` og `_axe_skript` hever `SkipTest`. Django teller ikke skip som feil | patch |
| V2 | Taggvalget i `TestmodusRunner` har ingen test. En feil gir 0 valgte tester og OK | medium | Ingen test nevner runneren. `exclude_tags` vinner over `tags` i `DiscoverRunner` | patch |
| V3/B2/E8 | Kontrollen med egne ID-er hopper over de fire rene POST-mønstrene | medium | `test_ola_far_ikke_404_for_egne_id_er` går bare gjennom mønstre med GET | patch |
| B3 | Innloggingstesten sender bare GET | medium | POST-viewene endrer data, og ingen test viser 302 og uendret database for utlogget POST | patch |
| B4 | axe-«incomplete» samles ikke | low | Nye «incomplete» går upåaktet hen, men å fange dem krever en tillatelsesliste. Avvist | reject |
| B5 | Kontrasten mot kartlinjene sjekkes ikke av en test | low | Bare dokumentert. En ny test med tokenlesing er mer enn en direkte rettelse. Avvist | reject |
| B6 | axe kjører bare på 1280×720 | medium | `target-size` og mobilmenyen sjekkes aldri. NFR-1 gjelder mobil | patch |
| B7 | Ingen håndheving av «ingen nettverkskall» | low | Sidene laster ingenting eksternt i dag. Avvist | reject |
| B8 | `/jobber/<id>/steg/` gir 200 for ID som ikke finnes, men 404 for en annens | low | Viser bare at en fortløpende ID finnes, ingen data. Er ført som merknad i sluttkontroll-6-3.md og blir åpent punkt i issues.md | reject |
| B9 | Åpne punkter er ikke i issues.md | false | sesjonslogg-skillen fører dem i issues.md når økten avsluttes (CLAUDE.md) | reject |
| B10 | Status ulik i spec og sprint-status. Den manuelle sjekklisten er tom | false | Steg 5 setter sprint-status til review. Den manuelle kontrollen gjøres av gruppa | reject |
| B11 | Punkt 12 i sjekklisten krever en engelsk quiz som seed ikke lager. axe ser aldri en side med `lang="en"` | medium | Seed lager ingen quiz på TXT, og ingen axe-tilstand har engelsk innhold | patch |
| B12 | `test_ki_merke.py` importerer hjelpere fra en annen testmodul | low | Kobler to testmoduler. Flytting til `fabrikk.py` er en direkte rettelse. Svakheten i strengsjekken er avvist: det finnes bare én quiz med modellen | patch |
| B13/E1 | `setUpClass` rydder ikke opp ved alle feil | low | Bare ved feil i oppstarten, og klassen er den eneste i kjøringen. Avvist | reject |
| E2 | `tearDownClass` er ikke robust | low | Samme som over. Avvist | reject |
| B14/E3 | `manage.py test farequiz.tests_axe` uten `--tag` kjører 0 tester og gir OK | medium | Runneren utelater taggen stille. Utviklere møter dette | patch |
| B15 | README mangler `--with-deps` for Linux. Seed-steget i CI har en foreldet kommentar og vakt | low | `ki/mock/` er committet, så vakten er død. Direkte rettelser. CI-cache er avvist | patch |
| B16 | Overskriften i feilmeldingen teller regler, ikke elementer | low | Direkte rettelse | patch |
| E4–E6 | Forutsetninger i axe-testene gir AttributeError i stedet for en tydelig melding | false | Testen feiler høylytt uansett. Det er riktig oppførsel | reject |
| E7/E11 | `re_path` med grupper oppdages ikke som ID-mønster | low | Prosjektet bruker bare `path()`. Avvist | reject |
| E9 | Forespørselen med ukjent ID i 405-grenen sjekkes ikke mot databasen | low | 405 kommer før viewet kjører. Avvist | reject |
| E10 | HEAD sendes ikke | false | HEAD bruker samme viewkode som GET | reject |

## Design Notes

URL-oppsettet kan være en tabell `{navn: lambda kjede: kwargs}`, der `kjede` er Olas objekter fra `lag_kjede`, og testen sammenligner nøklene med mønstrene fra resolveren. POST sendes med tomme eller gyldige skjemadata, men aldri slik at en egen rad endres. Sjekk det med antall rader og `updated` før og etter.

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- expected: rent
- `uv run python manage.py test` -- expected: alle grønne, nettlesertesten ikke kjørt
- `uv run python manage.py test --tag nettleser` -- expected: null axe-brudd
- `uv run python manage.py makemigrations --check --dry-run` -- expected: ingen endringer

**Manual checks (if no CLI):**
- Den manuelle kontrollen med tastatur og skjermleser gjøres av en i gruppa etter sjekklisten i `sluttkontroll-6-3.md`.
