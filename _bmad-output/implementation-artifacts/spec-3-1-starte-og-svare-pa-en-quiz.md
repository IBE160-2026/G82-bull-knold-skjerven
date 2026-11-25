---
title: 'Story 3.1: Starte og svare på en quiz'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '47476b24f0792ffa6087fb9f7d5733ad6cebf728'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Quizer kan lages og vises som kort på S7, men ingen kan ta dem. Det finnes ingen økt og ingen side for å svare (FR-17, FR-18).

**Approach:** Bygg `studier/services/okter.py` med `start_eller_fortsett_okt` og `lagre_svar` (AD-6, AD-16, AD-17). Lag S9 (`/okter/<id>/sporsmal/<nr>/`) med vanlige POST-skjemaer for Forrige og Neste (AD-13), og knappen «Ta quiz» på quizkortet. Etter generering åpnes quizen på spørsmål 1 i stedet for S7.

## Boundaries & Constraints

**Beslutninger 25.11 (Christian):**
- **Enkelt S10-skall:** `/okter/<id>/lever/` (GET) har h1 «Se over og lever» og én lenke per spørsmål til S9, for eksempel «Spørsmål 4 – ikke besvart» eller «Spørsmål 2 – besvart». Ingen Lever-knapp ennå (story 3.3). Brødsmuler: Oversikt › emne › notat › Se over og lever. En annens økt gir 404.
- **Knappeteksten er «Ta quiz»** (UX-designet), ikke «Ta quizen».
- **CSS bygges på nytt** som i story 1.6:
  - Installer `tailwindcss@4.3.5` og `@tailwindcss/cli@4.3.5` midlertidig i scratchpad med npm, bygg `static/css/input.css` til `static/css/app.css` (minifisert), og commit resultatet.
  - Nye stiler som trengs (flashcard, valgt alternativ med 2 px `accent-strong`-kant og `surface-muted`, knapper i full bredde under `md`) legges i `input.css` med tokenene som finnes, eller som Tailwind-klasser i malene.

**Always:**
- **`start_eller_fortsett_okt(quiz)`** gir den påbegynte `forsok`-økten for quizen, eller lager en ny i `transaction.atomic()`.
  - En ny økt har `type=forsok`, `status=pabegynt`, `notat=quiz.notat` og `quiz`.
  - `innhold` er `[{"sporsmal": id, "alternativer": [id, id, id]}, …]`: spørsmålene i quizens rekkefølge, alternativene stokket. Listen endres aldri etterpå.
  - En `IntegrityError` fra den betingede unike begrensningen (to samtidige kall) gir den eksisterende økten.
- **Første ubesvarte spørsmål:** nr (1-basert) for første element i `innhold` uten `Svar`. Er alle besvart, brukes nr 1.
- **`lagre_svar(okt, sporsmal, alternativ)`** er eneste sted som skriver `Svar`.
  - Den avviser (`ValueError` eller en egen unntaksklasse) hvis økten ikke er `pabegynt`, hvis spørsmålet ikke står i `okt.innhold`, eller hvis alternativet ikke hører til spørsmålet.
  - Ellers kjører den `update_or_create` på (`okt`, `sporsmal`) og oppdaterer `sist_endret`.
- **Start:** POST `/quizer/<id>/start/` (quizen slås opp med `hent_egen`) kaller `start_eller_fortsett_okt` og sender til første ubesvarte spørsmål. Hvert quizkort på S7 har et POST-skjema med knappen «Ta quiz».
- **Etter generering:** når `/jobber/<id>/steg/` ser at jobben er `ferdig`, kaller den `start_eller_fortsett_okt(jobb.quiz)` og gir `HX-Redirect` til `/okter/<id>/sporsmal/1/`. En annen fane som spør etterpå, får den samme økten. S8 (GET) for en ferdig jobb sender fortsatt til S7, så ingen GET endrer data.
- **S9 (GET):**
  - Øverst står «Laget av KI (<visningsnavn>). Spørsmålene kan inneholde feil.», med modellen fra quizen.
  - Så kommer «Spørsmål N av M» som tekst, og reiseruten (`.reiserute` med bredde N/M og et fåre-SVG med `aria-hidden`).
  - Spørsmålet står som `<legend>` i en `<fieldset>`. Tre radioknapper i `<label>`, minst 44 px høye, står i rekkefølgen fra `innhold`. Et lagret svar er valgt.
  - Når `quiz.sprak` ikke er `nb`/`no`/`nn`, får spørsmål og alternativer `lang="{{ quiz.sprak }}"`.
  - `<title>` er «Spørsmål N av M – <notat>». `base.html` legger til « – FåreQuiz».
  - Brødsmuler: Oversikt › emne › notat › «Spørsmål N av M». Tilbake går til notatet.
  - Under spørsmålet står lenken «Se over og lever» (S10).
