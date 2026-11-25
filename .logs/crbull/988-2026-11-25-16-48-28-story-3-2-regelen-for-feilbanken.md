# Story 3.2: regelen for feilbanken

## 2026-11-25 kl. 16:48 — crbull

### Oppgave
Bygge story 3.2 med bmad-build: regelen som legger feilbesvarte spørsmål i feilbanken og markerer dem som lært etter to riktige svar på rad. Bare tjenestelag og tester. Bygger på 3.1 ([logg](989-2026-11-25-16-40-53-story-3-1-starte-og-svare-pa-en-quiz.md)).

### Plan
- Kortveien (oneshot) i bmad-build. Kravene var klare, ingenting kunne ikke angres, og endringen var liten. Derfor ble den implementert direkte i hovedøkten, uten implementeringssubagent, og bare Blind Hunter gjorde review. Det holder subagentbruken nede.
- Spec: [spec-3-2-regelen-for-feilbanken.md](../../_bmad-output/implementation-artifacts/spec-3-2-regelen-for-feilbanken.md).

### Resultat
- Commit `b12f41b` på `main` (ikke pushet).
  - `studier/services/feilbank.py` med `registrer_svar(sporsmal, *, riktig) -> Hendelse`.
  - 14 tester i `studier/tests/test_feilbank.py`: alle fem hendelsene, sekvensen, ny læring, spørsmålsidentitet og en kildesjekk mot skriving utenfor tjenesten.
- Review: 12 funn.
  - Rettet direkte: kildesjekken ser bare på skriving og har positiv kontroll, test for ny læring, nøkkelordsargument, kommentar og returtype.
  - Utsatt til 3.3 i `deferred-work.md`: håndhev at `registrer_svar` bare kalles fra `lever_okt`.
  - Resten er avvist med begrunnelse.
- Verifisert: ruff, `makemigrations --check` og 367 tester grønne, 1 hoppet over.
- `sprint-status.yaml`: 3.2 står som `review`.

### Åpne punkter
- Story 3.3: legg til en kildesjekk for at `registrer_svar` bare kalles fra `lever_okt` (`deferred-work.md`).
