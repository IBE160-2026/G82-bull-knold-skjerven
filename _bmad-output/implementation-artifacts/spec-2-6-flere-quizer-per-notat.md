---
title: 'Story 2.6: Flere quizer per notat'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'c5524365280a374198d1b300ceebc232bc6d63b4'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** S7 lister allerede quizene, og «Lag ny quiz» virker (story 2.4). Men en quiz laget i testmodus fra en fil som ikke er et testdokument, ser ut som en quiz laget fra brukerens egen fil. Akseptansekriteriene for flere quizer per notat er heller ikke låst av tester (FR-11, FR-16, FR-27, UX-DR26).

**Approach:** Legg testmodus-merknaden på quizkortet når `Quiz.forhandslagret` er sann, og legg til tester for alle akseptansekriteriene i story 2.6.

## Boundaries & Constraints

**Always:**
- **Quizkort med `forhandslagret=True`:** under datoen står «Testmodus: denne quizen er laget fra et forhåndslagret testdokument, ikke fra filen din.» som tekst, ikke bare som ikon.
  - Teksten ligger i `farequiz/feilmeldinger.py`.
  - Merknaden står uansett om testmodus er på nå. Den følger quizen.
- **Beslutning 25.11 (Christian): modellnavnet står i metalinjen.** Merket er fortsatt «Laget av KI». Linjen under blir dato og modellnavn, for eksempel «25. november 2026 · Claude Sonnet 5.5». Navnet kommer fra `ki.visningsnavn(quiz.modell)`, aldri fra gjeldende innstilling (`KI_MODELL`).
- Kortene står nyeste først, hvert med nivå, antall spørsmål, dato og «Laget av KI». «Lag ny quiz» med samme skjema står under kortene (finnes fra 2.4).
- En ny quiz med samme nivå og antall som en eksisterende er lov og blir et eget kort. Ingen quiz endres eller slettes.
- Det finnes ingen knapp, lenke eller URL for å slette én enkelt quiz. Brødsmulene viser Oversikt › emne › notat.
- Andres notat gir «Fant ikke siden» (404) både ved GET og POST på `/notater/<id>/`.

**Never:**
- Ingen endring i `ki`, modellene, migreringene, genereringskjeden eller S8.
- Kortene blir ikke lenker (S9 kommer i Epic 3).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Flere quizer | tre quizer laget på ulike dager | Tre kort, nyeste først, hvert med nivå, antall, dato og «Laget av KI», over «Lag ny quiz» | N/A |
| Modellnavn fra quizen | `quiz.modell="claude-haiku-5-5"`, `KI_MODELL="claude-sonnet-5-5"` | Kortet viser «Claude Haiku 5.5», ikke Sonnet | N/A |
| Samme valg igjen | quiz middels/10 finnes, ny jobb middels/10 kjøres ferdig | To kort med middels/10, den første quizen er uendret | N/A |
| Forhåndslagret | `forhandslagret=True` på én av to quizer | Merknaden står bare på det kortet | N/A |
| Ikke forhåndslagret | `forhandslagret=False` | Ingen merknad | N/A |
| Ingen sletting | S7 med quizer | Ingen «Slett»-tekst og ingen lenke eller skjema mot en quiz-URL. `/quizer/<id>/slett/` finnes ikke (404) | N/A |
| Annens notat | GET og POST mot en annen brukers notat | Ingen jobb lages | 404, «Fant ikke siden» |

</frozen-after-approval>

## Code Map

- `templates/studier/notat.html` -- quizkortene (`{% if quizer %}`) og skjemaet. Merknaden legges under datoen i kortet.
- `studier/views.py` (`notat`) -- `quizer` er sortert `-opprettet, -pk` og har `antall_sporsmal`. Teksten for merknaden sendes i konteksten.
- `farequiz/feilmeldinger.py` -- ny tekst `TESTMODUS_FORHANDSLAGRET`.
- `ki.visningsnavn(modell)` -- gir «Claude Sonnet 5.5» fra `claude-sonnet-5-5` brukes i metalinjen.
- `studier/tests/test_generering.py` -- `GenereringTestCase`, `_raatt`, `generer_synkront`. `SiderTest` har mønster for S7-HTML.
- `templates/partials/brodsmuler.html` -- brødsmuler.

