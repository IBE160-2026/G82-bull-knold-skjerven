---
title: 'Story 5.2: Dekningsgrad per emne'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'd598c4a20b31a881c9c9ec2349cdc6c3f71d0965'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Dekningsgraden finnes bare på S7. S4 og S3 viser den ikke, verken for emnet eller for notatene, så studenten ser ikke hva som gjenstår i et emne (FR-25, UX-DR7, UX-DR8).

**Approach:** Utvid `services.dekningsgrad` til å regne ut mange notater og emner i et fast antall spørringer, og vis dekningsgraden på emnesiden (S4, tallfliser og notatkort) og på emnekortene på S3.

## Boundaries & Constraints

**Always:**
- **Regelen (AD-4):**
  - Dekningsgraden for et emne er snittet av `total` for notatene som har quiz. Lengden på notatene spiller ingen rolle.
  - Et notat har quiz når minst ett nivå ikke er `None` (et nivå der alle spørsmålene er meldt, er `None`, FR-31).
  - Har ingen notater i emnet quiz, er verdien `None`.
  - Tallet er en `float` mellom 0 og 1 uten avrunding, og avrundes bare i malen med `hel_prosent`.
- **Tjenesten:**
  - `for_notater(notater) -> {notat_id: Dekning}` regner ut alle notatene med de samme to spørringene som i 5.1, gruppert på notat. Spørringene øker ikke med antall notater eller spørsmål.
  - `for_notat(notat)` bruker `for_notater` og gir det samme som før.
  - `for_emner(emner) -> {emne_id: float | None}` bruker `for_notater`.
  - `services.dekningsgrad` er fortsatt eneste sted «dekket» defineres.
- **Feilbanken per notat:** en lesehjelper i `feilbank.py` gir `{notat_id: antall}` i én spørring, med samme utvalg som `apne_rader` (ikke lært, ikke meldt).
- **S4:**
  - To tallfliser under h1 (UX-DR8, `stat-tile`: `bg-surface-inverse`, tallet stort, kort tekst under).
    - «Dekningsgrad» med «N %», eller «Ingen dekningsgrad».
    - «I feilbanken» med antallet for hele emnet.
  - Hvert notatkort viser filnavn og «Lastet opp …» som i dag, og i tillegg dekningsgraden med en enkel `reiserute`-stolpe (uten fåret, `aria-hidden`) og «Dekningsgrad N %», eller «Ingen quiz».
  - Notatkortet viser også «N i feilbanken».
  - Emne uten notater viser ingen tallfliser, bare dagens tomtilstand.
- **S3:**
  - Hvert emnekort viser antall notater som i dag.
  - I tillegg: en stolpe og «Dekningsgrad N %», eller «Ingen notater» for et emne uten notater, eller «Ingen dekningsgrad» når ingen notater har quiz.
  - Teksten står i lenken, så kortet leses som for eksempel «Webutvikling, 4 notater, Dekningsgrad 62 %».
- **Ytelse:** antall spørringer på S3 og S4 er det samme for 1 og 3 emner eller notater.
- Ingen ny modell, migrering eller lagret verdi. Ingen JavaScript.

**Never:**
- Ikke endre regelen for «dekket» eller S7. Ikke historikk (5.3).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| FR-25-eksempel | to notater med 0,8 og 0,4, et tredje uten quiz | emnet 0,6. S4 «60 %» og «Ingen quiz» på det tredje | N/A |
| Uten notater | emne uten notater | `None`. S3 «Ingen notater», S4 uten tallfliser | N/A |
| Ingen quiz | notater, men ingen quizer | `None`. S3 og S4 «Ingen dekningsgrad» | N/A |
| Alle meldt | notat der alle spørsmålene er meldt | teller som uten quiz | N/A |
| Feilbank | 2 åpne rader i notat A, 1 i B, 1 meldt og 1 lært | A «2 i feilbanken», B «1», flisen «3» | N/A |
| Samme som S7 | notat med vilkårlige svar | `for_notater(...)[id]` er lik `for_notat(notat)` | N/A |
| Andre brukere | andres emner og notater | ikke med i tallene eller på sidene | N/A |
| Spørringer | 1 og 3 emner (S3), 1 og 3 notater (S4) | samme antall spørringer | N/A |

</frozen-after-approval>

## Code Map

- `studier/services/dekningsgrad.py` -- `for_notat` fra 5.1.
  - Flytt spørringene til `for_notater`, med `values("quiz__notat", "quiz__vanskelighetsgrad")` og `quiz__notat__in=notater`.
  - Nivåene med quiz kommer fra `Quiz.objects.filter(notat__in=…).filter(Exists(Sporsmal.objects.ikke_meldt().filter(quiz=OuterRef("pk")))).values_list("notat_id", "vanskelighetsgrad").distinct()`.
  - Regnestykket per notat er uendret. KEEP: `hel_prosent`, `VEKTER` og `Dekning`.
