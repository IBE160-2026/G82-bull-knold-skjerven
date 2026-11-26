# Story 6.4: KI-kvalitet og genereringstid

## 2026-11-26 kl. 12:50 — MagnusGjerstad

### Oppgave
Pushe 6.3 med PR og gå videre til neste story. 6.4 krever ekte modell med API-nøkkel, og den finnes ikke her. Magnus valgte «Bygg nå, kjør senere»: verktøyet bygges nå, og målingen og vurderingen gjøres senere med nøkkel.

### Plan
- **6.3:** pushet og laget PR #15. CI er grønn, og axe-steget kjørte 45 tester på GitHub.
- **Branch:** `story-6-4-ki-kvalitet-og-genereringstid`, laget fra 6.3-branchen (`4233d1e`), fordi PR #15 ikke er merget.
- **`bmad-build`** med [spec-6-4-ki-kvalitet-og-genereringstid.md](../../_bmad-output/implementation-artifacts/spec-6-4-ki-kvalitet-og-genereringstid.md).
- **Beslutning 26.11:** kvalitetskjøringen lager 10 spørsmål per quiz som standard, altså 150 spørsmål å vurdere. Tallet kan overstyres med `--antall`.
- **Gjennomføring:** en underagent implementerte. Deretter kom review i tre lag og rettelser fra samme underagent.

### Resultat
- **Commit:** `5517d85`, ikke pushet.
- **`ki/management/commands/maal_ki_kvalitet.py`:**
  - **Kjøring:** nekter i testmodus. Den kjører 5 dokumenter × 3 nivåer og 3 tidsmålinger med 30 spørsmål fra `html-struktur-og-semantikk.pdf`, alle med `timeout=300`.
  - **SM-4 og språk** sjekkes automatisk, og hver rad viser modell, stoppgrunn og feildetalj.
  - **Tid:** median og lengste tid, og lengste kvalitetskall. Rader over 120 s merkes.
  - **Vurdering:** én tabell per quiz for den manuelle vurderingen (SM-2).
  - **Valg:** `--antall`, `--runder`, `--modell`, `--effort` og `--ut`. Valgene sjekkes før noe kall.
  - **Rapporten** skrives til `_bmad-output/implementation-artifacts/ki-kvalitet/`.
- **`ki/generering.py`:** `RaattSvar.stoppgrunn`, så avkutting (`max_tokens`) kan skilles fra andre formatfeil.
- **`PromptVersjonTest`** låser `PROMPT_VERSJON` til prompten, skjemaet, nivåene, `effort` og oppgaveteksten.
- **[ki-kvalitet-6-4.md](../../_bmad-output/implementation-artifacts/ki-kvalitet-6-4.md):** mal for resultatet, med kommandoene øverst.
- **Review:** 21 funn. 14 er rettet og 7 avvist med begrunnelse. Ingenting er utsatt.
- **Verifisert:** ruff og `makemigrations --check` er rene. 591 tester er grønne, uten nettverkskall, og kommandoen nekter i testmodus.
- **Sprint-status:** `6-4: review`.

### Åpne punkter
- Kjør `maal_ki_kvalitet` med API-nøkkel og vurder spørsmålene manuelt (minst 90 % gode). Fyll ut `ki-kvalitet-6-4.md`, og commit rapporten sammen med malen.
- Sammenlign med Haiku og med en lavere `effort` (`--modell claude-haiku-5-5`, `--effort low`). Gjør valget for `effort`, `MAKS_TOKENS` og modell. Endres noe, økes `PROMPT_VERSJON`, og så kjøres `lag_mocksvar`, `seed_testdata` og testen med ny klone på nytt.
- Valget mellom hel PDF og uttrukket tekst må begrunnes i malen. Det finnes ikke noe valg for uttrukket tekst i kommandoen, og tokenbruken lagres ikke.
