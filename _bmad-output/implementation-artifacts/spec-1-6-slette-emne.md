---
title: 'Story 1.6: Slette emne'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'd304f5492f961f5e13d1630eea77b6d2a36320cd'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Studenten kan ikke slette et emne (FR-6). Emner hun er ferdig med, blir liggende med notater og filer.

**Approach:** S4 får lenken «Slett emne» til bekreftelsessiden S13 (`/emner/<id>/slett/`). Siden sier nøyaktig hva som slettes, og POST kaller `services.emner.slett_emne`. Den sletter alt i emnet i én transaksjon, og filene slettes etter commit (AD-14). Etterpå sendes brukeren til Oversikt (S3).

## Boundaries & Constraints

**Always:**
- `slett_emne(emne)` samler filnavnene til notatene og sletter emnet med cascade i `transaction.atomic`. Filene slettes i `transaction.on_commit`. En fil som alt mangler, eller som ikke kan slettes, gir ingen feil for brukeren.
- Bare `slett_emne` sletter `Notat`, `Quiz`, `Okt` eller `Feilbankrad`. En test sjekker at ingen annen kode i appene kaller `.delete()` på disse.
- Emnet hentes med `hent_egen` både ved GET og POST. Andres emne gir «Fant ikke siden» (404), og ingenting slettes.
- S13 er en egen side, ikke en popup. Overskrift: «Slette emnet «<navn>»?». Teksten sier antallet notater og quizer, for eksempel «Dette sletter 4 notater, 9 quizer og all historikk. Det kan ikke angres.»
- «Avbryt» (sekundær, lenke til S4) kommer før fareknappen «Slett emnet og alt innhold» (`error`, POST) i tab-rekkefølgen.
- Andre emner og dataene deres er uendret. Det testes.
- Virker uten JavaScript. Ingen vannrett rulling på 320 px. Klikkflatene er minst 44 px.

- **Beslutning 25.11:** CSS bygges med `npx @tailwindcss/cli@4.3.5`, samme versjon som i 1.3. Ingen ny binær eller avhengighet i repoet. Spec-en beholdes som én story selv om den er ca. 2000 tokens.

**Never:**
- Ingen popup og ingen JavaScript.
- Ingen nye migreringer og ingen endringer i modellene.
- Ingen sletting av konto eller av enkeltnotater (ikke i v1).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Vis S13 | Eier åpner `/emner/<id>/slett/` | Overskrift med navnet, antall notater og quizer, «Avbryt» før fareknappen | N/A |
| Slett | POST fra eier | Emnet og alt i det er slettet, filene er borte, sendt til S3 | N/A |
| Fil mangler | Notatets fil finnes ikke på disk | Slettes uten feil, sendt til S3 | Ignoreres |
| Tilbakerulling | Transaksjonen ruller tilbake etter `slett_emne` | Radene og filen ligger igjen | N/A |
| Andre emner | Brukeren har to emner | Bare det valgte slettes | N/A |
| Andres emne | GET eller POST mot en annen brukers emne | «Fant ikke siden», 404, ingenting slettes | 404 |
| Allerede slettet | POST på nytt etter sletting | 404 | 404 |
| Utlogget | GET eller POST uten innlogging | Sendt til innlogging | N/A |

</frozen-after-approval>

## Code Map

