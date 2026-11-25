---
title: 'Story 3.2: Regelen for feilbanken'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Feilbanken har en modell (`Feilbankrad`), men det finnes ingen regel som legger spørsmål inn i den og markerer dem som lært. Story 3.3 (levering) og Epic 4 trenger én funksjon å kalle (FR-21, FR-23, AD-2, AD-3, AD-5).

**Approach:** Ny `studier/services/feilbank.py` med `registrer_svar(sporsmal, riktig) -> Hendelse` som eneste sted som oppretter eller endrer `Feilbankrad`, og tester for alle fem hendelsene. Bare tjenestelag og tester.

- **Uten rad:** feil svar gir `get_or_create` med `riktige_pa_rad=0` og `lagt_i`. Riktig svar gir ingen rad og `ingen`.
- **I feilbanken (`laert_tidspunkt IS NULL`):** riktig svar gir telleren +1 og `opp`. Når telleren når 2, settes `laert_tidspunkt` og hendelsen er `laert`. Feil svar gir telleren 0 og `nullstilt`.
- **Lært:** feil svar åpner den samme raden igjen med `laert_tidspunkt=None` og telleren 0, og gir `nullstilt`. Riktig svar gir `ingen`, og raden endres ikke.
- Høyst én rad per spørsmål, og ingen rad slettes (AD-3). Like spørsmålstekster i to quizer er to spørsmål med hver sin rad (AD-5).
- En test sjekker at ingen annen fil i appene (utenom `studier/services/feilbank.py`, migreringer og tester) lager eller endrer `Feilbankrad`.

</frozen-after-approval>

## Implementation Notes

- **Kortvei (oneshot):** implementert direkte i hovedøkten, uten implementeringssubagent.
- **`studier/services/feilbank.py`:** `registrer_svar(sporsmal, *, riktig) -> Hendelse` i `transaction.atomic()`.
  - Eksisterende rad hentes med `select_for_update()`, som er uten virkning på SQLite.
  - Ny rad lages med `get_or_create`.
  - `riktig` er bare et nøkkelordsargument, så sant og usant ikke byttes om i `lever_okt` (review).
- **Tester:** 14 tester i `studier/tests/test_feilbank.py`.
  - De fem hendelsene og sekvensen feil → riktig → feil → riktig → riktig.
  - At et spørsmål kan bli lært på nytt, og at lik tekst i to quizer gir to rader.
  - En kildesjekk som slår ut på skriving til `Feilbankrad` utenfor tjenesten, men slipper lesing. Mønsteret har en egen positiv og negativ kontroll.
- **Verifisert:** ruff, `makemigrations --check` og 367 tester grønne, 1 hoppet over.

## Review Triage Log

B = Blind Hunter (det eneste laget på kortveien). Pass 1, 25.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | Kildesjekken ser ikke skriving via `hent_egen`/`egne` med `save()` på en senere linje, `_default_manager` eller rå SQL | low | Stemmer, men en tekstsjekk kan aldri fange alt. `egne(...).update(` fanges nå. Resten ville krevd AST-analyse | avvist |
| B2 | Kildesjekken stopper også lesing, som Epic 4 og 5 trenger | medium | Bekreftet: `Feilbankrad\.objects` traff også `.filter(...).count()`. Mønsteret ser nå bare på skrivekall | patch |
| B3 | Kildesjekken mangler mappesjekk og positiv kontroll | low | Direkte rettelse: `is_dir()` per app og en test med linjer som skal og ikke skal treffe | patch |
| B4 | App-listen er hardkodet | low | Fire apper, og nye apper er ikke planlagt. Ingen skade nå | avvist |
| B5 | Ingen test for å bli lært på nytt | low | Kjerneregelen i FR-23. Direkte testtillegg | patch |
| B6 | Grenen for samtidig opprettelse kan ikke nås på SQLite, og kommentaren sier noe annet | low | Kommentaren er rettet. Grenen beholdes for databaser med radlåser | patch (kommentar) |
| B7 | `riktig` er posisjonelt og kan byttes om | low | Direkte rettelse: nøkkelordsargument | patch |
| B8 | Docstringen mangler verb, og returtypen mangler | low | Direkte rettelse | patch |
| B9 | «Kalles bare fra `lever_okt`» er ikke håndhevet | medium | `lever_okt` kommer i 3.3. En kildesjekk for kall til `registrer_svar` hører hjemme der | defer |
| B10 | `laert_tidspunkt` sjekkes bare med `assertIsNotNone` | low | Tidspunktet er `timezone.now()`, og ingen kode bruker verdien ennå | avvist |
| B11 | `_sporsmal` gjentar `fabrikk.py` | low | Ti linjer i én testfil. Ingen skade | avvist |
| B12 | `test_alle_fem_hendelsene_dekkes` er overflødig | low | Skadeløs. Sekvenstesten dekker rekkefølgen | avvist |