- **S9 (POST)** med `retning` ∈ {`forrige`, `neste`} og valgfritt `alternativ`:
  - Med `alternativ` kalles `lagre_svar`. Uten `alternativ` lagres ingenting, og brukeren navigeres likevel.
  - Forrige på nr 1 blir på nr 1. Neste på siste spørsmål sender til S10.
  - Etter navigering har spørsmålet fokus (`tabindex="-1"` og `autofocus` på spørsmålet).
  - `alternativ` slås opp med `hent_egen(Alternativ, …)`. Er det en annen brukers, eller finnes det ikke, gir det 404.
  - Avvist svar: et eget alternativ som ikke er ett av spørsmålets tre i `innhold`, eller som `lagre_svar` avviser. Da vises S9 for samme nr med «Svaret ble ikke lagret. Sjekk nettet og prøv igjen.» i `role="alert"` ved knappene (status 400), og ingenting lagres.
  - POST til en levert økt sender til S10 (`/okter/<id>/lever/`). Story 3.3 endrer dette til resultatsiden.
  - Ukjent `nr` (0, over M, ikke tall) gir 404.
- **AD-20:** malen og konteksten for S9 får aldri `er_riktig` eller `begrunnelse`. Alternativene sendes som (id, tekst). Rekkefølgen kommer fra den stokkede listen.
- **Tilgang (AD-8):** en annen brukers quiz, økt eller alternativ gir 404 («Fant ikke siden»).
- **Universell utforming:**
  - S9 virker med bare tastatur, og piltastene virker i radiogruppen (vanlige radioknapper).
  - Ingen vannrett rulling ved 360 px.
  - Under `md` er Forrige og Neste like brede som skjermen og står nederst i innholdet.
- Ingen JavaScript eller HTMX på S9 i 3.1. Bare vanlige skjemaer.

**Never:**
- Ingen levering, retting, resultatside eller feilbank (3.2, 3.3). Ingen «Fortsett»- eller «Ta på nytt»-tilstand på quizkortet (3.4, 3.5).
- Ikke endre modellene, migreringene eller `ki`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Start | POST start for quiz med 5 spørsmål | Ny økt `forsok`/`pabegynt`, `innhold` med 5 spørsmål i quizens rekkefølge og hvert med sine 3 alternativ-ID-er, redirect til nr 1 | N/A |
| Start igjen | påbegynt økt med svar på 1 og 2 | Ingen ny økt, samme `innhold`, redirect til nr 3 | N/A |
| Samtidig start | `IntegrityError` ved opprettelse | Den eksisterende økten | N/A |
| Neste med svar | nr 2, gyldig `alternativ` | `Svar` lagret, `sist_endret` oppdatert, redirect til nr 3 | N/A |
| Endre svar | nytt alternativ på samme spørsmål | Fortsatt ett `Svar`, nå med det nye alternativet | N/A |
| Uten svar | Neste uten `alternativ` | Ingen `Svar`, redirect til neste | N/A |
| Forrige på 1 | nr 1, Forrige | Redirect til nr 1 | N/A |
| Neste på siste | nr M | Svar lagret, redirect til S10 | N/A |
| Alternativ fra annet spørsmål | ID fra spørsmål 3 sendt på nr 2 | Ingenting lagret, S9 nr 2 med meldingen | 400 |
| Annens alternativ | ID fra en annen brukers quiz | Ingenting lagret | 404 |
| Levert økt | `status=levert`, POST | Ingenting lagret, redirect bort fra S9 | N/A |
| Annens økt eller quiz | GET/POST S9, POST start | Ingenting endres | 404 |
| Ukjent nr | 0, M+1, «x» | Ingenting endres | 404 |
| Etter generering | siste steg ferdig, og en annen fane spør etterpå | `HX-Redirect` til `/okter/<id>/sporsmal/1/` for begge, én økt | N/A |
| Fasit skjult | S9-HTML for et spørsmål | Riktig alternativ skilles ikke ut med klasse, `data-*` eller fast posisjon. Ingen `begrunnelse` | N/A |
| Språk | `quiz.sprak="en"` | `lang="en"` på spørsmål og alternativer. Ingen `lang` for `nb` | N/A |

</frozen-after-approval>

## Code Map