- `studier/services/emner.py` -- legg til `slett_emne(emne)`. Bruk `default_storage.delete(navn)` per fil i `on_commit(..., robust=True)`, og fang `OSError` per fil, så én feil ikke stopper resten. Eksisterende `opprett_emne` og `gi_nytt_navn` er uendret.
- `studier/views.py` -- ny view for GET og POST på S13. Bruk `hent_egen(Emne, pk, request.user)`. Tell notatene (`objekt.notater.count()`) og quizene (`Quiz.objects.filter(notat__emne=objekt).count()`). Brødsmuler: Oversikt › <emne> › Slett emne. Tilbake går til S4 med «Tilbake til <emne>». Importer servicen med alias, fordi viewen heter det samme.
- `studier/urls.py` -- `emner/<int:pk>/slett/`, navn `studier:slett_emne`.
- `templates/studier/slett_emne.html` -- ny S13. Følg knappestilen i `ny_emne.html` og `emne.html`.
- `templates/studier/emne.html` -- lenken «Slett emne» nederst, slik som i prototypen (S4).
- `static/css/app.css` -- bygges på nytt med `npx @tailwindcss/cli@4.3.5 -i static/css/input.css -o static/css/app.css --minify`. `input.css` er uendret.
- `studier/tests/fabrikk.py` -- `lag_kjede` gir et notat med fil, men uten fil på disk. Testene lager filen selv i en midlertidig `MEDIA_ROOT` (`override_settings`).
- `studier/tests/test_slett_emne.py` -- ny. Bruk `captureOnCommitCallbacks(execute=True)` for filsletting.
- Ikke endre: modellene, `studier/tilgang.py` og `farequiz/views.py` (Oversikt).

## Tasks & Acceptance

**Execution:**
- [x] `studier/services/emner.py` -- `slett_emne` med atomic og on_commit -- AD-14
- [x] `studier/views.py` og `studier/urls.py` -- S13 med GET og POST, `hent_egen` og omdirigering til `startside`
- [x] `templates/studier/slett_emne.html` og `templates/studier/emne.html` -- S13 og lenken på S4
- [x] `static/css/app.css` -- bygges på nytt med `bg-error` og `hover`-variant
- [x] `studier/tests/test_slett_emne.py` -- én test per rad i I/O-matrisen, tab-rekkefølgen og kildesjekken for `.delete()`

**Acceptance Criteria:**
- Gitt S4, når eieren velger «Slett emne», så åpnes S13 med antallet notater og quizer og knappene i riktig rekkefølge.
- Gitt S13, når eieren trykker «Slett emnet og alt innhold», så finnes ingen rader fra emnet etterpå (notater, jobber, quizer, spørsmål, alternativer, økter, svar og feilbankrader), filen er borte fra disk, og S3 vises uten emnet.
- Gitt kildekoden, når testen søker etter `.delete()` på `Notat`, `Quiz`, `Okt` eller `Feilbankrad` utenfor `studier/services/emner.py` og testene, så finner den ingenting.

## Implementation Notes

- **25.11, implementert.** 160 tester er grønne (17 nye) etter review-rettelsene. ruff, format og migreringssjekken er grønne.
- **CSS-bygging:** `npx @tailwindcss/cli@4.3.5` alene feiler med «Can't resolve 'tailwindcss'», fordi repoet ikke har `node_modules`. `tailwindcss@4.3.5` og `@tailwindcss/cli@4.3.5` ble installert i en midlertidig mappe utenfor repoet og kjørt mot `static/css/input.css`. Bare `.bg-error`, `.mt-8` og `hover:brightness-90` kom til i `app.css`.
- **Hover på fareknappen:** tokenene har ingen mørkere rødfarge, så knappen bruker `hover:brightness-90` i stedet for en ny token.
- **Kildesjekken** søker linje for linje etter modellnavn og `.delete(`. Den fanger ikke en variabel med et nøytralt navn.

## Spec Change Log

## Review Triage Log

Runde 1, 25.11. Tre lag: Blind Hunter (B), Edge Case Hunter (E) og Verification Gap (V).

