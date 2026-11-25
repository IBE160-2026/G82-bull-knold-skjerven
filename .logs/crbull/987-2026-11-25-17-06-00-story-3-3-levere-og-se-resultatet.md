# Story 3.3: levere og se resultatet

## 2026-11-25 kl. 17:06 — crbull

### Oppgave
Bygge story 3.3 med bmad-build: levere quizen fra S10, se poengsummen og riktig/feil per spørsmål på S11 uten fasit, og la feilsvarene havne i feilbanken. Samle opp de utsatte punktene fra 3.1 og 3.2 om leverte økter ([3.2-logg](988-2026-11-25-16-48-28-story-3-2-regelen-for-feilbanken.md)).

### Plan
- Spec: [spec-3-3-levere-og-se-resultatet.md](../../_bmad-output/implementation-artifacts/spec-3-3-levere-og-se-resultatet.md). Godkjent med omtrent 2500 tokens.
- Første story der implementeringssubagenten kjørte på Sonnet (via `_bmad/custom/bmad-build.user.toml`). Tre reviewere kjørte på Opus.

### Resultat
- Commit `d7acce5` på `main` (ikke pushet).
  - `lever_okt` (AD-18) og `fasit_synlig`.
  - «Lever» på S10, med låst knapp og tekst når spørsmål mangler.
  - S11 med poengsum, rader og fasit bare for lærte spørsmål.
  - S9 og `steg` håndterer leverte økter.
  - En kildesjekk sørger for at `registrer_svar` bare kalles fra `lever_okt`.
- Review, pass 1: 25 funn.
  - 4 patcher: S10 bruker `UbesvarteSporsmal.nr`, docstring, og tester for gammel S8-fane med levert og påbegynt forsøk og for levering med utdatert objekt.
  - 1 produktspørsmål utsatt i `deferred-work.md`.
  - Resten er avvist med begrunnelse.
- Verifisert: ruff, `makemigrations --check` og 393 tester grønne, 1 hoppet over. Ikke kjørt i nettleser.
- Lukket punktene fra 3.1 (leverte økter i `steg` og S9) og 3.2 (kildesjekk for `registrer_svar`).
- `sprint-status.yaml`: 3.3 står som `review`.

### Åpne punkter
- ~~Produktspørsmål før 3.4~~ Avgjort samme dag: Christian valgte alternativ 1. «N spørsmål er lagt i feilbanken» teller bare `lagt_i`, altså spørsmål som legges i feilbanken for første gang. Lærte spørsmål som kommer tilbake (`nullstilt`), telles ikke. Punktet i `deferred-work.md` trenger ingen kodeendring.
- S10 og S11 er ikke sjekket i nettleser (tastatur, 360 px).
