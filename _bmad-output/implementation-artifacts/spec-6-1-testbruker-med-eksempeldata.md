---
title: 'Story 6.1: Testbruker med eksempeldata'
type: 'feature'
created: '2026-11-26'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'cbc02c21312bd49a1369b1b76a30d7b420bdcb56'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-6-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Sensor har ingen bruker med data. Etter `migrate` er databasen tom, og S3, S4 og S7 viser bare tomtilstander, så dekningsgrad, historikk, feilbank og «Fortsett der du slapp» kan ikke vises uten å bruke mange minutter (FR-28, AD-21, UX-DR26).

**Approach:** Ny kommando `manage.py seed_testdata` lager testbrukeren og et fast datasett gjennom de vanlige tjenestene i testmodus. Innloggingen står på ett sted i koden, og den vises på S1 i testmodus og i README-en.

## Boundaries & Constraints

**Always:**
- **Testmodus og nettverk:** kommandoen kaller `ki.tving_testmodus()` først og gjør aldri nettverkskall.
- **Bare tjenester (AD-1):**
  - `create_user` og `godta_vilkar` for brukeren, `opprett_emne` for emnet og `last_opp` med filene fra `testdokumenter/`.
  - `generer_synkront` for quizene, og `start_eller_fortsett_okt`, `lagre_svar` og `lever_okt` med faste svar.
  - Ved ny kjøring slettes brukerens emner med `slett_emne`.
  - Aldri `Model.objects.create`/`update` på `studier`-modellene i kommandoen.
- **Innlogging (besluttet 26.11):** `sensor@farequiz.no` med passordet `sensor123`. De står som konstanter i én modul. Seed, S1 og en test mot README-en bruker dem.
- **Mock-svar (besluttet 26.11):** bygg nå. Testene bruker en midlertidig mock-mappe. 6.1 står i `review` til Magnus har kjørt `lag_mocksvar` og prøvd seed på ekte.
- **Datasett (fast):** emnet «Webutvikling» med tre notater.
  - **`html-struktur-og-semantikk.pdf`:**
    - Quiz lett med 10 spørsmål. Forsøk 1 leveres med 1–7 riktige, så 8–10 havner i feilbanken. Forsøk 2 («ta på nytt») leveres med alle riktige.
    - Deretter leveres en øvingsøkt der 8 og 9 er riktige og 10 er feil. Da er 8 og 9 lært, og 10 er fortsatt åpen.
    - Quiz middels med 10 spørsmål og et påbegynt forsøk med 3 svar. Det gir «Fortsett der du slapp» på S3 og «Påbegynt – spørsmål 4 av 10».
  - **`universell-utforming.docx`:** quiz vanskelig med 10 spørsmål og ett levert forsøk med 6 riktige.
  - **`javascript-og-dom.txt`:** ingen quiz, så «Ingen quiz» og «Lag en quiz for å komme i gang» også vises.
  - Valgt svar velges på `er_riktig`, ikke på posisjon, så stokkingen ikke endrer resultatet.
- **Kjøres to ganger:** finnes brukeren, slettes emnene, passordet settes på nytt og vilkårene godtas. Resultatet blir det samme, med samme antall av hver ting.
- **Mock-svar mangler:** finnes ikke `ki/mock/manifest.json`, stopper kommandoen med `CommandError` og en norsk melding om `lag_mocksvar` før noe er endret.
- **S1 i testmodus:** en boks over skjemaet med «Testbruker», e-posten og passordet. Utenfor testmodus vises den ikke.
- **README:** et kort avsnitt «Testbruker» med kommandoen og innloggingen.

**Never:**
- Ingen ny modell eller migrering, og ikke noe design på S1 utover boksen (designet hører til egen story).
- Ikke bytt ut `ki.generer` i kommandoen, og ikke lag quizer uten `generer_synkront`.
- Ikke kjør seed automatisk ved oppstart eller i `migrate`. CI-steget hører til 6.2.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Første kjøring | tom database, mock-mappe finnes | 1 bruker, 1 emne, 3 notater, 3 quizer, 3 leverte forsøk, 1 levert øving, 1 påbegynt forsøk, 7 feilbankrader (2 lært, 5 åpne: 1 i HTML-notatet og 4 i DOCX-notatet) | N/A |
| Kjøres igjen | brukeren og dataene finnes | samme antall av hver ting. Gamle notatfiler er slettet fra disk | N/A |
| Lært og ikke lært | etter seed | spørsmål 8 og 9 i lett har `laert_tidspunkt`, og 10 har ikke | N/A |
| Uten mock-svar | `ki/mock/manifest.json` mangler | `CommandError`. Ingen bruker eller emne endret | melding om `lag_mocksvar` |
| Nettverk | `ki.generering._klient` patchet til å feile | kommandoen lykkes | N/A |
| S1 testmodus | testmodus på / av | boksen med innloggingen vises / vises ikke | N/A |
| Innlogging | etter seed | `client.login` med konstantene lykkes, og S3 viser «Webutvikling» med dekningsgrad og «Fortsett der du slapp» | N/A |

