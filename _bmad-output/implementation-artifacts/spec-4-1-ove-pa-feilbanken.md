---
title: 'Story 4.1: Øve på feilbanken'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'ab36ff9f9246fcbf8ff5a2f7f3cf6fb751ecd857'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Feilbanken fylles (3.2/3.3), men studenten kan ikke øve på den. Ingen tjeneste lager `oving`-økter, S7 og S11 har ingen «Øv på feil», og S9/S10/S11/S3 antar at en økt har en quiz (FR-22, UX-DR21, UX-DR23).

**Approach:** Utvid `start_eller_fortsett_okt` til å lage eller hente notatets påbegynte øvingsøkt med låst, stokket innhold fra de åpne feilbankradene. Legg «Øv på feil (N)»/«Fortsett» på S7 og S11, gjenbruk S9 og S10 med overskriften «Øv på feil» og terrakotta-aksent, og ta øvingsøkter med i «Fortsett der du slapp».

## Boundaries & Constraints

**Always:**
- **Feilbanken for et notat** = `Feilbankrad` med `laert_tidspunkt IS NULL` for spørsmål i notatets quizer, via `egne(Feilbankrad, …)`. N = antallet.
- **Tjeneste:** `start_eller_fortsett_okt(quiz=None, *, notat=None)`, nøyaktig én av dem. Med `notat`: den påbegynte `oving`-økten for notatet, ellers en ny med `type=oving`, `notat` satt og `quiz=None`. Samme `atomic`/`IntegrityError`-mønster som for forsøk. `innhold` = de åpne radenes spørsmål sortert på `Feilbankrad.opprettet`, så `pk`, hvert med alternativene stokket. Gir `None` (og lager ingenting) når feilbanken er tom og ingen øving er påbegynt. Kall med `quiz` virker som før.
- **Start (POST `notater/<pk>/ov/`, `studier:ov_pa_feil`):** `hent_egen(Notat, …)`, tjenesten, så redirect til `forste_ubesvarte`. `None` gir redirect til S7.
- **S7:** egen seksjon over quizkortene (UX-DR23). Påbegynt øving: knappen «Fortsett» med «Påbegynt – spørsmål N av M» (samme regel som 3.5), også når feilbanken er tom. Ellers «Øv på feil (N)». N = 0 og ingen påbegynt: knappen har `aria-disabled="true"` og `aria-describedby` til teksten «Ingen spørsmål i feilbanken». Alltid et POST-skjema.
- **S11:** samme knapp etter samme regler, men bare når N > 0 eller en øving er påbegynt. Skjemaet «Ta på nytt»/«Fortsett» for quizen vises bare når `okt.quiz_id` er satt.
- **S9 for øving:** h1 «Øv på feil», deretter «Spørsmål N av M» som avsnitt. KI-merket med modellen fra spørsmålets quiz står over spørsmålet. Tittel «Øv på feil – Spørsmål N av M – <notat>». Ingen `er_riktig` eller `begrunnelse` i konteksten. Forsøk er uendret.
- **S9 og S10 for øving:** innholdet ligger i et element med klassen `ovemodus`, som setter `--color-accent-strong: #A34420`, `--color-accent-hover: #7A3214` og `--color-card-hover: #F3D9CC` (prototypen, S12). Valgt alternativ beholder tykk kant og fylt radioknapp. Toppfeltet endres ikke. Brødsmulene: Oversikt › emne › notat › siste.
- **S3:** påbegynte øvingsøkter står i boksen sammen med forsøk, samme sortering, uten ekstra spørringer per rad. Raden har tittelen «Øv på feil, M spørsmål», linjen «<emne> · <notat> · spørsmål N av M» og lenken «Fortsett øvingen» (avgjort av Christian 25.11).
- **Levering før 4.2:** «Lever» virker for øving med uendret `lever_okt`, så svarene registreres mot feilbanken. S11 vises med poengsum og rader, uten quizskjemaet. 4.2 bygger S12-visningen oppå (avgjort av Christian 25.11).
- Andres notat eller øvingsøkt gir 404, og ingenting lages.
- Ingen JavaScript. `app.css` bygges på nytt med Tailwind 4.3.5.

**Never:**
- Ikke endre `lagre_svar`, `lever_okt`, `registrer_svar`, modellene eller migreringene. Ingen ny leveringsflyt.
- Ikke S12-resultatet («Lært. Riktig svar var: …», prikker, teller). Det er 4.2.
- Ikke filtrering av meldte spørsmål (4.3). Ingen «Øv på feil» på S3 eller i Meny.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Start | 3 åpne rader, 1 lært, i to quizer | ny `oving` med 3 spørsmål i radenes rekkefølge, S9 nr 1 | N/A |
| Fortsett | påbegynt øving, 1 av 3 besvart | samme økt, S9 nr 2 | N/A |
| Låst innhold | rad blir lært etter start | `innhold` uendret | N/A |
| Tom feilbank | 0 åpne, ingen påbegynt | S7: `aria-disabled` + «Ingen spørsmål i feilbanken». POST: ingen økt, redirect S7 | N/A |
| Tom, men påbegynt | 0 åpne, påbegynt øving | «Fortsett» virker | N/A |
| Samtidig start | to kall | samme økt | `IntegrityError` → hent |
| S11 | forsøk levert, N = 2 | «Øv på feil (2)» | N/A |
| S3 | påbegynt forsøk og øving | to rader, nyeste først | N/A |
| Tilgang | annens notat eller økt | 404 | ingenting lages |

