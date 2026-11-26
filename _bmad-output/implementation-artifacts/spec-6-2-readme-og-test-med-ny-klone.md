---
title: 'Story 6.2: README og test med ny klone'
type: 'chore'
created: '2026-11-26'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '37bc1a547b3254cec2f2c25ede7d04ce7aeb3784'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-6-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** README-en har i dag bare gruppa, testbrukeren og et avsnitt om mock-svar. Sensor kan ikke installere og kjøre appen med den alene (FR-29, FR-30, AD-22, SM-1).
- `requirements.txt` er utdatert og mangler `whitenoise`, så pip-veien gir en app som ikke starter.
- CI fanger ikke en ødelagt seed.

**Approach:** Skriv README-en om til en oppskrift for sensor. Generer `requirements.txt` på nytt, og la CI sjekke at den er i takt med `uv.lock`. Legg seed på en tom database inn i CI. Den manuelle testen med ny klone gjøres av en i gruppa og dokumenteres i sesjonsloggen.

## Boundaries & Constraints

**Always:**
- **README** (norsk bokmål, du-form, kort og saklig, uten utropstegn og emojier). Rekkefølge:
  1. **Hva appen gjør:** to til tre setninger.
  2. **Hva som trengs:** Python 3.14 og uv, eller pip.
  3. **Kom i gang:** nøyaktig `uv sync` (eller `pip install -r requirements.txt` i et virtuelt miljø), `python manage.py migrate`, `python manage.py seed_testdata` og `python manage.py runserver`. Med uv skrives kommandoene med `uv run` foran. Adressen er `http://127.0.0.1:8000/`.
  4. **Testbruker:** e-post og passord fra `kontoer/testbruker.py`, og hva seed lager.
  5. **Testmodus:** den er på uten `.env`, og banneret «Testmodus: quizene bruker mock-svar, ingen KI kalles.» betyr at quizene kommer fra lagrede svar. En egen fil gir et standard testdokument med merknad.
  6. **Ekte modell:** kopier `.env.example` til `.env` (kommando for Windows og for macOS/Linux), legg inn `ANTHROPIC_API_KEY`, sett `TESTMODUS=0`, og bytt eventuelt `KI_MODELL`.
  7. **Mobil på samme nett:** legg maskinens IP i `ALLOWED_HOSTS` i `.env` og kjør `runserver 0.0.0.0:8000`. Dette er ikke hosting.
  8. **For gruppa:** `lag_mocksvar` og at `ki/mock/` committes.
  9. **Medlemmer.**
- **Tester:** stegene, e-posten og passordet, banneret, `.env.example`, `ANTHROPIC_API_KEY`, `TESTMODUS`, `KI_MODELL` og `ALLOWED_HOSTS` står i README-en. Banneret i README-en er det samme som i `templates/base.html`.
- **`requirements.txt`:** genereres med `uv export --no-hashes -o requirements.txt`. CI genererer den på nytt med `--frozen` og feiler hvis `git diff --exit-code requirements.txt` viser forskjell.
- **CI-seed:** et steg etter testene kjører `migrate` og `seed_testdata` på en tom database.
  - Besluttet 26.11: steget kjører seed bare når `ki/mock/manifest.json` finnes. Ellers gir det en GitHub-advarsel (`::warning::`) om at seed er hoppet over fordi mock-svarene mangler. Når mock-filene er committet, kjører det alltid.
- **Manuell test med ny klone:** står som åpent punkt i sesjonsloggen, med sjekkliste og et felt for hvem, hvilket OS og hvilken dato. 6.2 står i `review` til den er gjort på Windows og på macOS eller Linux.

**Never:**
- Ikke endre appkoden utover det en avviker i README-en eller i den manuelle testen krever.
- Ingen hosting eller Docker.
- Ikke commit `.env` eller nøkler.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| README komplett | README.md | testen finner alle stegene og navnene over | testen feiler med det som mangler |
| Banner i takt | teksten i `base.html` endres | README-testen feiler | N/A |
| requirements i takt | ny avhengighet i `pyproject.toml` uten ny `requirements.txt` | CI-steget feiler | N/A |
| pip-veien | `requirements.txt` | inneholder `whitenoise` og alt fra `uv export` | N/A |
| Seed i CI | tom database, `ki/mock/` finnes | steget lykkes | en ødelagt seed stopper merge |