## Tasks & Acceptance

**Execution:**
- [x] `farequiz/feilmeldinger.py` -- `TESTMODUS_FORHANDSLAGRET`
- [x] `studier/views.py`, `templates/studier/notat.html` -- merknaden på kortet
- [x] `studier/tests/test_flere_quizer.py` -- én test per rad i matrisen, pluss brødsmulene

**Acceptance Criteria:**
- Gitt S7 med to quizer der én er forhåndslagret, når siden vises, så står merknaden bare på det kortet, og «Lag ny quiz» står under begge kortene.

## Implementation Notes

- **`notat`:** gjør quizene om til en liste og setter `quiz.modellnavn = ki.visningsnavn(quiz.modell)`. `TESTMODUS_FORHANDSLAGRET` sendes i konteksten.
- **Kortet:** metalinjen er «dato · modellnavn», og merknaden står som egen `<p>` under når `forhandslagret` er sann. Ingen nye CSS-klasser.
- **Tester:** 9 tester i `studier/tests/test_flere_quizer.py`. Testen for at testmodus er av patcher `farequiz.context_processors.er_testmodus` (review V1).
- **Verifisert:**
  - Hvis malen endres til `{% if testmodus and quiz.forhandslagret %}`, feiler testen, og endringen ble fjernet igjen etterpå.
  - ruff, `makemigrations --check` og 315 tester grønne, 1 hoppet over.

## Spec Change Log

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 25.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| V1 | `test_merknaden_folger_quizen_ogsa_nar_testmodus_er_av` patcher `ki.er_testmodus`, men kontekstprosessoren har sin egen referanse (`from ki import er_testmodus`), så testmodus er aldri av i testen | medium | Bekreftet: `farequiz/context_processors.py` importerer navnet, og `farequiz/tests_maler.py` patcher `farequiz.context_processors.er_testmodus`. Testen beviser ikke det den skal | patch |
| E1 | Samme som V1 | medium | Samme som V1 | patch |
| B1 | Samme som V1 | medium | Samme som V1 | patch |
| E2 | Tom `quiz.modell` gir en løs « · » | low | Kan ikke nås: `Quiz` lages bare fra `QuizUtkast`, og `sjekk` krever at `modell` ikke er tom. Fikstur-ID-er som `claude-test` finnes bare i tester | avvist |
| B2 | Tomme eller ukjente modell-ID-er vises rått | low | Samme som E2 | avvist |
| E3 | `re.search(...)` på `<main>` gir `AttributeError` i stedet for en tydelig feil | low | Bare testkvalitet. Testen feiler fortsatt hvis oppsettet endres | avvist |
| B3 | Kortregexen er avhengig av Tailwind-klasser | low | Samme mønster som resten av testene i repoet. Ingen funksjonell skade | avvist |
| B4 | «Ingen sletting» sjekker hele siden | low | Ingen planlagt funksjon på S7 bruker «slett». Testen feiler i så fall høylytt og kan snevres inn da | avvist |
| B5 | Kjøreløkken finnes to steder | low | Fem linjer i én test. Ingen skade | avvist |
| B6 | Merknaden har ikke `role="note"` eller visuell markering | low | Spec-en krever tekst, og teksten starter med «Testmodus:». Ny markering krever CSS-klasser som ikke er bygget (Tailwind-CLI mangler på maskinen) | avvist |
| B7 | Modellnavnet slås opp i viewet, ikke i et filter | low | Designvalg. Epic 3 kan lage et filter når S9 trenger det | avvist |
| B8 | Ingen negativ test for at kortene ikke er lenker, og plasseringen er bare delvis sjekket | low | `test_ingen_sletting…` sjekker at det ikke finnes quiz-URL-er. Regexen sjekker at merknaden står rett etter metalinjen | avvist |
| B9 | En informasjonstekst ligger i `feilmeldinger.py` | low | Spec-en krever det. Modulen er «tekster til brukeren», jf. docstringen | avvist |

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne
