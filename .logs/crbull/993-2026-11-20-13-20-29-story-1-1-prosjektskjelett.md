# Story 1.1: Prosjektskjelett

## 2026-11-20 kl. 13:20 — crbull

### Oppgave
Bygge story 1.1, «Prosjektskjelett med datamodell og CI», med `bmad-build`: et kjørbart Django-prosjekt med hele datamodellen, eierhjelperne, testmodus og CI, som resten av gruppa kan bygge på.

### Plan
- Build-workflowen ble fulgt fra den rendrede skill-fila, og subagenter ble brukt med Christians tillatelse.
- Ny branch fra `arkitektur-epics-christian`, senere omdøpt til `story-1-1-prosjektskjelett-christian` slik at gruppa ser at den er Christians.
- En subagent samlet epic-konteksten i `_bmad-output/implementation-artifacts/epic-1-context.md`.
- Spec: [spec-1-1-prosjektskjelett-med-datamodell-og-ci.md](../../_bmad-output/implementation-artifacts/spec-1-1-prosjektskjelett-med-datamodell-og-ci.md). Beslutninger tatt sammen:
  - Spec-en beholdes hel (omtrent 2 700 tokens).
  - Ingen Django admin, fordi den bryter AD-14.
  - uv oppdateres til 0.13.9, uten hardt krav i `pyproject.toml`.
  - Spec-en skrives på norsk.
- Implementert av en subagent. Etterpå ble diffen verifisert her, og tre review-subagenter (Blind Hunter, Edge Case Hunter og Verification Gap) gikk gjennom den.

### Resultat
- Commit `844deb4` på `story-1-1-prosjektskjelett-christian`:
  - Django 5.2.19 og Python 3.14 med uv, `requirements.txt` og appene `farequiz`, `kontoer`, `studier` og `ki`.
  - `kontoer.Bruker` og alle ni modellene i `studier`, med constraints og første migrering.
  - `studier/tilgang.py`, `ki.er_testmodus()` og en test-runner som tvinger testmodus på.
  - `.github/workflows/test.yml` med migreringssjekk, ruff og tester.
- Verifisert lokalt: `uv sync --locked`, ruff, `makemigrations --check`, 55 tester, migrate og check på en tom database. `runserver` uten `.env` gir 200, og `pip install -r requirements.txt` gir de samme versjonene.
- Reviewen ga 38 funn. 4 er rettet: migreringssjekk i CI, gjenoppretting i en testhjelper, MD5-hasher i parallelle tester og en test av `Bruker.clean()`. 1 er utsatt til `deferred-work.md` (parallell testmodus i CI), og resten er avvist med begrunnelse i triage-loggen i spec-en.
- Spec-en er `done`, og sprint-status har 1.1 på `review` og Epic 1 på `in-progress`.
- Pushet tidligere i økten: `arkitektur-epics-christian` og planleggingsfilene for 1.1. Koden i `844deb4` er ikke pushet. Ingen PR er opprettet, og `main` er urørt.

### Åpne punkter
- CI-workflowen har ikke kjørt. Det skjer først ved en PR mot `main`, og da må den sjekkes.
- Story 1.4: unikt emnenavn må sammenlignes med `casefold()` i Python, fordi SQLite `LOWER` ikke skiller store og små Æ, Ø og Å.
