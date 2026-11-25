# Story 2.4: lage quiz med fremdrift

## 2026-11-25 kl. 15:11 — crbull

### Oppgave
Bygge story 2.4 med bmad-build: skjema for ny quiz på Notatsiden (S7), genereringsjobben fra AD-9 og Generering (S8) med tre fremdriftssteg, slik at studenten ser hvor genereringen er og ikke lager to quizer ved et uhell.

### Plan
- `/bmad-build` var ikke lastet, fordi VS Code var åpnet på `c:\IBE160`. Arbeidsflyten ble kjørt manuelt via `_bmad/scripts/render_skill.py`.
- Spec: [spec-2-4-lage-quiz-med-fremdrift.md](../../_bmad-output/implementation-artifacts/spec-2-4-lage-quiz-med-fremdrift.md). Den ble godkjent med omtrent 2700 tokens, over grensen på 1600, etter valg.
- En subagent implementerte. Tre subagenter gjorde review (Blind Hunter, Edge Case Hunter, Verification Gap). Etterpå kom patcher og ny verifisering.
- Branch `story-2-4-lage-quiz-med-fremdrift` fra oppdatert `main`.

### Resultat
- Commit `f8ec5b2` på `story-2-4-lage-quiz-med-fremdrift` (ikke pushet).
  - Ny `studier/services/generering.py`: `aktiv_jobb`, `opprett_jobb`, `kjor_steg`, `generer_synkront`.
  - S7-skjema og quizkort i `notat.html`. S8 i `jobb.html`, `_steg.html` og `_fremdrift.html`.
  - Rutene `/jobber/<id>/` og `/jobber/<id>/steg/`. `NyQuizForm`, nye feiltekster og `hx-headers` med CSRF på `<body>`.
- Review, pass 1: 21 funn. 4 ble rettet som patch:
  - live-regionen byttes bare når statusen endres
  - test for uventet unntak i `kjor_steg`
  - gjenstående tid regnes ut etter `les_fil`
  - SQLite-kommentaren i `opprett_jobb`

  1 funn var et intent_gap: S8-teksten lovet at fanen kunne lukkes. Etter brukerens valg ble den «Dette kan ta opptil to minutter. Hold fanen åpen til quizen er klar.», og koden ble beholdt. Resten ble avvist med begrunnelse i triageloggen i spec-en. Ingenting ble utsatt.
- Verifisert:
  - ruff, `makemigrations --check` og 288 tester grønne (1 hoppet over, `EkteMockfilerTest`).
  - Headless Edge via CDP mot en midlertidig server (egen database, media og mock-mappe, testmodus tvunget). S7 → S8 → S7 med alle tre stegene og quizkortet, `#fremdrift` byttet én gang per statusendring, ingen konsollfeil.
- `sprint-status.yaml`: 2.4 står som `review`.

### Åpne punkter
- S8 er ikke sjekket manuelt med bare tastatur og skjermleser (nettlesertesten var automatisk).
- Story 2.5: S8 stopper stille ved 500, nettfeil eller utløpt økt, og notat eller jobb slettet underveis gir 500 på `/steg/`. Avvist i 2.4 fordi sluttfragmentet og feilhåndteringen hører til 2.5.
- CDP-skriptet fikk ikke sendt innloggingsskjemaet (ingen POST nådde serveren). Det er ikke undersøkt om dette er en feil i siden eller i skriptet.
