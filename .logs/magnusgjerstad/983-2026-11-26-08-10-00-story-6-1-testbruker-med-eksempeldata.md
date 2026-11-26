# Story 6.1: Testbruker med eksempeldata

## 2026-11-26 kl. 08:10 — MagnusGjerstad

### Oppgave
Pushe story 5.3 og fortsette med neste story: en testbruker med ferdige data, slik at sensor ser dekningsgrad, historikk, feilbank og «Fortsett der du slapp» med en gang (FR-28).

### Plan
- **Story 5.3:**
  - Pushet `story-5-3-historikk-per-notat` og laget PR #12. CI er grønn.
  - Merge til `main` ble stoppet av sikkerhetssjekken, så PR-en venter på at Magnus merger den.
- **Branch:** `story-6-1-testbruker-med-eksempeldata` er laget fra 5.3-branchen, så `sprint-status.yaml` og loggene ikke får konflikt.
- **`bmad-build`:**
  - En subagent satte sammen [epic-6-context.md](../../_bmad-output/implementation-artifacts/epic-6-context.md).
  - Spec: [spec-6-1-testbruker-med-eksempeldata.md](../../_bmad-output/implementation-artifacts/spec-6-1-testbruker-med-eksempeldata.md).
  - Beslutninger 26.11:
    - Bygg nå, og kjør seed på ekte når `ki/mock/` finnes.
    - Innloggingen er `sensor@farequiz.no` med passordet `sensor123`.
    - Spec-en beholdes som én story (ca. 2050 tokens).
  - Implementert av en subagent. Deretter review i tre lag og rettelser.

### Resultat
- **Commit:** `dd9b833` på `story-6-1-testbruker-med-eksempeldata`, ikke pushet.
- **`manage.py seed_testdata`** (`studier/management/commands/seed_testdata.py`) går bare gjennom tjenestene og alltid i testmodus. Testbrukeren får emnet «Webutvikling» med tre notater:
  - **HTML-PDF:**
    - Quiz lett med 10 spørsmål. Den har to leverte forsøk (7 av 10 og 10 av 10) og en øving. Etter øvingen er spørsmål 8 og 9 lært, og 10 ligger fortsatt i feilbanken.
    - Quiz middels med et påbegynt forsøk, som gir «spørsmål 4 av 10».
  - **DOCX:** quiz vanskelig med ett levert forsøk, 6 av 10.
  - **TXT:** ingen quiz.
  - **Forhåndssjekk:** testdokumentene, manifestet, at shaene står i manifestet og nivåfilene sjekkes før noe slettes.
  - **Ny kjøring:** gir samme data. Emnene slettes, passordet settes på nytt og brukeren aktiveres.
- **Innlogging:** `kontoer/testbruker.py` er eneste sted den står i koden. S1 viser boksen «Testbruker» i testmodus, og README-en har avsnittet «Testbruker».
- **Avvik fra spec-teksten:**
  - Det påbegynte forsøket har 4 svar, ikke 3. Fremdriften viser antall svar, og 4 svar er det som gir «spørsmål 4 av 10» i akseptansekriteriet.
  - Avviket står i spec-en.
- **Review:** 21 funn.
  - Rettet:
    - forhåndssjekken, før noe slettes
    - aktivering av en deaktivert testbruker
    - nettverkstesten kjører nå med testmodus av
    - tester for `KIFeil` og forhåndssjekken
  - 10 er avvist med begrunnelse i spec-en. Ingenting er utsatt.
- **Verifisert:**
  - ruff, `makemigrations --check` og 548 tester er grønne (1 hoppet over til `ki/mock/` finnes).
  - Seed mot den lokale databasen stopper med en tydelig melding og endrer ingenting, fordi `ki/mock/` mangler.
- **Sprint-status:** `6-1: review`, med en kommentar om at seed må kjøres på ekte når mock-filene er committet. `epic-6` er `in-progress`.

### Åpne punkter
- Når `ki/mock/` er committet, må `seed_testdata` kjøres på ekte. Sjekk S3, S4 og S7 som testbrukeren før 6.1 settes til `done`.
- Avklar med Christian om «Påbegynt – spørsmål N av M» (S3 og S7) skal vise antall svar, slik den gjør i dag, eller spørsmålet du fortsetter på. Etter 4 svar står det «spørsmål 4 av 10», men du fortsetter på spørsmål 5.