- `studier/models.py` -- `Okt` (`innhold` JSONField, betingede `UniqueConstraint`-er), `Svar` (`UniqueConstraint(okt, sporsmal)`), `Okttype` og `Oktstatus`. Ingen endring.
- `studier/tilgang.py` -- `hent_egen`/`egne`. `EIERVEI` har `Okt`, `Svar` og `Alternativ`.
- `studier/services/generering.py` -- mønster for tjenestemodul, `transaction.atomic` og logger.
- `studier/views.py:285-312` -- `steg`: `HX-Redirect` til S7 ved `ferdig` (linje 311) byttes. `jobb` (S8 GET) for ferdig jobb beholder redirect til S7. `notat` (S7) og `_emne_kontekst(emne, siste, notat=…)` for brødsmuler.
- `studier/urls.py` -- nye ruter `quizer/<pk>/start/`, `okter/<pk>/sporsmal/<int:nr>/` og `okter/<pk>/lever/`.
- `templates/studier/notat.html` -- quizkortene får «Ta quiz»-skjemaet.
- `templates/base.html` -- `<title>` er allerede `{% block title %}{% endblock %} – FåreQuiz`.
- `templates/studier/last_opp.html:42` og `static/css/input.css` (`.reiserute`) -- reiseruten.
- `ki.visningsnavn(modell)` -- modellnavnet i KI-merket.
- Prototype S9: `_bmad-output/planning-artifacts/ux-designs/ux-G82-bull-knold-skjerven-2026-11-11/prototype/index.html:440-466`. Fåre-symbolet `#faar-ballong` står øverst i samme fil. DESIGN.md i samme mappe har flashcard og option-card.
- `studier/tests/test_generering.py` -- `GenereringTestCase`, `generer_synkront`, `_raatt`. 2.4-testene som sjekker `HX-Redirect` til S7 for ferdig jobb, må oppdateres.

## Tasks & Acceptance

**Execution:**
- [x] `studier/services/okter.py` -- `start_eller_fortsett_okt`, `forste_ubesvarte`, `lagre_svar` -- AD-6, AD-16, AD-17
- [x] `studier/views.py`, `studier/urls.py` -- start, S9 GET/POST, S10-skallet, endringen i `steg`
- [x] `templates/studier/sporsmal.html` (S9), `templates/studier/lever.html` (S10-skall), `notat.html`, `static/css/input.css` og `static/css/app.css` (bygget)
- [x] `studier/tests/test_okter.py` -- én test per rad i matrisen. Oppdater 2.4-testene for `HX-Redirect`.

**Acceptance Criteria:**
- Gitt en ferdig quiz på S7, når brukeren trykker «Ta quiz», svarer på alle spørsmål med Neste og går tilbake med Forrige, så er svarene valgt når spørsmålene vises igjen, og alternativene står i samme rekkefølge hver gang.
- Gitt S9 i headless Edge ved 360 px, når siden vises, så er det ingen vannrett rulling, og fokus står på spørsmålet etter Neste.

## Implementation Notes

- **Tjenesten:** `studier/services/okter.py` har `start_eller_fortsett_okt`, `forste_ubesvarte`, `lagre_svar`, og hjelperne `element(okt, nr)` og `besvarte(okt)`. `lagre_svar` hever `SvarAvvist` (en `ValueError`) eller underklassen `OktErLevert`. Første skriving i transaksjonen er `filter(pk, status=pabegynt).update(sist_endret=…)`, så en samtidig levering (3.3) ikke kan komme mellom statussjekken og svaret.
- **S9:** spørsmålet er `<legend class="flashcard" tabindex="-1" autofocus>`. Ved avvist svar har meldingen `autofocus` i stedet. Fieldset har `min-w-0`, ellers gir lange ord vannrett rulling (fieldset har `min-inline-size: min-content`).
- **Enter i radiogruppen:** første knapp i skjemaet er en skjult `retning=neste`, så Enter går videre og ikke tilbake. Sjekket i headless Edge.
- **Ukjent `retning`** (tom eller annen verdi) gir 400 uten lagring. Spec-en sier ikke noe om dette.
- **S7-testene fra 2.4/2.6** som sa at `/quizer/` ikke fantes på siden, sjekker nå at de eneste `/quizer/`-adressene er «Ta quiz»-skjemaene.
- **CSS:** bygget med `tailwindcss@4.3.5` og `@tailwindcss/cli@4.3.5` installert i scratchpad. `input.css` ble kopiert dit (så `@import "tailwindcss"` finnes), og CLI-en ble kjørt fra prosjektroten. Uten endringer i `input.css` ga det samme `app.css` som før, bortsett fra `.py-1`, som manglet fra 2.6.
- **Manuell sjekk (headless Edge, midlertidig server med egen database):** «Ta quiz» på S7 åpner nr 1 med fokus på `#sporsmal`. Tab til radio, pil ned velger, Enter går til nr 2 med fokus på spørsmålet. Neste uten svar, Forrige to ganger, og svaret på nr 1 er valgt igjen. `scrollWidth == clientWidth` på 360 og 320 px for S9, S10 og S7. Knappene er 328 px brede under `md` og står på én linje ved 1024 px. Valgt alternativ har 2 px kant og `surface-muted`. Neste på nr 5 går til S10. Ingen konsollfeil.

