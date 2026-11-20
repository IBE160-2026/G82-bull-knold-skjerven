---
title: 'Story 1.1: Prosjektskjelett med datamodell og CI'
type: 'feature'
created: '2026-11-20'
status: 'in-progress'
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
- [ ] `pyproject.toml`, `.python-version`, `uv.lock`, `requirements.txt` -- `uv init --app` og `uv add`, ruff som dev, `[tool.ruff]` med `target-version = "py314"`, og `uv export --no-hashes -o requirements.txt` -- låste versjoner, og pip-vei for sensor
- [ ] `manage.py`, `farequiz/settings.py`, `farequiz/urls.py`, `farequiz/wsgi.py`, `farequiz/asgi.py` -- startproject. `settings.py` leser `.env` med `load_dotenv(BASE_DIR / ".env")` og standardverdiene fra AD-22. Appene `kontoer`, `studier` og `ki`. `LoginRequiredMiddleware`. `AUTH_USER_MODEL`. SQLite-`OPTIONS`, `ATOMIC_REQUESTS=False`, `USE_TZ=True`, `TIME_ZONE="Europe/Oslo"` og `LANGUAGE_CODE="nb"`. `MEDIA_ROOT = BASE_DIR / "media"` og `TEMPLATES.DIRS = [BASE_DIR / "templates"]`. `urls.py` er tom (`urlpatterns = []`) -- grunnlaget alle bygger på
- [ ] `farequiz/testrunner.py` -- `DiscoverRunner`-subklasse som kaller `ki.tving_testmodus()` i `setup_test_environment`, satt som `TEST_RUNNER` -- testmodus tvinges på i alle tester
- [ ] `ki/__init__.py`, `ki/apps.py` -- `er_testmodus()` leser `settings.TESTMODUS` og `settings.ANTHROPIC_API_KEY`, og `tving_testmodus()` setter et modulflagg. Ingen import fra `studier` eller `kontoer` -- eneste kilde til testmodus (AD-12)
- [ ] `kontoer/models.py`, `kontoer/apps.py`, `kontoer/migrations/0001_initial.py` -- `Bruker` og `BrukerManager` etter AD-15, med `create_user` og `create_superuser`, og e-post med små bokstaver
- [ ] `studier/models.py`, `studier/migrations/0001_initial.py`, `studier/services/__init__.py` -- alle ni modellene, se Design Notes
- [ ] `studier/tilgang.py` -- `EIERVEI` (dict fra modell til oppslag), `hent_egen` og `egne` -- AD-8
- [ ] `kontoer/tests.py`, `ki/tests.py`, `studier/tests/test_modeller.py`, `studier/tests/test_tilgang.py` -- dekker I/O-matrisen og alle ni modellene i `tilgang`
- [ ] `.env.example`, `.gitattributes`, `.gitignore` -- som i Code Map og epic-1-context.md
- [ ] `.github/workflows/test.yml` -- ved `pull_request` mot `main` og `push` til `main`: `astral-sh/setup-uv`, `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .` og `uv run python manage.py test`, uten nøkkel

**Acceptance Criteria:**
- Gitt en ny klone uten `.env`, når `uv sync`, `uv run python manage.py migrate` og `uv run python manage.py runserver` kjøres, så starter serveren på `localhost:8000` uten feil
- Gitt `requirements.txt`, når `pip install -r requirements.txt` kjøres i et tomt Python 3.14-miljø, så installeres de samme versjonene som i `uv.lock`
- Gitt migreringene, når `uv run python manage.py makemigrations --check --dry-run` kjøres, så finnes ingen endringer som ikke er migrert
- Gitt kodebasen, når den søkes gjennom, så importerer ingen fil i `ki/` fra `studier` eller `kontoer` (det sjekkes også av en test)
- Gitt en pull request mot `main`, når CI kjører, så er alle stegene grønne

## Implementation Notes

## Spec Change Log

## Review Triage Log

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
