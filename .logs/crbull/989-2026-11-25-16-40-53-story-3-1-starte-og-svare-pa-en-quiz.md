# Story 3.1: starte og svare på en quiz

## 2026-11-25 kl. 16:40 — crbull

### Oppgave
Starte Epic 3 med story 3.1: ta en quiz ett spørsmål om gangen med Forrige og Neste, der svarene lagres for hvert steg. Bygget med bmad-build direkte på `main`. Christian ba også om at subagentbruken skulle ned (`/usage`).

### Plan
- Epic 3-konteksten ble kompilert av en subagent: [epic-3-context.md](../../_bmad-output/implementation-artifacts/epic-3-context.md).
- Spec: [spec-3-1-starte-og-svare-pa-en-quiz.md](../../_bmad-output/implementation-artifacts/spec-3-1-starte-og-svare-pa-en-quiz.md). Godkjent med omtrent 3100 tokens. Christian bestemte tre ting:
  - et enkelt S10-skall
  - knappeteksten «Ta quiz»
  - CSS bygges på nytt med en midlertidig Tailwind 4.3.5
- En subagent implementerte. Tre subagenter gjorde review, og etterpå kom patcher og ny verifisering.
- Bruk: implementeringssubagenten i bmad-build kjører fra nå på Sonnet via den personlige overstyringen `_bmad/custom/bmad-build.user.toml` (gitignorert). Reviewerne beholder øktens modell, slik step-04 krever. 3.1 ble implementert på Opus, fordi agenten var startet før endringen.

### Resultat
- Commit `c49cb5e` på `main`.
  - `studier/services/okter.py`: `start_eller_fortsett_okt`, `lagre_svar` og `forste_ubesvarte`.
  - S9: KI-merke, reiserute, flashcard og radioknapper, og Forrige/Neste/«Se over og lever» som POST.
  - S10-skall.
  - «Ta quiz» på quizkortene, og `steg` åpner quizen på nr 1.
  - `app.css` er bygget på nytt.
- Review, pass 1: 23 funn.
  - 4 patcher: «Se over og lever» lagrer svaret, og nye tester for `autofocus`, CSRF og språkvarianter.
  - 3 utsatt til 3.3 i `deferred-work.md`: leverte økter i `steg` og S9, og en view-test for `OktErLevert`.
  - Resten er avvist med begrunnelse.
- Verifisert:
  - ruff, `makemigrations --check` og 353 tester grønne, 1 hoppet over.
  - Subagenten kjørte S9 i headless Edge: fokus etter Neste, ingen vannrett rulling ved 360/320 px, og knapper i full bredde under `md`.
- `sprint-status.yaml`: Epic 3 er `in-progress`, og 3.1 står som `review`.

### Åpne punkter
- Story 3.3 må ta de tre utsatte punktene om leverte økter (se `deferred-work.md`).
- Den skjulte standardknappen for Enter på S9 er bare kontrollert i Edge, ikke i Safari.
