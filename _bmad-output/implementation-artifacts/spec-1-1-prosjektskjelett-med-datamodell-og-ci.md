---
title: 'Story 1.1: Prosjektskjelett med datamodell og CI'
type: 'feature'
created: '2026-11-20'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'fb536991db68319124ccdaa6eda770e0eefcd186'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Repoet har ingen kode. Tre personer skal bygge parallelt, og alle stories trenger samme Django-prosjekt, hele datamodellen, eierhjelperne og CI. Ellers får gruppa migreringskonflikter og ulike løsninger på tilgang.

**Approach:** Sett opp Django-prosjektet `farequiz` med uv og appene `kontoer`, `studier` og `ki`. Lag `kontoer.Bruker` og alle modellene i `studier` med constraints, i én første migrering per app. Legg til `studier/tilgang.py`, `ki.er_testmodus()` og en CI-workflow. Feltlistene står i epic-1-context.md (Technical Decisions).

## Boundaries & Constraints

**Always:**
- Følg epic-1-context.md og AD-ene den viser til. Kode-identifikatorer er norske uten æ, ø og å.
- En ny klone uten `.env` skal kjøre med `DEBUG=True`, en fast `SECRET_KEY` merket usikker, `ALLOWED_HOSTS=localhost,127.0.0.1` og testmodus på.
- `ki` importerer aldri fra `studier` eller `kontoer`.
- Testene kjører med testmodus tvunget på og uten nettverk.
- `ruff check` og `ruff format --check` er grønne.
- **Beslutning 20.11 (uv):** Lokal uv oppdateres til ≥ 0.13 med `uv self update`. `pyproject.toml` får ikke `required-version`, slik at sensor med eldre uv eller pip fortsatt kommer i gang.

**Never:**
- **Beslutning 20.11 (admin):** Ingen Django admin. `django.contrib.admin` står ikke i `INSTALLED_APPS`, og `/admin/` finnes ikke, fordi admin kan slette utenom `slett_emne` (AD-14).
- Ingen views, URL-er for sidene, maler, Tailwind eller htmx. Det er story 1.2–1.4.
- Ingen tjenester i `studier/services/` utover en tom pakke. `slett_emne` hører til story 1.6.
- Ingen URL-rute til `MEDIA_ROOT`.
- Ingen ekte nøkkel i repoet, og ingen kall til Anthropic.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Ingen `.env` | Ny klone | `er_testmodus()` er sann, og appen starter | N/A |
| Testmodus på | `TESTMODUS` er `1`, `true`, `yes` eller `on` (uansett store og små bokstaver), med nøkkel | Sann | N/A |
| Testmodus av | `TESTMODUS=0` eller tom, og nøkkel satt | Usann | N/A |
| Tvunget | `tving_testmodus()` er kalt | Sann uansett miljø | N/A |
| Egen rad | `hent_egen(Modell, pk, eier)` | Objektet | N/A |
| Andres rad | `hent_egen(Modell, pk, annen)`, eller pk som ikke finnes | — | `Http404` |
| Liste | `egne(Modell, bruker)` | Bare brukerens rader | N/A |
| Ukjent modell | `hent_egen(Bruker, …)` | — | Feil med tydelig melding, ikke stille tilgang |
| Likt emnenavn | Samme eier, «HTML» og «html» | — | `IntegrityError` |
| To påbegynte | To påbegynte `forsok` på samme quiz, eller to påbegynte `oving` på samme notat | — | `IntegrityError` |
| Ugyldig Okt | `forsok` uten quiz, eller `oving` med quiz | — | `IntegrityError` |
| E-post | `create_user("Ola@Eks.no", …)` | Lagret som `ola@eks.no` | N/A |

</frozen-after-approval>

## Code Map

- Repoet har ingen kode. Behold `.claude/`, `_bmad/`, `_bmad-output/`, `.logs/`, `CLAUDE.md` og `README.md` uendret (README-en skrives i story 6.2).
- `.gitignore` -- finnes. Legg til `db.sqlite3` og `media/`. Den har alt `.env`, `.env.*` og `!.env.example`.
- `pyproject.toml`, `uv.lock`, `requirements.txt` og `.python-version` -- nye. Python 3.14 (uv laster den ned). Pakker: `django>=5.2.19,<6` (låses til 5.2.19), `anthropic>=2.8,<3` (2.11.0), `python-docx==1.2.0` og `python-dotenv==1.2.4`. `ruff` (0.17.6) ligger i dev-gruppen.
- `manage.py` og `farequiz/` -- nye, fra `django-admin startproject farequiz .`.

