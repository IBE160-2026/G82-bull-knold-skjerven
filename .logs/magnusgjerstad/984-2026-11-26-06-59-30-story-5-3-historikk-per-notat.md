# Story 5.3: Historikk per notat

## 2026-11-26 kl. 06:59 — MagnusGjerstad

### Oppgave
Hente siste status fra `main` og fortsette med story 5.3: historikken med de leverte forsøkene på notatsiden (S7), slik at studenten ser om hen blir bedre.

### Plan
- `git pull` på `main` (`f62315a`). Der lå storyene 2.4–5.2 fra Christian og fra Magnus på en annen maskin, og 519 tester var grønne.
- Laget branchen `story-5-3-historikk-per-notat` fra `main`.
- `bmad-build` med [epic-5-context.md](../../_bmad-output/implementation-artifacts/epic-5-context.md) og spec 5.2.
  - Spec: [spec-5-3-historikk-per-notat.md](../../_bmad-output/implementation-artifacts/spec-5-3-historikk-per-notat.md).
  - Workflowen valgte den korte veien (`oneshot`): én spec, implementering i hovedøkten og review med én reviewer (Blind Hunter).
  - Beslutninger:
    - Datoen viser klokkeslett, så flere forsøk samme dag kan skilles.
    - Quiz-kolonnen har samme tekst som quizkortet («Middels, 10 spørsmål»).
    - I tabellen er datoen lenken. På mobil er hele kortet én lenke.

### Resultat
- Commit `0ad6a3e` på `story-5-3-historikk-per-notat`, ikke pushet.
- **`studier/views.py` (`notat`):**
  - Historikken er `egne(Okt, …)` med leverte forsøk, sortert nyeste først.
  - Quizen hentes fra quizkortene, så det blir ingen ekstra spørring per rad.
- **`templates/studier/notat.html`:** seksjonen «Historikk» nederst.
  - Under `md`: kort med skilletegn for skjermleser.
  - Fra `md`: en `<table>` med `<caption>`, `<th scope="col">` og datoen som `<th scope="row">`.
  - Uten forsøk: «Ingen forsøk ennå. Ta en quiz for å se historikken.»
- **`static/css/app.css`:** bygget på nytt for `md:hidden`, `md:table` og `font-normal`.
- **Tester:** `studier/tests/test_historikk.py` har 10 tester. I tillegg teller `test_ta_pa_nytt` nå bare quizkortene, fordi historikken gjentar quizteksten.
- **Review:** 9 funn. 4 ble rettet (quizen hentes ikke to ganger, radoverskrift og to tester), og 5 ble avvist med begrunnelse i spec-en. Ingenting utsatt.
- **Verifisert:** ruff, `makemigrations --check` og 529 tester grønne (1 hoppet over til `ki/mock/` finnes).
- **Sprint-status:** `5-3: review`.
- **Løst punkt fra 4.1** (står i Christians `issues.md`): historikken viser ikke øvingsøkter. Dette er testet.

### Åpne punkter
- Historikken på S7 er ikke sjekket i nettleser (360 px med kort, tabell fra `md`, skjermleser i tabellen).
