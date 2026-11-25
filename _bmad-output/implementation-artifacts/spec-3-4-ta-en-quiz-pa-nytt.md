---
title: 'Story 3.4: Ta en quiz på nytt'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
baseline_commit: '768ca389402dd6a2c09121ce9c05c2cbf5e4dcb6'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Når en quiz er levert, kan studenten ikke se at den kan tas på nytt. S7 sier bare «Ta quiz», og S11 har ingen knapp. Uten nye forsøk kan et spørsmål i kjernen aldri bli lært hvis Epic 4 kuttes (FR-20, FR-23).

**Approach:** Bruk den eksisterende `start_quiz` (`start_eller_fortsett_okt`). Den fortsetter allerede et påbegynt forsøk eller lager et nytt med alternativene stokket på nytt (`_lag_innhold`). Knappen heter «Ta på nytt» på S7 når quizen har et levert forsøk, og S11 får et POST-skjema «Ta på nytt» til `start_quiz`. Tester viser at gamle forsøk er uendret, og at to riktige på rad i to leverte forsøk gjør spørsmålet lært og fasiten synlig.

**Decisions (agentens, ikke avklart med mennesket):**
- S7: knappen heter «Ta på nytt» når quizen har minst ett levert `forsok`, ellers «Ta quiz». Påbegynt-merket og «Fortsett» hører til 3.5, så knappen heter også «Ta på nytt» når et nytt forsøk er påbegynt.
- S11: «Ta på nytt» er en sekundærknapp (som «Forrige» på S9) ved «Tilbake til notatet», nederst på siden. Den vises på alle leverte forsøk, også eldre.
- Alternativene stokkes uavhengig med `random.shuffle`. Samme rekkefølge som før kan skje tilfeldig og er lov.
- «N spørsmål er lagt i feilbanken.» teller bare `lagt_i` (avgjort 25.11, se 3.3-loggen).

</frozen-after-approval>

## Implementation Notes

- **Tjenestelaget er uendret.** `start_eller_fortsett_okt` (betinget `UniqueConstraint`, `IntegrityError`-gren) og `registrer_svar` dekker allerede AC 1–3. Ingen nye modeller og ingen migreringer.
- **Filer:**
  - `studier/views.py` → `notat` annoterer `har_levert = Exists(levert forsok)` per quiz. `Exists` i stedet for en ny `Count` hindrer at antall spørsmål ganges opp. `start_quiz` har ny docstring. `resultat` er uendret, fordi malen leser `okt.quiz_id`.
  - `templates/studier/notat.html` → knappeteksten.
  - `templates/studier/resultat.html` → skjemaet «Ta på nytt» ved «Tilbake til notatet».
  - Ny `studier/tests/test_ta_pa_nytt.py` med 13 tester.
  - I `test_levering.py` er `assertNotIn("Ta på nytt")` fjernet.
- **CSS:** layouten bruker klasser som allerede er bygget (`flex-wrap`, `w-full md:w-auto`), så `app.css` er ikke bygget på nytt. `md:flex-row` og `md:gap-6` fantes ikke.
- **Verifisert:** ruff, `makemigrations --check` og 406 tester grønne, 1 hoppet over. Ikke kjørt i nettleser.

## Review Triage Log

B = Blind Hunter. Pass 1, 25.11. Oneshot-ruten har bare dette laget.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | S11 krasjer for `oving` (`okt.quiz_id` er `None`) | maybe-false (high hvis den nås) | Kan ikke nås ennå: ingen tjeneste lager `oving`. Blir aktuelt i 4.2 | defer |
| B2 | Implementation Notes stemmer ikke med koden (`levert`, `quiz_id`) | low | Bekreftet. Notatene er rettet | patch |
| B3 | Docstringen til `start_quiz` nevner bare «Ta quiz» på S7 | low | Bekreftet. Rettet | patch |
| B4 | «Ta på nytt» på S11 fortsetter et påbegynt forsøk | low | Følger AC 3. Teksten hører til 3.5 («Fortsett») | defer |
| B5 | Stokketesten bruker en `shuffle` som ikke gjør noe, og beviser ikke at det nye forsøket bruker stokkingen | medium | Bekreftet. Testen sorterer nå synkende og sjekker rekkefølgen i `ny.innhold` | patch |
| B6 | Testen for «Ta på nytt» fra S11 poster til en hardkodet URL | medium | Bekreftet. Henter nå `action` fra S11-HTML-en | patch |
| B7 | Sekundærknappen er grå, DESIGN.md sier grønn | low | Gjelder også «Forrige» fra 3.1. Krever ny CSS-bygging | defer |
| B8 | Akseptansekriteriene står ikke i spec-en | low | Spec-en er frosset og viser til epic-konteksten. AC 3 dekkes av `test_paabegynt_forsok_fortsettes` og den betingede begrensningen fra 3.1 | avvist |

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne
