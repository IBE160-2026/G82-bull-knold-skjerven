---
title: 'Story 1.5: Gi emne nytt navn'
type: 'feature'
created: '2026-11-24'
status: 'draft'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'TBD'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Studenten kan opprette emner, men kan ikke endre navnet på et emne etterpå (FR-5). Feil navn må kunne rettes uten å miste notater, quizer eller historikk.

**Approach:** Legg et skjema på S4 med knappen «Gi nytt navn». Skjemaet viser dagens navn og har knappen «Lagre navn». Samme feilmeldinger og samme regler som ved nytt emne. Lagring endrer bare navnet.

## Boundaries & Constraints

**Always:**
- Samme navneregler som ved nytt emne: trimming, tomt navn, høyst 100 tegn og unikt per eier uten å skille store og små bokstaver. Æ, Ø og Å regnes likt. Feilmeldingene er de samme som i `farequiz/feilmeldinger.py`.
- Det gamle navnet på emnet regnes ikke som duplikat. Emnet kan få samme navn med ny skrivemåte, for eksempel «html» til «HTML».
- Lagring skjer i `studier/services/emner.py` (`gi_nytt_navn`), som validerer navnet selv, samme som `opprett_emne`.
- Emnet hentes med `hent_egen`. Andres emne gir «Fant ikke siden», 404.
- Notater, quizer og historikk er uendret. Det testes.
- Feil vises ved feltet med `aria-describedby`, og fokus flyttes dit.
- Skjemaet virker uten JavaScript. Ingen vannrett rulling på 320 px.

**Never:**
- Ingen sletting (1.6) og ingen egen side for navnbyttet. Skjemaet ligger på S4.
- Ingen nye migreringer.
- Ingen JavaScript.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Vis skjema | Eier åpner S4 | Skjemaet «Gi nytt navn» med dagens navn i feltet | N/A |
| Nytt navn | «Kjemi» til «Biologi» | Navnet endres. Brukeren sendes til S4 med det nye navnet | N/A |
| Ny skrivemåte | «html» til «HTML» | Navnet endres. Ikke duplikat av seg selv | N/A |
| Tomt navn | Bare mellomrom | Navnet beholdes. «Navnet kan ikke være tomt.» | Feilmelding ved feltet, fokus dit |
| Navn tatt | «Biologi» når et annet emne heter det | Navnet beholdes. «Du har allerede et emne med dette navnet.» | Feilmelding ved feltet, fokus dit |
| For langt navn | 101 tegn | Navnet beholdes. «Navnet kan være høyst 100 tegn.» | Feilmelding ved feltet, fokus dit |
| Innhold uendret | Navn endres, emnet har notater | Notater og quizer finnes fortsatt | N/A |
| Andres emne | Innlogget, `pk` tilhører en annen bruker | «Fant ikke siden», 404 | 404 |
| Utlogget | POST uten innlogging | Sendt til innlogging | N/A |

## Code Map

- `studier/services/emner.py` -- `gi_nytt_navn(emne, navn)`: trimmer, validerer og lagrer. Samme validering som `opprett_emne`, med `ValueError` for ugyldig navn.
- `studier/forms.py` -- `EmneForm` tar et valgfritt `emne`-argument. Med `emne` utelates emnet selv i duplikatsjekken.
- `studier/views.py` -- ny `gi_nytt_navn_visning` for POST på `/emner/<pk>/navn/`. Bruker `hent_egen`. Ved feil vises S4 med skjemaet og feilmeldingen.
- `studier/urls.py` -- `emner/<int:pk>/navn/`, navn `studier:endre_navn`.
- `templates/studier/emne.html` -- skjemaet «Gi nytt navn» under «Last opp notat». Knappen er sekundær.
- `studier/tests/test_emner.py` -- tester for hver rad i I/O-matrisen.

## Tasks & Acceptance

**Execution:**
- [ ] `studier/services/emner.py` -- `gi_nytt_navn` med validering
- [ ] `studier/forms.py` -- `EmneForm` med valgfritt `emne`
- [ ] `studier/views.py` og `studier/urls.py` -- POST på `/emner/<pk>/navn/` med `hent_egen`
- [ ] `templates/studier/emne.html` -- skjema med feltet og knappen «Lagre navn»
- [ ] Tester etter I/O-matrisen, pluss en test for at notater og quizer er uendret

**Acceptance Criteria:**
- Gitt et emne, når eieren åpner S4, så står skjemaet med dagens navn og knappen «Lagre navn».
- Gitt et nytt, gyldig navn, når skjemaet sendes, så står det nye navnet på S4 og i Oversikt, og ingen data er slettet.
- Gitt et tomt, for langt eller tatt navn, når skjemaet sendes, så beholdes det gamle navnet og feilmeldingen står ved feltet med fokus.
- Gitt en annen brukers emne, når skjemaet sendes, så gir det 404.

## Implementation Notes

- Ingen implementasjon ennå. Dette er et utkast.
- Branchen starter fra `story-1-4-oversikt` (`92830e5`), fordi PR #5 og #6 ikke er merget ennå.

## Spec Change Log

## Design Notes

- **Skjemaet ligger på S4**, slik sprint-forslaget sier, og ikke på egen side.
- **Duplikatsjekken** ekskluderer emnet selv, slik at en ny skrivemåte av samme navn går.

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- expected: 0 funn
- `uv run python manage.py makemigrations --check --dry-run` -- expected: «No changes detected»
- `uv run python manage.py test` -- expected: alle tester grønne

**Manual checks:**
- `runserver`: gi et emne nytt navn, og sjekk at Oversikt oppdateres. Sjekk feilmeldinger og 320 px.