</frozen-after-approval>

## Code Map

- `studier/services/okter.py` -- `start_eller_fortsett_okt`, `_pabegynt_forsok`, `_lag_innhold`. Legg til `_pabegynt_oving(notat)` og innhold fra feilbankrader. `forste_ubesvarte` gjenbrukes.
- `studier/services/feilbank.py` -- legg til en lesehjelper, for eksempel `apne_rader(notat)` (queryset). Modulen er eneste sted som *skriver* `Feilbankrad`.
- `studier/urls.py`, `studier/views.py` -- ny `ov_pa_feil` (`@require_POST`, som `start_quiz`). `notat` (S7): N og påbegynt øving med `Count("svar")`. `resultat` (S11): samme verdier for `okt.notat`. `_vis_sporsmal`/`_vis_lever`: send `er_oving`, sett tittel og h1. Helst én hjelper som gir knappens tilstand for et notat, brukt av S7 og S11.
- `templates/studier/notat.html`, `resultat.html`, `sporsmal.html`, `lever.html` -- knappen (gjerne en partial, for eksempel `_ov_pa_feil.html`), `ovemodus`-omslaget og `{% if okt.quiz_id %}` på S11.
- `farequiz/views.py` -- `_fortsett_rader` filtrerer på `FORSOK` og bruker `okt.quiz` i tittelen. Fjern typefilteret og lag tittelen for `oving` uten quiz.
- `static/css/input.css` -- `.ovemodus` med de tre variablene. Bygg: `npx --yes @tailwindcss/cli@4.3.5 -i static/css/input.css -o static/css/app.css --minify`. Diffen skal bare legge til `.ovemodus` og eventuelle nye klasser.
- Tester: mønstre i `studier/tests/test_okter.py` (`OktTestCase`, `_annen_bruker`), `test_fortsette.py` (S3) og `test_ta_pa_nytt.py` (S7/S11). Feilbankrader kan lages direkte i testene.

## Tasks & Acceptance

**Execution:**
- [x] `studier/services/feilbank.py`, `studier/services/okter.py` -- `apne_rader` og `notat`-grenen i `start_eller_fortsett_okt`.
- [x] `studier/urls.py`, `studier/views.py` -- `ov_pa_feil`, kontekst for S7, S9, S10 og S11.
- [x] `templates/studier/*.html`, `static/css/input.css`, `static/css/app.css` -- knappen, øvemodus og vakten på S11.
- [x] `farequiz/views.py`, `templates/studier/oversikt.html` -- øvingsøkter i «Fortsett der du slapp».
- [x] `studier/tests/test_oving.py` -- én test per rad i matrisen, pluss at S9 for øving ikke har `er_riktig`/begrunnelse, og at S9 og S10 har `ovemodus` bare for øving.

**Acceptance Criteria:**
- Gitt en påbegynt øvingsøkt, når S9 vises, så står h1 «Øv på feil», KI-merket med modellen fra spørsmålets quiz og alternativene i rekkefølgen fra `innhold`, og siden har klassen `ovemodus`.
- Gitt en levert øvingsøkt, når S11 åpnes, så gir den 200 og har ikke skjemaet til `start_quiz`.

## Implementation Notes

- **Implementert av Sonnet.** Review med tre reviewere på Opus.
- **Tjeneste:** `start_eller_fortsett_okt(quiz=None, *, notat=None)` deler `atomic`/`IntegrityError`-mønsteret for begge typer. `apne_rader(notat)` i `feilbank.py` er en lesehjelper sortert på `opprettet`, `pk`. Den bruker ikke `egne`, fordi notatet alltid er hentet med `hent_egen`.
- **Knappen:** partialen `_ov_pa_feil.html` og `_ov_knapp` i `studier/views.py` brukes av S7 og S11. Knappene har `aria-describedby` til «Øv på feil» (h2 på S7, `sr-only` på S11), så de skilles fra quizens «Fortsett».
- **S9/S10:** `er_oving` gir h1 «Øv på feil», tittel og brødsmule «Øv på feil – Spørsmål N av M» og omslaget `ovemodus`.
- **CSS:** `app.css` er bygd på nytt med `@tailwindcss/cli@4.3.5` (midlertidig, `node_modules` fjernet). Utenom `.ovemodus` kom fem klasser til som malene alt brukte (`hover:bg-surface-muted`, `focus:border-2`, `focus:border-accent-strong`, `md:flex-row`, `md:gap-6`). Den forrige `app.css` manglet dem.
- **Eldre tester:** `test_flere_quizer.py` (skjemalisten på S7) og `test_levering.py` (S11 viser nå «Øv på feil (3)») er oppdatert.
- **Verifisert:** ruff, `makemigrations --check` og 443 tester grønne, 1 hoppet over. Ikke kjørt i nettleser.