| # | Lag | Funn | Vurdering | Begrunnelse | Rute |
|---|-----|------|-----------|-------------|------|
| 1 | B, E, V | `_slett_filer` fanger bare `OSError`. Andre feil stopper løkken, og resten av filene blir liggende | low | `SuspiciousFileOperation` er ikke `OSError`. Navnene kommer fra `upload_to`, så det skjer neppe, men rettelsen er én linje | patch |
| 2 | V | `robust=True` testes ikke av noen feil som ikke er `OSError` | medium | Testen med `PermissionError` fanges av `except OSError`, så flagget kunne fjernes uten at noen test feilet | patch |
| 3 | B, E | Testen av tab-rekkefølgen finner brødsmulelenken i stedet for «Avbryt» | medium | `html.index('href="/emner/<pk>/"')` treffer brødsmulen før `<main>`, så testen ville bestått selv om «Avbryt» ble flyttet | patch |
| 4 | B, E, V | Kildesjekken fanger ikke `.delete()` på `Emne`, `Genereringsjobb`, `Sporsmal` eller brukeren, som alle sletter videre med cascade | medium | Alle fremmednøkler har CASCADE. Ingen slike kall finnes i dag, men sjekken håndhever ikke AD-14 | patch |
| 5 | E, B | Kildesjekken består uten å sjekke noe hvis en app-mappe mangler | low | `rglob` på en mappe som ikke finnes gir ingen treff. Rettelsen er én `assert` | patch |
| 6 | B | `test_allerede_slettet_gir_404` sjekker ikke at første POST slettet | low | En feil i første POST ville gitt 404 likevel. Rettelsen er to linjer | patch |
| 7 | B | Testen for fil som mangler, sjekker ikke at ingenting logges | low | Viser ikke at fila hoppes over uten varsel. Rettelsen er `assertNoLogs` | patch |
| 8 | V | Ingen test sjekker CSRF-tokenet i skjemaet på S13 | low | Uten `{% csrf_token %}` feiler sletting i nettleseren (403), men testene består. Én `assertIn` | patch |
| 9 | B | Den dokumenterte kommandoen for å bygge CSS virker ikke | medium | `scripts/bygg-css.sh` krever binæren, og `npx` alene finner ikke `tailwindcss`. Problemet fantes før denne storyen | defer |
| 10 | B | Opplasting som kjører samtidig med sletting kan etterlate en fil | maybe-false | Opplasting finnes ikke før story 2.3. Avgjøres når `last_opp` skrives | defer |
| 11 | B | Teksten «2 notater, 0 quizer» når emnet ikke har quizer | low | Kosmetisk. Følger formatet i spec-en, og en rettelse krever en ny gren i malen | avvist |
| 12 | B | `antall_notater or antall_quizer` er i praksis bare `antall_notater` | false | Riktig resultat i alle tilfeller, og ingen feil oppstår | avvist |
| 13 | B | Sprint-status (`in-progress`) og spec (`in-review`) er ulike | false | Steg 5 setter sprint-status til `review`. Det er rekkefølgen i arbeidsflyten | avvist |
| 14 | B | Tomme mapper `notater/<bruker>/` blir liggende | low | Ingen skade for brukeren, og rettelsen krever ekstra logikk | avvist |
| 15 | B | `APPER` er hardkodet i stedet for hentet fra `INSTALLED_APPS` | low | Funn 5 dekker at sjekken ikke består uten å sjekke noe. Mer logikk for liten gevinst | avvist |
| 16 | E | To POST samtidig: den andre gir 302 i stedet for 404 | low | Kappløp. Brukeren havner på S3 der emnet er borte, og ingen data går tapt | avvist |
| 17 | V | CSRF bør testes likt i hele repoet | low | Dekket for S13 i funn 8. En felles regel for alle skjemaer hører ikke hjemme i denne storyen | avvist |

## Design Notes

- **Tekst ved antall:** entall og flertall («1 notat», «2 notater», «1 quiz», «2 quizer»). Uten notater: «Dette sletter emnet. Det har ingen notater eller quizer ennå. Det kan ikke angres.»
- **Ingen melding på S3 etter sletting.** Prototypen viser ingen, og emnet er borte fra lista.
- **`robust=True`** på `on_commit`: en feil ved filsletting logges i stedet for å gi 500 etter at radene alt er slettet.
- Genereringsjobber som kjører (Epic 2), finnes ikke ennå. Hva som skjer med en jobb under sletting, avgjøres i Epic 2.

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- expected: 0 funn
- `uv run python manage.py makemigrations --check --dry-run` -- expected: «No changes detected»
- `uv run python manage.py test` -- expected: alle tester grønne

**Manual checks:**
- `runserver`: slett et emne fra S4 via S13 med bare tastatur. Sjekk fareknappens farge, tab-rekkefølgen og 320 px.