## Tasks & Acceptance

**Execution:**
- [x] `pyproject.toml`, `.python-version`, `uv.lock`, `requirements.txt` -- `uv init --app` og `uv add`, ruff som dev, `[tool.ruff]` med `target-version = "py314"`, og `uv export --no-hashes -o requirements.txt` -- låste versjoner, og pip-vei for sensor
- [x] `manage.py`, `farequiz/settings.py`, `farequiz/urls.py`, `farequiz/wsgi.py`, `farequiz/asgi.py` -- startproject. `settings.py` leser `.env` med `load_dotenv(BASE_DIR / ".env")` og standardverdiene fra AD-22. Appene `kontoer`, `studier` og `ki`. `LoginRequiredMiddleware`. `AUTH_USER_MODEL`. SQLite-`OPTIONS`, `ATOMIC_REQUESTS=False`, `USE_TZ=True`, `TIME_ZONE="Europe/Oslo"` og `LANGUAGE_CODE="nb"`. `MEDIA_ROOT = BASE_DIR / "media"` og `TEMPLATES.DIRS = [BASE_DIR / "templates"]`. `urls.py` er tom (`urlpatterns = []`) -- grunnlaget alle bygger på
- [x] `farequiz/testrunner.py` -- `DiscoverRunner`-subklasse som kaller `ki.tving_testmodus()` i `setup_test_environment`, satt som `TEST_RUNNER` -- testmodus tvinges på i alle tester
- [x] `ki/__init__.py`, `ki/apps.py` -- `er_testmodus()` leser `settings.TESTMODUS` og `settings.ANTHROPIC_API_KEY`, og `tving_testmodus()` setter et modulflagg. Ingen import fra `studier` eller `kontoer` -- eneste kilde til testmodus (AD-12)
- [x] `kontoer/models.py`, `kontoer/apps.py`, `kontoer/migrations/0001_initial.py` -- `Bruker` og `BrukerManager` etter AD-15, med `create_user` og `create_superuser`, og e-post med små bokstaver
- [x] `studier/models.py`, `studier/migrations/0001_initial.py`, `studier/services/__init__.py` -- alle ni modellene, se Design Notes
- [x] `studier/tilgang.py` -- `EIERVEI` (dict fra modell til oppslag), `hent_egen` og `egne` -- AD-8
- [x] `kontoer/tests.py`, `ki/tests.py`, `studier/tests/test_modeller.py`, `studier/tests/test_tilgang.py` -- dekker I/O-matrisen og alle ni modellene i `tilgang`
- [x] `.env.example`, `.gitattributes`, `.gitignore` -- som i Code Map og epic-1-context.md
- [x] `.github/workflows/test.yml` -- ved `pull_request` mot `main` og `push` til `main`: `astral-sh/setup-uv`, `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .` og `uv run python manage.py test`, uten nøkkel

**Acceptance Criteria:**
- Gitt en ny klone uten `.env`, når `uv sync`, `uv run python manage.py migrate` og `uv run python manage.py runserver` kjøres, så starter serveren på `localhost:8000` uten feil
- Gitt `requirements.txt`, når `pip install -r requirements.txt` kjøres i et tomt Python 3.14-miljø, så installeres de samme versjonene som i `uv.lock`
- Gitt migreringene, når `uv run python manage.py makemigrations --check --dry-run` kjøres, så finnes ingen endringer som ikke er migrert
- Gitt kodebasen, når den søkes gjennom, så importerer ingen fil i `ki/` fra `studier` eller `kontoer` (det sjekkes også av en test)
- Gitt en pull request mot `main`, når CI kjører, så er alle stegene grønne

## Implementation Notes

- **20.11, implementert og verifisert lokalt** (Windows, uv 0.13.9, Python 3.14.7):
  - `uv sync --locked`, ruff check og format, og `makemigrations --check` er grønne.
  - 54 tester er grønne, også med `--parallel 2`.
  - `runserver` uten `.env` gir 200.
  - `pip install -r requirements.txt` gir de samme 24 versjonene som `uv.lock`.
