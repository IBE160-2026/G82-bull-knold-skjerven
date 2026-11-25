# Story 2.6: flere quizer per notat

## 2026-11-25 kl. 16:07 — crbull

### Oppgave
Bygge story 2.6 med bmad-build, direkte på `main`: flere quizer per notat på S7. Det er siste story i Epic 2. Bygger på 2.4 og 2.5 ([2.5-logg](991-2026-11-25-15-53-24-story-2-5-feil-timeout-og-prov-igjen.md)).

### Plan
- Spec: [spec-2-6-flere-quizer-per-notat.md](../../_bmad-output/implementation-artifacts/spec-2-6-flere-quizer-per-notat.md). Omtrent 1400 tokens.
- Det meste fantes fra 2.4. Det som manglet, var testmodus-merknaden på kortet og tester for AC-ene.
- Christian bestemte at modellnavnet skal stå i metalinjen på kortet, mens merket fortsatt er «Laget av KI».
- En subagent implementerte. Tre subagenter gjorde review, og etterpå kom en patch og ny verifisering.

### Resultat
- Commit `127e868` på `main` (ikke pushet).
  - Merknaden «Testmodus: denne quizen er laget fra et forhåndslagret testdokument, ikke fra filen din.» står på kort med `forhandslagret=True`.
  - Metalinjen er «dato · modellnavn» fra `ki.visningsnavn(quiz.modell)`.
  - 9 nye tester i `studier/tests/test_flere_quizer.py`.
- Review, pass 1: 13 funn. Én patch: testen for at testmodus er av patchet feil sted, og alle tre reviewerne fant det. Resten er avvist med begrunnelse. Ingenting er utsatt.
- Verifisert: ruff, `makemigrations --check` og 315 tester grønne (1 hoppet over). Testen feiler hvis merknaden gjøres avhengig av testmodus.
- `sprint-status.yaml`: 2.6 står som `review`. Alle stories i Epic 2 er nå `done` eller `review`, og 2.2 venter fortsatt på mock-filene.

### Åpne punkter
Ingen.