</frozen-after-approval>

## Code Map

- `studier/management/commands/seed_testdata.py` -- ny. `studier/management/` finnes ikke, så lag `__init__.py` i begge mappene. Mønster for kommandoen: `ki/management/commands/lag_mocksvar.py`.
- Konstantene -- ny `kontoer/testbruker.py` med `EPOST` og `PASSORD`. S1-viewet (`kontoer/views.py`, innlogging) legger dem i konteksten, og `templates/kontoer/logg_inn.html` viser boksen når `testmodus` er sann (context processor `farequiz/context_processors.py`).
- Tjenester:
  - `studier/services/emner.py`: `opprett_emne(eier, navn)` og `slett_emne(emne)`
  - `studier/services/vilkar.py`: `godta_vilkar`
  - `studier/services/notater.py`: `last_opp(emne, fil, bruker)`, der fila er `File`/`SimpleUploadedFile` med `name`
  - `studier/services/generering.py:205`: `generer_synkront`
  - `studier/services/okter.py`: `start_eller_fortsett_okt(quiz)`, `start_eller_fortsett_okt(notat=…)` for øving, `lagre_svar` og `lever_okt`
- Mock: `ki.generering.MOCK_MAPPE`. Testhjelperen `MockMappe` i `ki/tests_generering.py` viser formatet (`manifest.json` med `standard` og `filer`, og `<dok>/<nivå>.json`). For seed-testen lages en mappe der de tre testdokumentenes sha256 peker på hvert sitt dokument.
- README: avsnittet «Testmodus og mock-svar» finnes. Det nye avsnittet legges før det.

## Tasks & Acceptance

**Execution:**
- [x] `kontoer/testbruker.py`, `kontoer/views.py`, `templates/kontoer/logg_inn.html` -- konstantene og boksen på S1.
- [x] `studier/management/commands/seed_testdata.py` -- kommandoen etter datasettet over.
- [x] `README.md` -- avsnittet «Testbruker».
- [x] `studier/tests/test_seed.py` -- én test per rad i matrisen, pluss at README-en inneholder `EPOST` og `PASSORD`.

**Acceptance Criteria:**
- Gitt en tom database og mock-svar, når `seed_testdata` kjøres to ganger, så har testbrukeren nøyaktig samme antall emner, notater, quizer, økter per type og status, og feilbankrader (åpne og lærte) etter begge kjøringene.
- Gitt testbrukeren etter seed, når S7 for HTML-notatet vises, så har den dekningsgrad per nivå, «Øv på feil (1)», et quizkort med «Påbegynt – spørsmål 4 av 10» og to rader i historikken.

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne

## Implementation Notes

- **Implementert av en underagent.** Review med tre reviewere på Opus.
- **Kommandoen:**
  - `seed_testdata` kaller `ki.tving_testmodus()` og sjekker mock-svarene før noe endres.
  - Deretter lager eller nullstiller den testbrukeren og bygger datasettet gjennom tjenestene. Svarene velges på `er_riktig`.
  - Ingen ytre transaksjon, så ingen transaksjon står åpen under generering.