- **CI-kriteriet er ikke verifisert.** Workflowen har ikke kjørt ennå. Den kjører først ved en PR mot `main`. Taggene `actions/checkout@v7` og `astral-sh/setup-uv@v10.3.3` finnes på GitHub.
- **Tillegg utover spec-en:**
  - **ruff:** `extend-exclude` for BMAD-mappene og `*/migrations/*`, og `RUF012` ignoreres (Django `Meta`-lister).
  - **Raskere tester:** MD5-hasher bare i testkjøreren (fra 77 s til 0,5 s).
  - **`--parallel`:** en `ParallelTestSuite` som tvinger testmodus i arbeidsprosessene.
  - **`Bruker`:** `save()` gir e-post med små bokstaver, og `get_by_natural_key` skiller ikke store og små bokstaver.
  - **`tilgang`:** `hent_egen` gir 404 for ugyldige pk-er, og `egne` gir tomt queryset for en bruker som ikke er innlogget.
  - **`ki`:** `ki/models.py` og `ki/migrations/` er fjernet, fordi `ki` ikke har database.
- **Å vite om:**
  - ruff med `py314` skriver `except A, B:` uten parentes (ny syntaks i Python 3.14).
  - `requirements.txt` inneholder ruff fra dev-gruppen, fordi eksportkommandoen fra spec-en tar den med.
  - `Quiz.jobb` er påkrevd, så seed og tester må lage en `Genereringsjobb` før quizen.

## Spec Change Log

## Review Triage Log

Runde 1 (20.11). Lag: B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|---|---|---|---|
| B1, V-a | `uv.lock` mangler, så `uv sync --locked` feiler i CI | false | Fila finnes og er laget. Den ble bevisst holdt utenfor review-diffen og committes sammen med endringen. | avvist |
| B2 | CI kjører ikke `makemigrations --check` | medium | Workflowen har bare ruff og test. En modellendring uten migrering går gjennom CI og ødelegger for de andre. | patch |
| B3 | `requirements.txt` tar med ruff fra dev-gruppen | low | Ufarlig ekstra pakke for sensor. Eksportkommandoen er gruppas konvensjon i arkitekturen. Den treffer sjelden noen, og en endring gir støy hver gang andre eksporterer på nytt. | avvist |
| B4, E8, E9, E10 | `Svar`, `Okt` og `Quiz` kan peke på foreldre som ikke hører sammen (også på tvers av brukere) | false | Ingen kode skriver disse radene ennå. AD-1 legger alle skrivinger i tjenestene, AD-17 lar `lagre_svar` avvise alternativer fra feil spørsmål, og AD-8 slår opp alle ID-er med eierhjelperen (story 2.4 og 3.1). | avvist |
| B5 | Unik emne-constraint gir 500 fra skjema når `eier` mangler i skjemaet | false | Det finnes ikke noe skjema. Story 1.4 og AD-1 sier at skjemaet får `eier` i konstruktøren og sjekker unikt navn selv. | avvist |
| B6, E13 | Unik e-post uten forskjell på store og små bokstaver hviler bare på `save()` | low | `update()`, `bulk_create()` og rå SQL på e-post finnes ikke og er ikke planlagt. Lite sannsynlig, og en løsning krever en ny constraint. | avvist |
| B7, E14 | `DEBUG=False` med den usikre standardnøkkelen | low | Appen kjøres bare lokalt (NFR-4, ingen hosting). Lite sannsynlig, og en løsning krever en ny vakt. | avvist |
| B8, E16 | `LOGIN_URL` er ikke satt | false | Ingen beskyttede sider finnes ennå. Story 1.2 lager innloggingen og sendingen til Logg inn. | avvist |
| B9, E19 | `last_innstillinger` laster innstillingene på nytt mens miljøet fortsatt er patchet | low | Stemmer: `finally` kjører inne i `patch.dict`, så modulen blir stående med tomme verdier. Rettingen er bare å flytte én linje. | patch |
| B10, E17, E18, V-b | MD5-hasheren gjelder ikke i arbeidsprosessene ved `--parallel`, og `get_hashers` kan være mellomlagret | low | Stemmer: `_init_worker` kjører ikke `setup_test_environment` i runneren. Det påvirker bare hastighet. Rettingen er direkte: sett hasheren i `process_setup` også, og tøm mellomlageret. | patch |
| B11 | `Alternativ` mangler sortering | false | Visningsrekkefølgen kommer fra `Okt.innhold` (AD-16), ikke fra databasen. | avvist |
| B12, E3, E4, E5, E6, E7 | Mangler sjekker i databasen for gyldige verdier og tilstander | low | Ingen kode skriver disse feltene ennå. Tjenestene eier tilstandsovergangene (AD-9, AD-18). Lite sannsynlig, og en løsning gir flere constraints. | avvist |
| B13 | Sletting av emne etterlater filer på disk | false | `slett_emne` med filsletting hører til story 1.6 (AD-14), og ingen kode sletter emner nå. | avvist |
| B14, E11 | `notatfil_sti` bruker endelsen fra brukerens filnavn | low | Ingen opplasting finnes. Story 2.3 avviser alt annet enn PDF, DOCX og TXT før lagring. | avvist |
| B15 | Isolasjonstesten for `ki` ignorerer relative importer | false | `ki` er en toppnivåpakke. `from ..studier` gir ImportError, så en relativ import kan ikke nå `studier`. | avvist |
| E20 | Isolasjonstesten fanger ikke dynamiske importer | low | Lite sannsynlig, og en løsning gir mer testlogikk. | avvist |
| B16 | Sanne verdier står to steder | low | `settings.py` tolker `DEBUG`, og `ki` tolker `TESTMODUS`. Ingen av dem bruker den andres liste, så de kan ikke gli fra hverandre på en måte som skader. | avvist |
| E1 | SQLite `LOWER` skiller ikke store og små Æ, Ø og Å, så «Økonomi» og «økonomi» kan begge lagres | low | Stemmer for databasekontrollen. Skaden er kosmetisk (to like emner som kan få nytt navn eller slettes), og en løsning krever et nytt normalisert felt. Story 1.4 bør sammenligne med `casefold()` i Python. | avvist (notert for 1.4) |
| E2 | Tomt navn eller navn med mellomrom | false | Ingen skriving finnes. Skjemaet i 1.4 krever navn, og Djangos `CharField` i skjema fjerner mellomrom før og etter. | avvist |
| E12 | `sist_endret` oppdateres ikke automatisk | false | Det er bevisst: `lagre_svar` setter feltet selv (AD-17, Design Notes). | avvist |
| E15 | Skrivefeil i `DEBUG` slår den av uten varsel | low | Lite sannsynlig, og en løsning krever en ny vakt. | avvist |
| V1 | Testmodus i arbeidsprosessene ved `--parallel` blir aldri testet | low | Laget leverte funnet ferdig verifisert. Et parallelt CI-steg krever eksplisitt spawn-oppsett (forkserver er standard på Linux med 3.14). | defer |
| V2 | At `Bruker.clean()` gjør e-posten til små bokstaver, er ikke testet | low | Laget leverte funnet ferdig verifisert. En test med `full_clean()` mangler, og den er en direkte tilføyelse. | patch |

