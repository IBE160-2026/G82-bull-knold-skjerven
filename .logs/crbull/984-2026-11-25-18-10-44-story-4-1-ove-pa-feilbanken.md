# Story 4.1: øve på feilbanken

## 2026-11-25 kl. 18:10 — crbull

### Oppgave
Bygge story 4.1 med bmad-build: studenten kan øve på notatets feilbank i en egen øvingsøkt (`type=oving`). Øvingen startes fra «Øv på feil (N)» på S7 og S11, og S9 og S10 gjenbrukes med terrakotta-aksent. Påbegynte øvingsøkter står i «Fortsett der du slapp» på S3.

### Plan
- Epic 4-konteksten kompilert av en subagent: [epic-4-context.md](../../_bmad-output/implementation-artifacts/epic-4-context.md).
- Spec: [spec-4-1-ove-pa-feilbanken.md](../../_bmad-output/implementation-artifacts/spec-4-1-ove-pa-feilbanken.md), ca. 2300 tokens. Beholdt hel.
- Christians avgjørelser:
  - Raden på S3 heter «Øv på feil, M spørsmål», med lenken «Fortsett øvingen».
  - «Lever» virker allerede for øving med uendret `lever_okt`. S11 vises uten quizknappen, og S12-visningen kommer i 4.2.
- Sonnet implementerte og fikk rettelsene fra reviewen tilbake. Tre reviewere kjørte på Opus.

### Resultat
- Commit `8d4f2a2` på `main`.
  - `start_eller_fortsett_okt(quiz=None, *, notat=None)` lager eller henter notatets påbegynte øving. Innholdet er de åpne feilbankradene, sortert på `opprettet` og låst ved start. Ny `apne_rader(notat)` i `feilbank.py`.
  - Ny `ov_pa_feil` (POST `notater/<pk>/ov/`) og partialen `_ov_pa_feil.html` på S7 og S11. Knappen har tre tilstander: «Øv på feil (N)», «Fortsett» med fremdrift, og låst med «Ingen spørsmål i feilbanken».
  - S9 og S10: h1 «Øv på feil» og `.ovemodus` (terrakotta).
  - S11: quizskjemaet skjules for øvingsøkter, så siden ikke gir 500.
  - S3: øvingsøkter står i boksen.
  - `app.css` er bygd på nytt med Tailwind 4.3.5 via `npx`. Fem klasser som malene alt brukte, kom med, fordi den forrige `app.css` manglet dem.
  - Nye tester i `studier/tests/test_oving.py`.
- Review, pass 1: 27 funn.
  - 17 patcher, gruppert til 12 rettelser: sortering og eiersjekk i `apne_rader`, logglinje og docstring, layout og `aria-describedby` på S11 (to «Fortsett»), og 9 tester som manglet eller var for svake.
  - 10 avvist.
  - Ingenting utsatt.
- Verifisert: ruff, `makemigrations --check` og 443 tester grønne, 1 hoppet over. Ikke kjørt i nettleser.
- To punkter fra tidligere logger er lukket: «Ta på nytt» skjules for øvingsøkter, og øvingsøkter står på S3.
- `sprint-status.yaml`: 4.1 står som `review`, og epic 4 som `in-progress`.

### Åpne punkter
- S7, S9, S10 og S11 i øvemodus er ikke sjekket i nettleser (360 px, tastatur, skjermleser, terrakotta på knapper og fremdrift).
- Story 5.3: historikken skal ikke vise øvingsøkter (krav i 4.1, men historikken finnes ikke ennå).
- Story 4.3: `apne_rader` og innholdet i nye økter må utelate meldte spørsmål (`ikke_meldt()`).
