# Manuell test, Christian

## 2026-11-26 kl. 15:21 — crbull

### Oppgave
Hente siste `main`, sette opp appen lokalt og gjennomføre en manuell testøkt av kjerneflyten. Funnene skulle føres i Christians fil for testtilbakemeldinger.

### Plan
- `git pull` og `uv sync` (nye avhengigheter: playwright, axe-playwright-python, greenlet).
- `migrate` og `seed_testdata`, så `runserver`. Testmodus satt på i lokal `.env` (`TESTMODUS=1`), så ingen KI-kall kostet noe.
- Brukeren testet i nettleseren og beskrev funnene. Funnene ble ført etter malen i [manuell-test/README.md](../../_bmad-output/implementation-artifacts/manuell-test/README.md).

### Resultat
- `main` fast-forwardet fra `d9ab386` til `1e7771b` (story 6.3–6.5 og manuell-test-strukturen).
- Fem funn ført i [test_feedback_christian.md](../../_bmad-output/implementation-artifacts/manuell-test/test_feedback_christian.md), commit `ac05bf7`:
  - CHR-01 (S3, mindre): «Fortsett der du slapp» viser alle påbegynte forsøk øverst og blir rotete. Forslag: én sammenslått boks med `<details>`.
  - CHR-02 (S4, kosmetisk): «I feilbanken» bør være «Spørsmål i feilbanken».
  - CHR-03 (S12, mindre): når «Øv på feil» er ferdig, bør man få tre valg: tilbake til emnet, øv på feil igjen og avslutt til forsiden.
  - CHR-04 (S4, mindre): emnesiden mangler en underoverskrift (h2) over notatene og quizene.
  - CHR-05 (S4, kosmetisk): «Gi nytt navn» tar for mye plass.
- Ingen kodeendringer. Lokal `.env` har nå `TESTMODUS=1` (ignorert av git).

### Åpne punkter
- CHR-01 til CHR-05 er åpne. Gruppa avgjør hvilke som rettes før levering. De som ikke rettes, får status «avvist» eller «åpent punkt» i fila.
- CHR-03: avklar om «Tilbake til notatet» skal erstattes eller stå i tillegg, og om S11 skal få de samme valgene.
- Nettleseren mangler i raden for testøkta i test_feedback_christian.md.
