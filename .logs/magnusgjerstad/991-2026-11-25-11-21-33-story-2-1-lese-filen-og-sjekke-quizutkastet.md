# Story 2.1: Lese filen og sjekke quizutkastet

## 2026-11-25 kl. 11:21 — MagnusGjerstad

### Oppgave
Starte Epic 2 med story 2.1. `ki` skal kunne lese en notatfil og sjekke et svar fra modellen mot quizformatet, og prosjektet trenger fem testdokumenter som story 2.2, 6.1 og 6.4 bygger på.

### Plan
- Stoppet utviklingsserveren fra nettlesertesten av 1.6. Funnene derfra står i 1.6-loggen ([992](992-2026-11-25-07-57-55-story-1-6-slette-emne.md)).
- Sjekket origin: ingen andre har brancher for Epic 2.
- Laget `story-2-1-lese-filen-og-sjekke-quizutkastet` fra `main` (`d304f54`). Den er uavhengig av 1.6, som ikke er merget ennå.
- `bmad-build`:
  - Epic-konteksten ble samlet i [epic-2-context.md](../../_bmad-output/implementation-artifacts/epic-2-context.md).
  - Spec: [spec-2-1-lese-filen-og-sjekke-quizutkastet.md](../../_bmad-output/implementation-artifacts/spec-2-1-lese-filen-og-sjekke-quizutkastet.md).
  - Beslutninger 25.11:
    - Gruppa lager testdokumentene selv, med lisens CC BY 4.0.
    - Den skannede PDF-en simuleres.
    - Spec-en beholdes som én story (ca. 2200 tokens).
  - Implementert av en subagent. Deretter review i tre lag og rettelser.

### Resultat
- Commit `01df4ad` på `story-2-1-lese-filen-og-sjekke-quizutkastet`, ikke pushet.
- **Kode i `ki`:**
  - `ki/feil.py`: `KIFeil` med de seks kodene fra AD-10.
  - `ki/fil.py`: `les_fil` og `Innhold`.
    - En PDF returneres hel.
    - Fra en DOCX hentes avsnittene.
    - En TXT leses som UTF-8 med cp1252 som reserve.
    - En fil som mangler gir `api_feil`, og en fil uten tekst gir `for_lite_innhold`.
  - `ki/format.py`: `sjekk` og `QuizUtkast`. Hver formatfeil i FR-13 gir `KIFeil("format")`.
  - `ki/__init__.py` re-eksporterer alt.
- **Testdokumenter i `testdokumenter/`, laget av `scripts/lag_testdokumenter.py`:**
  - Tekst-PDF om HTML, 10 sider.
  - Lysbilde-PDF om CSS-layout, 11 liggende sider.
  - Simulert skannet PDF om HTTP, 2 sider uten tekstlag.
  - DOCX om universell utforming.
  - TXT på engelsk om JavaScript og DOM.
  - `KILDER.md` oppgir kilde og lisens.
  - Skriptet kjøres med `uv run --with reportlab==5.1.1 --with pillow==13.0.0`, så `uv.lock` er uendret. Det gir like filer hver gang, også på et annet OS.
- **Review:** 29 funn. 13 ble rettet, blant annet:
  - DOCX-hashen var avhengig av OS-et.
  - DOCX-fila ble lest to ganger.
  - Dypt nøstet JSON ga feil type unntak.
  - Det manglet tester for æøå i UTF-8, for egenskapene til testdokumentene og for at mellomrom fjernes.

  16 ble avvist med begrunnelse i triage-loggen, og ingen ble utsatt.
- **Verifisert:** ruff check og format, `makemigrations --check` og 175 tester er grønne (39 i `ki`).
- **Sprint-status:** `epic-2: in-progress`, `2-1: review`. Spec-en er `done`.
- **Lukket punkt** i `issues.md`: hvilke testdokumenter som kan brukes uten å bryte opphavsretten.

### Åpne punkter
- Story 2.2: sjekk at den skannede PDF-en (2 sider) og lysbilde-PDF-en gir 30 gyldige spørsmål per nivå. Ellers må testdokumentene få mer innhold, og da endres hashene.
- Story 2.3/2.4: `les_fil` godtar en tom PDF eller en fil som ikke er PDF. Opplastingen eller `leser`-steget må validere den.
- `les_fil` leser bare avsnittene i en DOCX. Tekst i tabeller, topptekster og tekstbokser kommer ikke med i quizen.
