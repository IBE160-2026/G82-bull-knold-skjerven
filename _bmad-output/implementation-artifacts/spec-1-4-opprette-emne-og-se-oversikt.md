---
title: 'Story 1.4: Opprette emne og se Oversikt'
type: 'feature'
created: '2026-11-24'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '0b1ff3c'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `/` er en midlertidig startside, og studenten kan ikke opprette emner ennå. FR-3 og FR-4 krever at hver bruker bare ser og oppretter egne emner.

**Approach:** Gjør `/` til Oversikt (S3) med kortet «Nytt emne» først og emnekortene alfabetisk. Lag S16 «Nytt emne» på `/emner/ny/` med navnefeltet. Lag S4 Emne på `/emner/<pk>/`, som viser notatene (tomme til 2.3). Eierskap sjekkes med `hent_egen`, og andres emner gir «Fant ikke siden».

## Boundaries & Constraints

**Always:**
- Følg epic-1-context.md, AD-1, AD-8 og AD-14. Norske identifikatorer uten æ, ø og å. Tekst er norsk bokmål, du-form og uten utropstegn.
- All skriving av `Emne` skjer i `studier/services/emner.py` (`opprett_emne`). Skjemaet sjekker selv at navnet er unikt uten å skille store og små bokstaver.
- Alle ID-er fra URL slås opp med `studier.tilgang.hent_egen`. Ingen rå `pk`-oppslag i views.
- Navnet trimmes. Et navn som er tomt etter trimming, er tomt. Høyst 100 tegn, som modellen.
- Emnekort og emnenavn lenker til S4. Hele kortet er én lenke med tydelig tekst, for eksempel «Webutvikling, 0 notater».
- Feilmeldinger står i `farequiz/feilmeldinger.py`. Feilen vises ved feltet med `aria-describedby`, og fokus flyttes dit.
- Universell utforming: ingen vannrett rulling på 320 px, `lang="nb"`, én `<h1>`, og POST/redirect/GET.
- Tilbake vises på S4 og S16, og peker til Oversikt. Ikke på Oversikt.
- Testmodus-banneret, toppfeltet og brødsmulesti fra 1.3 brukes. Ingen ny mal.

**Never:**
- Ingen notater, ingen opplasting og ingen dekningsgrad. Notatlisten er tom til 2.3, og dekning kommer i Epic 5.
- Ingen «Gi nytt navn» (1.5) og ingen «Slett emne» (1.6) på S4.
- Ingen nye migreringer. `Emne` finnes allerede.
- Ingen JavaScript.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Tom oversikt | Innlogget, ingen emner | Kortet «Nytt emne» og teksten «Ingen emner ennå. Opprett ditt første emne.» | N/A |
| Oversikt | Emner «webutvikling» og «Databaser» | Emnene alfabetisk, uten å skille store og små bokstaver. «Nytt emne» først | N/A |
| Opprett | «  HTML  » | Emne «HTML» lagres, og brukeren sendes til S4 med «Ingen notater ennå. Last opp det første.» | N/A |
| Tomt navn | Bare mellomrom | Ingen emne. «Navnet kan ikke være tomt.» ved feltet | Feilmelding ved feltet, fokus dit |
| Navn tatt | «html» når «HTML» finnes | Ingen emne. «Du har allerede et emne med dette navnet.» | Feilmelding ved feltet, fokus dit |
| For langt navn | 101 tegn | Ingen emne. «Navnet kan være høyst 100 tegn.» | Feilmelding ved feltet, fokus dit |
| Annen brukers navn | Bruker B oppretter «HTML» når A har det | Lagres. Unike navn gjelder per eier | N/A |
| Eget emne | Innlogget eier åpner `/emner/<pk>/` | S4 med navnet og tomme notater | N/A |
| Andres emne | Innlogget, `pk` tilhører en annen bruker | «Fant ikke siden», 404. Dataene avsløres ikke | 404 |
| Ukjent emne | `pk` finnes ikke | «Fant ikke siden», 404 | 404 |
| Utlogget | Åpner `/` eller `/emner/ny/` | Sendt til innlogging med `next` | N/A |
| Rekkefølge | Tre emner | Kortene følger alfabetisk rekkefølge | N/A |

## Code Map

