# Story 2.2: Generere med modellen eller mock-svar

## 2026-11-25 kl. 13:12 — MagnusGjerstad

### Oppgave
Neste story i Epic 2: `ki` skal kunne lage et quizsvar med Claude, eller fra lagrede mock-svar i testmodus. Kommandoen `lag_mocksvar` skal lage mock-svarene fra de fem testdokumentene.

### Plan
- Branch `story-2-2-generere-med-modellen-eller-mock-svar` fra `main` (`55e7ce4`).
- `bmad-build`, med epic-konteksten fra [epic-2-context.md](../../_bmad-output/implementation-artifacts/epic-2-context.md) og forrige spec (2.1).
  - Spec: [spec-2-2-generere-med-modellen-eller-mock-svar.md](../../_bmad-output/implementation-artifacts/spec-2-2-generere-med-modellen-eller-mock-svar.md).
  - Brukte API-referansen (claude-api) og den installerte `anthropic` 2.11.0 for parameterne og unntaksklassene.
  - Beslutninger 25.11:
    - Bygg nå og kjør `lag_mocksvar` senere med gruppas nøkkel, siden det ikke finnes noen nøkkel på denne maskinen.
    - Spec-en beholdes som én story (ca. 2400 tokens).
  - Implementert av en subagent. Deretter review i tre lag og rettelser.

### Resultat
- Commit `e837333` på `story-2-2-generere-med-modellen-eller-mock-svar`, ikke pushet.
- **`ki/generering.py`:** `generer`, `RaattSvar`, `visningsnavn` og `PROMPT_VERSJON = "1"`.
  - **Modellveien:** `KI_MODELL` (Sonnet 5.5), structured outputs, `effort: "medium"`, ingen nye forsøk i SDK-en (så fristen holder) og server-side fallback ved avslag.
  - Feilene gir kodene fra AD-10.
  - **Testmodus:** svaret slås opp i `ki/mock/manifest.json`, og de første N spørsmålene returneres.
- **`manage.py lag_mocksvar`:** 5 dokumenter × 3 nivåer × 30 spørsmål.
  - Ett nytt forsøk ved `format`, `timeout` og `api_feil`.
  - Ingenting skrives før alt er godkjent.
  - Varigheten per kall skrives ut.
- **README:** avsnitt om testmodus og mock-svar.
- **Review:** 27 funn. 14 ble rettet, 11 avvist og 2 utsatt til `deferred-work.md` (`max_tokens` og testen mot ekte `ki/mock/`). Blant rettelsene:
  - 408 og 504 gir `timeout`.
  - Alle SDK-feil blir `KIFeil`.
  - Kommandoen prøver på nytt etter forbigående feil.
  - Nye tester for ugyldig manifest og ugyldig mock-fil.
- **Verifisert:** ruff, `makemigrations --check` og 226 tester grønne (1 hoppet over til `ki/mock/` finnes). Modellveien er ikke prøvd mot ekte API.
- **Sprint-status:** `2-2: review`. Den står der til mock-filene er laget og committet.

### Åpne punkter
- Noen med gruppas API-nøkkel må kjøre `uv run python manage.py lag_mocksvar` og committe `ki/mock/`. Det er 15 kall med Sonnet 5.5, anslagsvis noen få dollar. Til da gir generering i testmodus `api_feil`, og story 2.2 står i `review`.
- Ved den første kjøringen må vi sjekke om noen kall ender med `max_tokens` (grensen er 16000), og notere varigheten mot 120 s.