- `studier/services/feilbank.py` -- `apne_rader` er utvalget. Den nye hjelperen, for eksempel `antall_apne_per_notat(notater)`, grupperer på `sporsmal__quiz__notat`.
- `studier/views.py:83` `_vis_emne` -- hent notatene som liste, regn ut `for_notater`, `for_emner([emne])` og feilbanktallene, og legg dem på hvert notat eller i konteksten.
- `farequiz/views.py:64` `startside` -- emnene som liste, og `for_emner` for dem.
- `templates/studier/emne.html`, `templates/studier/oversikt.html` -- flisene, stolpen og tekstene. Stolpen er `<div class="reiserute" aria-hidden="true"><span style="width: {{ p }}%"></span></div>` med `p` fra `hel_prosent`. `{% load dekning %}`.
- `static/css/` -- `bg-surface-inverse`, `text-ink-inverse` og `grid-cols-2` finnes i `app.css`. Bygg den på nytt bare ved nye klasser, som beskrevet i spec 5.1.
- Tester: `studier/tests/test_dekningsgrad.py` (hjelperne `_quiz`, `_forsok` og lignende) og `test_emner.py` (S3 og S4). Lag `studier/tests/test_dekningsgrad_emne.py`.

## Tasks & Acceptance

**Execution:**
- [x] `studier/services/dekningsgrad.py`, `studier/services/feilbank.py` -- `for_notater`, `for_emner` og feilbanktallene.
- [x] `studier/views.py`, `farequiz/views.py` -- konteksten for S4 og S3.
- [x] `templates/studier/emne.html`, `templates/studier/oversikt.html` -- visningen.
- [x] `studier/tests/test_dekningsgrad_emne.py` -- én test per rad i matrisen, pluss HTML for flisene og kortene. Eksisterende tester for 5.1, S3 og S4 skal være grønne uten endringer.

**Acceptance Criteria:**
- Gitt et emne med to notater på 80 % og 40 %, når S3 vises, så står «Dekningsgrad 60 %» på emnekortet, inne i lenken.
- Gitt S4 for samme emne, når den vises, så står «60 %» i flisen «Dekningsgrad», og hvert notatkort har sin prosent og sitt antall i feilbanken.

## Implementation Notes

- **Implementert av en underagent.** Review med tre reviewere på Opus.
- **Tjenesten:** `for_notater` (2 spørringer), `for_notat` bruker den, og `for_emner` (3 spørringer). `Dekning.har_quiz` er sann når minst ett nivå ikke er `None`. Etter review regner hjelperen `snitt(dekninger)` ut snittet både for `for_emner` og S4, så S4 ikke regner ut alt to ganger.
- **Feilbanken:** `_apne()` er felles utvalg for `apne_rader` og den nye `antall_apne_per_notat` (1 spørring).
- **Visning:** tallflisene står under hverandre under `md` og side om side fra `md` (`md:grid-cols-2`). `stat-tile` er bare et klassenavn, uten egen CSS. Stolpen på kortene er `.reiserute` uten fåret.
- **CSS:** bare klasser som alt fantes i `app.css`.
- **Etter review:** `snitt`, skilletegn for skjermleser på notatkortene, tallflisene som `<dl>` med etiketten først, og tester for et notat med quiz på 0 % og faste verdier mot S7.

## Spec Change Log

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 25.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| V1 | Ingen test for et notat med quiz, men 0 % dekning | medium | Bekreftet (filed gap): `har_quiz` med sannhetsverdi i stedet for `None`-sjekk ville passert | patch (med B4) |
| B4 | Samme som V1 | medium | Samme som V1 | patch (med V1) |
| B1 | S4 regner ut dekningsgraden to ganger | low | Bekreftet: `for_emner([emne])` henter notatene og kjører `for_notater` på nytt. Direkte rettelse med `snitt` | patch (med V-a, E1) |
| V-a | Samme som B1 | low | Samme som B1 | patch (med B1) |
| E1 | Flisen kan bruke andre notater enn kortene hvis et notat lastes opp samtidig | low | Samme rettelse som B1: snittet regnes fra de samme dekningene | patch (med B1) |
| B2 | Notatkortene på S4 mangler skilletegn for skjermleser | low | Bekreftet. S3 har dem. Direkte rettelse | patch |
| B6 | Tallflisene knytter ikke tall og etikett sammen | low | Bekreftet. `<dl>` som på S7 | patch |
| B3 | Emnekortet for et tomt emne leser «0 notater, Ingen notater» | low | Spec-en sier at kortet viser antallet som i dag, og `test_emner.py` sjekker «0 notater». Dobbelt, men ikke feil | avvist |
| B5 | `test_samme_som_s7` sammenligner koden med seg selv | low | Bekreftet. Legg til faste forventede verdier | patch |
| B7 | Kort med og uten quiz har ulik avstand | low | Kosmetisk. Ingen funksjon påvirkes | avvist |
| B8 | Stolpen er skrevet to ganger i stedet for en partial | low | Én linje HTML på to steder. En ny partial gir ikke mindre kode | avvist |
| B9 | Testhjelperne er like, og `_flis` bruker ikke `re.escape` | low | Bare testkode, og etikettene har ingen spesialtegn | avvist |
| B10 | Spec-en og `sprint-status.yaml` er ikke med i diffen | false | Utelatt med vilje. Review gjelder koden | avvist |
| E2 | S3 kan telle notater og dekning fra ulike spørringer hvis et notat lastes opp samtidig | low | Vinduet er millisekunder, og neste visning stemmer | avvist |

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne

**Manual checks:**
- S3 og S4 ved 360 px: ingen vannrett rulling, og flisene står side om side eller under hverandre.