- `farequiz/views.py` -- `startside` blir Oversikt: henter `egne(Emne, bruker)` sortert på `navn` (`Lower`). Brødsmulesti er bare «Oversikt». Navnet `startside` beholdes, og tittelen blir «Oversikt».
- `studier/services/emner.py` -- ny. `opprett_emne(eier, navn)` trimmer, sjekker tomt og lengde, og lagrer. Unikt navn fanges av skjemaet, og `IntegrityError` mappes til «Du har allerede et emne med dette navnet.». Samme mønster som `studier/services/vilkar.py`.
- `studier/forms.py` -- ny. `EmneForm(ModelForm)` med `navn`, `eier` gis i konstruktøren og brukes til unikhetssjekken uten å skille store og små bokstaver.
- `studier/views.py` -- ny. `ny_emne` (GET og POST på `/emner/ny/`) og `emne` (GET på `/emner/<pk>/`, med `hent_egen(Emne, pk, request.user)`).
- `studier/urls.py` -- ny, `app_name = "studier"`. Inkluderes i `farequiz/urls.py`.
- `templates/studier/oversikt.html` -- avløser `templates/startside.html`. Kortet «Nytt emne» først, så emnekortene, og tomtilstanden.
- `templates/studier/ny_emne.html` -- S16. Navnefelt, feilmelding og «Opprett emne».
- `templates/studier/emne.html` -- S4. Navn i `<h1>`, «Last opp notat» som deaktivert knapp til 2.3, og «Ingen notater ennå. Last opp det første.».
- `farequiz/feilmeldinger.py` -- legg til `NAVN_TOMT`, `NAVN_TATT` og `NAVN_FOR_LANGT`.
- `studier/tests/test_emner.py` -- tester for hver rad i I/O-matrisen, og for at `opprett_emne` er den eneste skriveveien.
- `kontoer/tests_sider.py` -- den midlertidige startsiden testes der i dag. Oppdateres til Oversikt.

## Tasks & Acceptance

**Execution:**
- [x] `studier/services/emner.py` -- `opprett_emne` med trimming, lengdesjekk og unikt navn
- [x] `studier/forms.py` -- `EmneForm` med unikhetssjekk uten å skille store og små bokstaver
- [x] `studier/views.py` og `studier/urls.py` -- `/emner/ny/` og `/emner/<pk>/`, med `hent_egen`
- [x] `farequiz/views.py` og `templates/studier/oversikt.html` -- `/` blir Oversikt med kort og tomtilstand
- [x] `templates/studier/ny_emne.html` og `templates/studier/emne.html` -- S16 og S4
- [x] `farequiz/feilmeldinger.py` -- tre nye feilmeldinger
- [x] Tester etter I/O-matrisen, og en test for at andres `pk` gir 404
- [x] Oppdater `kontoer/tests_sider.py` til Oversikt

**Acceptance Criteria:**
- Gitt en innlogget bruker uten emner, når hen åpner `/`, så står kortet «Nytt emne» og teksten «Ingen emner ennå. Opprett ditt første emne.».
- Gitt tre emner, når Oversikt vises, så står de alfabetisk etter navn, uten å skille store og små bokstaver.
- Gitt et tomt eller for langt navn, eller et navn som finnes fra før, når skjemaet sendes, så lagres ingenting og feilmeldingen står ved feltet med fokus.
- Gitt en opprettet emne, når brukeren sendes til S4, så står navnet i `<h1>` og «Ingen notater ennå. Last opp det første.».
- Gitt en annen brukers `pk`, når siden åpnes, så vises «Fant ikke siden» med status 404.
- Gitt en skjerm på 320 px, når Oversikt og S16 vises, så er det ingen vannrett rulling.

## Implementation Notes

- **24.11, implementert og verifisert lokalt.** Oversikt er `/`, S16 er `/emner/ny/`, og S4 er `/emner/<pk>/`. `opprett_emne` er eneste skriveveien for `Emne`.
- **Verifisert:** 120 tester er grønne, med 13 nye. ruff, format og migreringssjekk er grønne. Nettleser (Chrome headless, `DEBUG=False`): feil ved tomt navn, fokus på feilmeldingen, opprettelse og videre til S4, Oversikt, ingen vannrett rulling på 320 px, og axe finner ingen brudd på `/` og `/emner/ny/`.
- **Endringer i eksisterende tester:** stand-in-ruten for «beskyttet side» er flyttet fra `/emner/<pk>/` til `/testside/<pk>/`, siden emnesiden nå finnes. Tittelen på Oversikt er «Oversikt».
- **Åpent:** S4 har ingen «Gi nytt navn» og ingen «Slett emne». Det kommer i 1.5 og 1.6.
- Branchen starter fra `story-1-3-toppfelt` (`0b1ff3c`), fordi PR #5 ikke er merget ennå.

## Spec Change Log

## Design Notes

- **Oversikt er `/`.** Navnet `startside` beholdes for ikke å endre URL-er og tester fra 1.2. Tittelen blir «Oversikt».
- **Dekning er ikke med.** Plassen for dekningsgrad i kortet kommer i Epic 5, slik sprint-forslaget sier.
- **Unikt navn:** Databasen har `UniqueConstraint` på `Lower(navn)` per eier. Skjemaet sjekker først, slik at feilmeldingen blir riktig, og `IntegrityError` er bare et sikkerhetsnett.

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- expected: 0 funn
- `uv run python manage.py makemigrations --check --dry-run` -- expected: «No changes detected»
- `uv run python manage.py test` -- expected: alle tester grønne

**Manual checks:**
- `runserver` med testbrukeren: opprett tre emner i tilfeldig rekkefølge, og sjekk alfabetisk sortering.
- Sjekk 320 px uten vannrett rulling, og Tilbake fra S4 og S16.