## Design Notes

Disse valgene har ikke arkitekturen tatt, så de tas her:
- **Felter utover arkitekturen:** `opprettet` (`auto_now_add`) på `Emne`, `Notat`, `Quiz` og `Feilbankrad`. Quiz trenger dato (FR-16), og øvingsøkten sorteres på når feilbankraden ble opprettet. `Emne.navn` er `CharField(max_length=100)`. `Feilbankrad.riktige_pa_rad` er `PositiveSmallIntegerField(default=0)`. `Okt.sist_endret` har `default=timezone.now` og ikke `auto_now`, fordi `lagre_svar` setter den selv. `Svar.hendelse` er `blank=True, default=""` til levering. `Okt.innhold` har `default=list`. `Spørsmål` sorteres på `id`.
- **Ekstra constraints:** `UniqueConstraint(Lower("navn"), "eier")` på `Emne` sikrer unikt navn også ved dobbeltinnsending. `UniqueConstraint(fields=["sporsmal"], condition=Q(er_riktig=True))` på `Alternativ` gir høyst ett riktig svar. `Feilbankrad.sporsmal` er en `OneToOneField`. Alle fremmednøkler fra `Emne` og nedover bruker `CASCADE`.
- **Django 5.2:** `CheckConstraint(condition=…)`, siden `check=` er utgått.
- **`related_name`:** `emner`, `notater`, `quizer`, `sporsmal`, `alternativer`, `okter`, `svar`, `jobber`, `feilbankrad` og `quiz` (fra jobben).
- **`upload_to`:** funksjonen `notatfil_sti(instance, filnavn)` gir `notater/<eier-id>/<uuid4><endelse>`.
- **Oppstart:** AC-ene bruker `uv run python manage.py`, fordi `python` ikke peker på prosjektmiljøet etter `uv sync` uten aktivering. README-ordlyden tas i story 6.2.

## Verification

**Commands:**
- `uv sync --locked` -- expected: ingen endringer i låsefila
- `uv run ruff check . && uv run ruff format --check .` -- expected: 0 funn
- `uv run python manage.py makemigrations --check --dry-run` -- expected: «No changes detected»
- `uv run python manage.py test` -- expected: alle tester grønne, ingen nettverkskall
- `uv run python manage.py migrate` på en tom database, deretter `uv run python manage.py check` -- expected: ingen feil