- **Etter review (pass 1):**
  - «Se over og lever» er nå en sendeknapp (`retning=lever`) som lagrer valgt svar før S10.
  - Nye tester for `autofocus` ved avvist svar, for CSRF-feltet i de nye skjemaene og for språkvariantene.
  - 353 tester grønne, 1 hoppet over.

## Spec Change Log

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 25.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | «Se over og lever» er en vanlig lenke, så et valgt, ulagret svar går tapt | medium | Bekreftet: `<a>` inne i skjemaet sender ingen POST. Rettes med en sendeknapp som ser ut som lenken (`retning=lever`), som lagrer og sender til S10 | patch |
| B2 | `steg` sender til nr 1, mens «Ta quiz» sender til første ubesvarte | low | Det frosne punktet sier `/okter/<id>/sporsmal/1/` | avvist |
| B3 | `steg` kan lage et nytt forsøk når en ferdig jobb spørres etter levering | medium | Ekte, men kan først skje når 3.3 kan levere. Samme som E1 | defer |
| B4 | Viewet sjekker alternativet to ganger, så `except SvarAvvist` blir død kode og `except OktErLevert` er utestet | low | Dobbeltsjekken er forsvar i dybden. Testen for `OktErLevert`: se V3 | avvist |
| B5 | `SVAR_IKKE_LAGRET` nevner nettet | low | Teksten står i AC-en og i det frosne punktet | avvist |
| B6 | Ukjent `retning` gir en 400 i ren tekst | low | Kan bare nås med en forfalsket POST | avvist |
| B7 | GET på S9 for en levert økt viser et skjema som kan redigeres | medium | Kan først skje med levering i 3.3. Samme som E4 | defer |
| B8 | Feilmeldingen er ikke koblet til radiogruppen | low | Meldingen har `role="alert"` og fokus, så den leses opp. Kan bare nås ved avvist svar | avvist |
| B9 | Svarkortene har ingen egen fokusmarkering | low | Radioknappen har nettleserens fokusring (WCAG 2.4.7 er oppfylt) | avvist |
| B10 | Den skjulte Enter-knappen kan oppføre seg ulikt i nettleserne, og testnavnet lover for mye | maybe-false | Kontrollert i Edge. Safari er ikke testet. Ville bare vært low | avvist |
| B11 | SVG-en har faste farger og står inline | low | Appen har ikke mørk modus. Fargene er de samme som i prototypen | avvist |
| B12 | `_lang` regner `nn` som norsk og normaliserer ikke store bokstaver | low | Det frosne punktet sier `nb`/`no`/`nn` → ingen `lang`. «EN» som `lang` er gyldig | avvist |
| B13 | Mangler tester for innlogging, HEAD, start etter levering og tomt `innhold` | low | Innlogging gjelder globalt og er testet. En quiz har alltid 5–30 spørsmål. Start etter levering hører til 3.3 og 3.4 | avvist |
| E1 | `steg` lager et nytt forsøk etter levering | medium | Samme som B3 | defer |
| E2 | Notatet slettes mellom `refresh_from_db` og `objekt.quiz` | low | Et vindu på millisekunder | avvist |
| E3 | `IntegrityError` fra en slettet fremmednøkkel gir 500 | low | Samme som E2 | avvist |
| E4 | GET på S9 for en levert økt | medium | Samme som B7 | defer |
| E5 | En `oving`-økt kan åpnes i S9 | false | Epic 4 gjenbruker S9 for `oving` med vilje (epic-konteksten) | avvist |
| E6 | Samtidig sletting gir 500 i stedet for 404 | low | Samme som E2 | avvist |
| V1 | Ingen test for at bare meldingen har `autofocus` ved avvist svar | medium | Godtatt som levert | patch |
| V2 | Ingen test for CSRF-feltet i «Ta quiz» og S9 | medium | Godtatt som levert. Uten feltet gir alle svar 403 | patch |
| V3 | `except OktErLevert` i viewet er ikke testet | medium | Kan først nås med levering i 3.3 | defer |
| V4 | `_lang` er bare testet med `en` og `nb` | low | Godtatt som levert. Direkte testtillegg | patch |

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne

**Manual checks:**
- Headless Edge mot en midlertidig server: start en quiz fra S7, Neste/Forrige med og uten svar, sjekk `document.activeElement` etter Neste og `scrollWidth <= clientWidth` ved 360 px.
