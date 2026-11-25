# Story 3.5: fortsette der jeg slapp

## 2026-11-25 kl. 17:43 — crbull

### Oppgave
Bygge story 3.5 med bmad-build: boksen «Fortsett der du slapp» på Oversikt (S3), fremdrift og «Fortsett» på quizkortet (S7), og «Fortsett» på S11 når quizen har et påbegynt forsøk. Det siste var utsatt fra 3.4 ([3.4-logg](986-2026-11-25-17-24-07-story-3-4-ta-en-quiz-pa-nytt.md)).

### Plan
- Spec: [spec-3-5-fortsette-der-jeg-slapp.md](../../_bmad-output/implementation-artifacts/spec-3-5-fortsette-der-jeg-slapp.md). Godkjent med omtrent 2100 tokens (beholdt hel).
- Christians avgjørelse: «spørsmål N av M» har N = antall besvarte, men minst 1. Et forsøk uten svar viser «spørsmål 1 av 10».
- Sonnet implementerte og fikk rettelsene fra reviewen tilbake. Tre reviewere kjørte på Opus.

### Resultat
- Commit `53e0e78` på `main`.
  - `_fortsett_rader` i `farequiz/views.py` gir et fast antall spørringer.
  - Boksen på S3 står øverst og vises ikke uten påbegynte forsøk.
  - S7 viser «Påbegynt – spørsmål N av M» og «Fortsett».
  - S11 viser «Fortsett».
  - 15 nye tester i `studier/tests/test_fortsette.py`.
- Review, pass 1: 17 funn.
  - 13 patcher, gruppert til 9 rettelser: tester for sortering og ulike emner, paritet med `forste_ubesvarte`, `_boks`, positiv tilgangskontroll, `aria-describedby` med fremdrift, `egne()`, kommentarer og docstrings.
  - 4 avvist.
  - Ingenting utsatt.
- Verifisert: ruff, `makemigrations --check` og 421 tester grønne, 1 hoppet over. Ikke kjørt i nettleser.
- Lukket punktet fra 3.4 om at «Ta på nytt» på S11 skal følge «Fortsett»-regelen.
- `sprint-status.yaml`: 3.5 står som `review`. Alle storyene i epic 3 er nå bygget.

### Åpne punkter
- Epic 4: øvingsøkter (`type=oving`) skal også stå i «Fortsett der du slapp» (spec-en sier at Epic 4 legger dem til).
- S3- og S7-endringene er ikke sjekket i nettleser (tastatur, skjermleser, 360 px).