- **Avvik fra den frosne teksten:** det påbegynte forsøket på middels har **4 svar, ikke 3**. Fremdriften på S3 og S7 regner «spørsmål N» som antall svar (`max(antall_svar, 1)`, låst av `test_fortsette.test_samme_fremdrift_fra_annen_klient`). Bare 4 svar gir «Påbegynt – spørsmål 4 av 10», som akseptansekriteriet krever. Den frosne teksten sier både «3 svar» og «spørsmål 4 av 10», og det kan ikke begge stemme. Tatt opp med Magnus.
- **S1:** boksen «Testbruker» over skjemaet i testmodus, med konstantene fra `kontoer/testbruker.py`.
- **Tester:** 14 i `studier/tests/test_seed.py`, med en midlertidig mock-mappe der shaene til de tre testdokumentene peker på hvert sitt dokument, og midlertidig `MEDIA_ROOT`.
- **Etter review:**
  - Forhåndssjekken dekker nå testdokumentene, at `manifest.json` kan leses, shaene i manifestet og nivåfilene som brukes, før noe slettes.
  - En deaktivert testbruker aktiveres igjen.
  - Nettverkstesten kjører med testmodus slått av.
  - Nye tester for `KIFeil` → `CommandError`, forhåndssjekken og deaktivert bruker.

## Spec Change Log

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 26.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| V1 | `NettverkTest` beviser ikke at seed tvinger testmodus, fordi testkjøreren alt gjør det | medium | Filed gap, bekreftet: `TestmodusRunner` kaller `tving_testmodus()` | patch |
| V2 | Grenen `KIFeil` → `CommandError` er ikke testet | low | Filed gap: ingen test lager en ødelagt nivåfil | patch |
| V3 | En feil etter `_klargjor_bruker` etterlater halve data | medium | Samme rot som B1/E1–E4: forhåndssjekken er for smal | patch (med B1) |
| B1 | Feil midt i kjøringen etterlater testbrukeren med halve data | medium | Bekreftet. Emnene slettes før generering, og bare `manifest.json` sjekkes først | patch (forhåndssjekk) |
| B2 | Forhåndssjekken sjekker ikke at mock-svarene hører til testdokumentene | medium | Bekreftet: ukjent sha gir standarddokumentet og `forhandslagret=True` uten feil | patch (med B1) |
| E1 | Unntak etter `_klargjor_bruker` etterlater et halvt emne | medium | Samme rot som B1 | patch (med B1) |
| E2 | Manglende nivåfil oppdages først etter slettingen | medium | Samme rot som B1 | patch (med B1) |
| E3 | Manglende testdokument gir traceback etter slettingen | medium | Samme rot som B1 | patch (med B1) |
| E4 | Ukjent sha gir quiz fra feil dokument | medium | Samme som B2 | patch (med B1) |
| B3 | 4 svar i stedet for 3 i det påbegynte forsøket | low | Den frosne teksten motsier seg selv (3 svar og «spørsmål 4 av 10»). Koden oppfyller akseptansekriteriet. Rettingen er å endre spec-en, som avvises her. Tatt opp med Magnus | avvist |
| B4 | Ingen vakt mot å kjøre seed mot en ikke-testdatabase | false | Appen kjøres bare lokalt (AD-22, ingen hosting), og innloggingen er offentlig i README-en med vilje | avvist |
| B5 | Returverdiene fra tjenestene sjekkes ikke | false | Tilstandene (`None`, `False`, `StopIteration`) kan ikke nås med datasettet som nettopp ble laget, og de feiler høylytt hvis de nås | avvist |
| B6 | En deaktivert testbruker aktiveres ikke igjen | low | Bekreftet. Én linje | patch (med E6) |
| E6 | Samme som B6 | low | Samme som B6 | patch |
| B7 | Feilmeldingen sier «hent ki/mock/ fra repoet», men mappen er ikke committet ennå | low | Blir riktig når Magnus committer `ki/mock/`, og spec-en beholder 6.1 i review til da. `migrate` i README hører til 6.2 | avvist |
| B8 | Passordet legges i konteksten også utenfor testmodus | false | Passordet står offentlig i README-en, så det er ingenting å lekke | avvist |
| B9 | Mangler tester for `KIFeil`, andre brukere og deaktivert bruker | low | `KIFeil` og deaktivert bruker dekkes av V2 og B6. Seed rører bare `bruker.emner` | delvis patch |
| B10 | Alle tidsstempler er i samme sekund | low | Kosmetisk i historikken. Rettingen krever en ny parameter i tjenestene eller brudd på AD-1 | avvist |
| B11 | Testene skriver navnene på nytt i stedet for å importere dem | low | Bare testkode | avvist |
| E5 | Samme som B7 | low | Samme som B7 | avvist |
| E7 | To samtidige kjøringer gir `IntegrityError` | low | Feiler høylytt, og kommandoen kjøres for hånd én gang | avvist |