## Spec Change Log

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 25.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | `apne_rader` lover «eldste først», men sorterer ikke | low | Bekreftet. Direkte rettelse: `order_by("opprettet", "pk")` i `apne_rader` | patch (med E1, V-a) |
| B2 | `egne(Feilbankrad, notat.emne.eier)` sjekker eieren mot seg selv | low | Bekreftet: vakten beskytter ingenting og koster en ekstra spørring. Notatet er alltid hentet med `hent_egen`. Filtrer direkte og dokumenter forutsetningen | patch (med V-b) |
| B3 | Logglinjen mistet quiz- og notat-ID | low | Bekreftet. Direkte rettelse | patch |
| B4 | Moduldocstringen i `okter.py` nevner bare forsøk | low | Bekreftet. Direkte rettelse | patch |
| B5 | `_ov_knapp` gjentar filteret og teller alltid | low | To små spørringer. Gjenbruk krever `egne` i tjenesten og gir ikke mindre kode | avvist |
| B6 | S11: `mt-3` og manglende `w-full md:w-auto` på skjemaet i flex-raden | medium | Bekreftet: knappen fyller ikke raden på mobil og står forskjøvet | patch |
| B7 | Ingen test for at levert øving registreres i feilbanken | medium | Bekreftet. Spec-beslutningen krever det | patch |
| B8 | Den betingede unike begrensningen er ikke testet | false | `test_modeller.py` linje 73–83 tester `okt_en_pabegynt_oving_per_notat` | avvist |
| B9 | `test_tilgang` dekker ikke S9/S11/POST for andres øving | low | `hent_egen(Okt, …)` er uavhengig av type og testet i `TilgangTest`. Liten nytte | avvist |
| B10 | `aria-disabled` sjekkes mot hele S7 | low | S7 har ingen annen `aria-disabled`. Kosmetisk | avvist |
| B11 | S3-testen mangler `assertNumQueries`, linjen og URL-en for øving | low | Øvingsgrenen leser ikke `okt.quiz`, og spørringene er uendret fra 3.5 | avvist |
| B12 | KI-merket testes ikke med ulik modell per quiz | medium | Bekreftet: begge quizene har `claude-test-standard`, så AC-en er ikke bevist | patch |
| B13 | `test_last_innhold` sammenligner bare lengden | medium | Samme som V2 | patch (med V2) |
| B14 | `app.css` mangler i diffen | false | Utelatt med vilje (minifisert). Kontrollert: bare `.ovemodus` og klasser malene alt bruker, kom til | avvist |
| B15 | Terrakotta på fokusring og valgt svar strider mot DESIGN.md | false | UX-DR21 og prototypen (S12) setter aksenten på hele seksjonen. Endringsforslaget fra 23.11 går foran DESIGN.md | avvist |
| B16 | Stille redirect ved tom feilbank | low | Knappen er `aria-disabled` med beskrivelse, og S7 viser teksten igjen. Melding krever nytt maskineri | avvist |
| B17 | `cursor-pointer` mangler | low | Quizknappene på S7 har det heller ikke. Kosmetisk | avvist |
| E1 | `apne_rader` uten sortering | low | Samme som B1 | patch |
| E2 | S11 kan få to knapper som heter «Fortsett» | medium | Bekreftet når både quiz og øving er påbegynt. Øvingsknappen beskrives nå også av «Øv på feil» (h2 på S7, `sr-only` på S11) | patch |
| V1 | `apne_rader` er ikke testet mot et annet notat hos samme bruker | medium | Bekreftet (filed gap) | patch |
| V2 | `test_last_innhold` kaller ikke start på nytt | medium | Bekreftet (filed gap) | patch |
| V3 | Fremdriften for øving er bare testet med 0 svar | medium | Bekreftet (filed gap) | patch |
| V4 | S11 med påbegynt øving og tom feilbank er ikke testet | medium | Bekreftet (filed gap) | patch |
| V5 | `ov_pa_feil` tar bare POST, men det er ikke testet | medium | Bekreftet (filed gap) | patch |
| V6 | Brødsmulene på S9 og tittelen på S10 er ikke testet | low | Bekreftet. To linjer i eksisterende tester | patch |
| V-a | Docstringen til `apne_rader` | low | Samme som B1 | patch |
| V-b | Ekstra spørring i `apne_rader` | low | Samme som B2 | patch |

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne

**Manual checks:**
- S7, S9 og S10 i øvemodus ved 360 px: ingen vannrett rulling, og knappene og fremdriften er terrakotta.