</frozen-after-approval>

## Code Map

- `README.md` -- skrives om. Behold «Medlemmer» og innholdet i «Testbruker» og «Testmodus og mock-svar», men ordne det som over.
- `kontoer/testbruker.py` -- `EPOST` og `PASSORD`. Testen bruker dem.
- `templates/base.html:18` -- bannerteksten. Testen leser den fra malen, ikke fra en kopi.
- `.env.example` -- variablene `ANTHROPIC_API_KEY`, `KI_MODELL`, `TESTMODUS`, `SECRET_KEY`, `DEBUG` og `ALLOWED_HOSTS` finnes. Endres bare hvis README-testen avslører noe.
- `farequiz/settings.py` -- leser `.env` med `load_dotenv`, `ALLOWED_HOSTS` som kommaliste og `KI_MODELL`.
- `requirements.txt` -- mangler `whitenoise` (lagt til i 1.3, `d7a8f89`). Generer den på nytt.
- `.github/workflows/test.yml` -- legg til to steg: «requirements.txt er i takt» og «Seed på tom database».
- `studier/tests/test_seed.py` `ReadmeTest` -- flytt til en egen `farequiz/tests_readme.py` og utvid den.

## Tasks & Acceptance

**Execution:**
- [x] `requirements.txt` -- generer på nytt.
- [x] `README.md` -- skriv om etter rekkefølgen over.
- [x] `farequiz/tests_readme.py` -- README-testen (flyttet fra `test_seed.py` og utvidet).
- [x] `.github/workflows/test.yml` -- stegene for requirements og seed.

**Acceptance Criteria:**
- Gitt README-en, når testene kjøres, så finner de de fire stegene, testbrukeren, banneret og alle `.env`-variablene sensor trenger.
- Gitt en PR, når CI kjører, så feiler den hvis `requirements.txt` ikke er i takt med `uv.lock`.

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv export --no-hashes --frozen -o requirements.txt && git diff --exit-code requirements.txt` -- ingen forskjell
- `uv run python manage.py test` -- alle grønne

**Manual checks:**
- README-en leses fra start til slutt som sensor. Alle kommandoene finnes og stemmer med koden.

## Implementation Notes

- **Implementert av en underagent.** Review med tre reviewere på Opus.
- **README:**
  - Skrevet om i rekkefølgen fra spec-en.
  - Bannerteksten er den samme som i `base.html`.
  - Kopieringskommandoene er med for Windows og for macOS/Linux.
- **`requirements.txt`:** generert med `--frozen`, fordi `uv export` skriver kommandoen i hodet på fila. CI bruker samme kommando, så fila ville ellers alltid vist forskjell. At `uv.lock` er i takt med `pyproject.toml`, sjekker `uv sync --locked`.
- **Hovedsesjonen la til `RequirementsTest`:** matriseraden om pip-veien var ellers bare dekket av CI-steget, som ikke kjøres lokalt.
- **CI:**
  - Steget «requirements.txt er i takt» kommer etter installasjonen.
  - Steget «Seed på tom database» kommer etter testene, og bare når `ki/mock/manifest.json` finnes (besluttet 26.11).
- **Etter review:**
  - Rekkefølgen sjekkes nå bare i «Kom i gang», for både uv og pip.
  - `--no-dev`, så `ruff` ikke er med i `requirements.txt`.
  - Navnene normaliseres etter PEP 503, og Python-versjonen leses fra `requires-python`.
  - README-en fikk:
    - kloningssteg
    - `py -3.14` og et hint om PowerShell
    - `runserver 0.0.0.0:8000` med pip og `hostname -I`
    - en advarsel om `DEBUG=True`
    - presis tekst om når testmodus er på, og standardmodellen

## Spec Change Log

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 26.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| V1 | Rekkefølgetesten treffer `uv sync` i «Hva som trengs», og pip-rekkefølgen sjekkes ikke | medium | Filed gap, bekreftet: `index` gir første treff | patch |
| E8 | Samme som V1 | medium | Samme som V1 | patch (med V1) |
| V2 | CI-seed hoppes alltid over i dag | low | Hoppes over med vilje (besluttet 26.11). Lukkes når `ki/mock/` committes, og står som åpent punkt | avvist |
| B2 | Samme som V2 | low | Samme som V2 | avvist |
| E1 | Samme som V2 | low | Samme som V2 | avvist |
| E11 | Påstanden «CI fanger en ødelagt seed» stemmer ikke ennå | low | Samme som V2. Spec-en sier at steget hoppes over til mock-svarene finnes | avvist |
| B1 | «Kom i gang» feiler på `seed_testdata` i dag | low | Sant til `ki/mock/` er committet. Klonetesten og leveransen kommer etter det. «For gruppa» sier det, og den setningen fjernes når mock-svarene committes (åpent punkt) | avvist |
| E3 | Samme som B1 | low | Samme som B1 | avvist |
| B3 | `ruff` er med i `requirements.txt` | low | Bekreftet: `uv export` tar med dev-gruppen. Ett flagg | patch |
| B4 | CI tester ikke pip-veien | low | Underagenten prøvde pip-veien i et rent venv. Den manuelle klonetesten dekker resten. En ny CI-jobb er mer enn en enkel rettelse | avvist |
| B5 | Pip-veien: `python` er kanskje ikke 3.14, PowerShell-policy, og `runserver 0.0.0.0` bare med uv | medium | Bekreftet. Vanlig på Windows. Rettes i README-en | patch |
| E4 | PowerShell-policy stopper `activate` | medium | Samme som B5 | patch (med B5) |
| E5 | `python` er ikke 3.14 | medium | Samme som B5 | patch (med B5) |
| B6 | Mangler kloningssteg | low | Bekreftet. To linjer | patch |
| B7 | Testmodus-avsnittet mangler `TESTMODUS=1` og tom nøkkel, og standardmodellen nevnes ikke | low | Bekreftet mot `ki/__init__.py` og `.env.example` | patch |
| E6 | Variabler i skallet overstyrer «uten `.env`» | low | Samme rot som B7. Presis tekst om nøkkel og `TESTMODUS` dekker det | patch (med B7) |
| B8 | Ingen advarsel om `DEBUG=True` på delt nett | low | Bekreftet. Én setning | patch |
| E7 | Ingen IP-kommando for Linux | low | Bekreftet. `hostname -I` | patch |
| B9 | «uv» og «Python 3.14» sjekkes som deltekst, og versjonen er hardkodet | low | Bekreftet. Les fra `requires-python` | patch |
| B10 | `test_kommandoene_finnes` hardkoder stier og gjentar andre tester | low | Bare testkode, og den feiler tydelig hvis stien endres | avvist |
| B11 | `RequirementsTest` normaliserer ikke navn og fanger ikke dev-verktøy | low | Bekreftet. Enkel normalisering, og `ruff` skal ikke være med | patch (med E10) |
| E10 | Samme som B11 | low | Samme som B11 | patch |
| B12 | Spec-en og `sprint-status.yaml` er ikke med i diffen | false | Utelatt med vilje. Review gjelder koden | avvist |
| E2 | Ulik uv-versjon lokalt og i CI kan gi falsk diff | maybe-false | Ikke påvist. Avgjøres ved første CI-kjøring | defer |
| E9 | Utropstegn-testen fjerner ikke kodeblokker med ``` eller bilder | low | README-en har ingen av delene, og testen feiler tydelig | avvist |
| V-a | `ENV_VARIABLER` er hardkodet | low | Sjekkes mot `.env.example`, som er det sensor kopierer | avvist |
