# Story 5.2: dekningsgrad per emne

## 2026-11-25 kl. 21:51 — magnusgjerstad

### Oppgave
Brukeren spurte hvorfor 5.2 ikke var neste. Jeg hadde valgt den bort fordi den er merket «kan kuttes». Deretter ba brukeren om å implementere, committe og pushe 5.2.

### Plan
- Spec: [spec-5-2-dekningsgrad-per-emne.md](../../_bmad-output/implementation-artifacts/spec-5-2-dekningsgrad-per-emne.md). «Implementer, committ og push» ble tatt som godkjenning.
- bmad-build: underagent for implementasjonen, og Blind Hunter, Edge Case Hunter og Verification Gap på Opus.

### Resultat
- **Commit dd975ec.**
- **`services/dekningsgrad`:**
  - `for_notater` (2 spørringer for alle notater), `for_emner` (3) og `snitt` (snittet av notatene med quiz).
  - `Dekning.har_quiz`.
  - `for_notat` bruker `for_notater`.
- **`feilbank.antall_apne_per_notat`:** 1 spørring, med samme utvalg som `apne_rader`.
- **S4:**
  - Tallflisene «Dekningsgrad» og «I feilbanken» som `<dl>`.
  - Notatkortene med stolpe og «Dekningsgrad N %» eller «Ingen quiz», og «N i feilbanken».
- **S3:** emnekortene med stolpe og «Dekningsgrad N %», «Ingen notater» eller «Ingen dekningsgrad», inne i lenken.
- **Review:** 14 funn.
  - Rettet:
    - en test for et notat med quiz på 0 %;
    - S4 regnet ut alt to ganger;
    - skilletegn for skjermleser;
    - `<dl>` på flisene;
    - faste verdier i testen mot S7.
  - Ett punkt ble avvist etter at underagenten pekte på spec-en: «0 notater, Ingen notater» på et tomt emne.
- **Verifisert:** ruff, `makemigrations --check` og 519 tester grønne, 1 hoppet over. Ikke kjørt i nettleser.
- **`sprint-status.yaml`:** 5.2 står som `review`.

### Åpne punkter
- S3 og S4 er ikke sjekket i nettleser: 360 px, flisene under hverandre, og skjermleser på kortene.
