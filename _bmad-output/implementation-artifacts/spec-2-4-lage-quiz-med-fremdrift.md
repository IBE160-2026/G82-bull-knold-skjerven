---
title: 'Story 2.4: Lage quiz med fremdrift'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 1
baseline_commit: '4dfd11b7a9b53b3681ffea52cc6da14850ec8bb2'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Notatsiden (S7) er bare et skall. Studenten kan laste opp et notat, men ikke lage en quiz fra det (FR-11–FR-14).

**Approach:** Skjema for ny quiz på S7. `studier.services.generering` med jobbkjeden fra AD-9. Generering (S8) med tre fremdriftssteg som HTMX driver ett steg om gangen. Quizkort på S7 når quizen er lagret.

## Boundaries & Constraints

**Always:**
- **Tjenesten `studier/services/generering.py`** er eneste sted som lager `Genereringsjobb` og `Quiz` (AD-1):
  - `aktiv_jobb(notat)`: jobb med status som ikke er `ferdig` eller `feilet`. En aktiv jobb med `startet` eldre enn 120 s settes til `feilet`/`timeout` og regnes ikke som aktiv.
  - `opprett_jobb(notat, vanskelighetsgrad, antall)`: i `transaction.atomic()` gir den den aktive jobben hvis den finnes, ellers lager den en ny (FR-14).
  - `kjor_steg(jobb_id)`: tar jobben med `filter(pk, status=S, i_gang=False).update(i_gang=True)`. Endres 0 rader, eller er jobben ferdig eller feilet, gjøres ingenting. Ellers kjøres ett steg, og `i_gang` settes tilbake til `False`, også ved feil.
    - `leser`: `ki.les_fil(notat.fil.path)`, så `lager`.
    - `lager`: `les_fil` på nytt og `ki.generer(innhold, nivå, antall, timeout=gjenstående av 120 s)`. Lagrer `raatt_svar`, `forhandslagret`, `modell` og `prompt_versjon`, så `sjekker`.
    - `sjekker`: `ki.sjekk(raatt_svar, antall)`. Formatfeil i runde 1 gir `lager` med `runde=2`. I runde 2 blir jobben `feilet`/`format` (FR-13). Et gyldig utkast lagres i én transaksjon som `Quiz` (`jobb`, `vanskelighetsgrad`, `sprak`, `modell`, `prompt_versjon`, `forhandslagret`), `Sporsmal` med `begrunnelse` og tre `Alternativ`, og jobben blir `ferdig`.
    - En `KIFeil` gir `feilet` med `feilkode=kode`. Den logges med jobb-ID og kode, aldri med filinnhold.
  - `generer_synkront(notat, vanskelighetsgrad, antall)`: `opprett_jobb` og `kjor_steg` i løkke, høyst 5 steg. Gir `Quiz`, eller hever `KIFeil(feilkode)` når jobben feiler.
- **AD-19:** ingen `ki`-kall (også `sjekk`) mens en transaksjon er åpen. Hver statusovergang committes for seg. Filinnhold lagres aldri på jobben eller i sesjonen.
- **S7 (`/notater/<id>/`, GET og POST):**
  - Skjemaet har tre radioknapper (lett, middels, vanskelig) i `<fieldset>` med `<legend>Vanskelighetsgrad</legend>`, og middels er valgt.
  - Tallfeltet «Antall spørsmål» har `min=5`, `max=30`, verdien 10 og hjelpeteksten «Fra 5 til 30.», koblet med `aria-describedby`.
  - Knappen heter «Lag quiz». Tekstene kommer fra prototypen.
  - Skjemaet står øverst når notatet ikke har quiz, sammen med «Lag en quiz for å komme i gang». Ellers står det under quizkortene.
  - POST med gyldige valg kaller `opprett_jobb` og sender til S8. Antall utenfor 5–30 eller ikke et tall gir «Velg et antall fra 5 til 30.» ved feltet (`role="alert"`, `autofocus`, status 200), og ingen jobb lages.
  - Quizkortene står nyeste først med «Middels, 10 spørsmål», dato og «Laget av KI». De er ikke lenker ennå (S9 kommer i Epic 3).
  - Har notatet en aktiv jobb, står «En quiz lages nå.» med lenke til S8.
- **S8 (`/jobber/<id>/`, GET):**
  - h1 «Lager quiz». Brødsmuler: Oversikt › emne › notat › Lager quiz.
  - Stegene «Leser filen», «Lager spørsmål» og «Sjekker quizen» står i en `<ol>`. Hvert steg er markert ferdig, pågår eller venter med ikon (`aria-hidden`) og tekst, for eksempel «Leser filen (ferdig)».
  - Under står «Dette kan ta opptil to minutter. Hold fanen åpen til quizen er klar.» (beslutning 25.11 etter review, E6: stegene kjører bare mens S8 er åpen, så prototypeteksten «Du kan lukke fanen og komme tilbake» lovet for mye) og knappen «Lag quiz» med `aria-disabled="true"`. `<noscript>` forklarer at JavaScript må være på.
  - En ferdig jobb sender til S7.
- **`/jobber/<id>/steg/` (bare POST):**
  - Kaller `kjor_steg` og gir fragmentet `templates/studier/_fremdrift.html`.
  - Er jobben i gang, har fragmentet et element med `hx-post` som spør igjen. Spørringen går med en gang etter et fullført steg, og med `delay:1s` når 0 rader ble endret.
  - Ferdig jobb gir `HX-Redirect` til S7.
  - `aria-live="polite"`-regionen ligger fast på S8, og bare innholdet byttes.
- **HTMX:** `static/js/htmx.min.js` lastes på S8 (`skript`-blokken med `{{ block.super }}`). CSRF-tokenet sendes med `hx-headers` på `<body>` i `base.html`.
- Jobber og notater slås opp med `hent_egen`, så andres jobb gir 404.

**Never:**
- Ingen feiltekst per kode, ingen «Prøv igjen» og ingen sluttfragment for slettet jobb eller notat (story 2.5). En feilet jobb viser bare «Klarte ikke å lage quizen.» med `role="alert"` og lenke tilbake til notatet.
- Ingen testmodus-merknad på quizkort og ingen modellnavn i merket (story 2.6). Ingen dekningsgrad (Epic 5).
- Ikke endre `ki`, modellene eller migreringene.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Lag quiz | POST middels, 10 | Ny jobb (`leser`, runde 1), redirect til S8 | N/A |
| Ugyldig antall | 4, 31, «abc», tomt | Ingen jobb | «Velg et antall fra 5 til 30.» ved feltet |
| Aktiv jobb finnes | POST «Lag quiz» på S7 (ny fane eller dobbeltklikk) | Ingen ny jobb, redirect til S8 for den aktive jobben | N/A |
| Hele kjeden | tre steg-kall | `ferdig`, én quiz med N spørsmål × 3 alternativer, ett riktig, `HX-Redirect` til S7 | N/A |
| Formatfeil én gang | `sjekk` feiler i runde 1 | `lager`, `runde=2`, så quiz | N/A |
| Formatfeil to ganger | `sjekk` feiler i runde 2 | `feilet`/`format`, ingen quiz | Logges, fragment med feil |
| `KIFeil` i `leser`/`lager` | f.eks. `api_feil` | `feilet`/kode, ingen quiz | Logges, fragment med feil |
| Samtidige kall | to steg-kall med `i_gang=True` | Ett `ki`-kall, én quiz | Det andre gir gjeldende fragment |
| Gammel jobb | aktiv, `startet` 121 s siden | `aktiv_jobb` gir `None`, jobben er `feilet`/`timeout` | N/A |
| Annens jobb | GET S8 eller POST steg | Ingenting endres | 404 |

</frozen-after-approval>

## Code Map

- `studier/models.py` -- `Genereringsjobb`, `Jobbstatus`, `Feilkode`, `Quiz`, `Sporsmal`, `Alternativ` finnes. Ingen migrering trengs.
- `ki/__init__.py` -- `les_fil(sti) -> Innhold`, `generer(innhold, vanskelighetsgrad, antall, timeout) -> RaattSvar`, `sjekk(raatt, antall) -> QuizUtkast` og `KIFeil(kode)`. `generer` hever `ValueError` ved ugyldig valg.
- `ki/mock/` finnes ikke ennå (story 2.2 venter på Magnus). I testmodus gir `generer` derfor `api_feil`. Testene må stubbe `ki.generer` eller patche `ki.generering.MOCK_MAPPE` som i `ki/tests_generering.py:55-93`.
- `studier/services/notater.py` -- mønster for tjenestemodul, logger og transaksjon.
- `studier/tilgang.py` -- `hent_egen(Genereringsjobb, pk, bruker)`. `EIERVEI` har modellen.
- `studier/views.py:146-154` -- `notat` (S7-skallet) utvides. Gjenbruk `_emne_kontekst`, og legg til notatet som brødsmule for S8.
- `studier/urls.py` -- nye ruter `jobber/<pk>/` (`jobb`) og `jobber/<pk>/steg/` (`steg`).
- `studier/forms.py` -- nytt `NyQuizForm`.
- `templates/studier/notat.html`, `ny_emne.html:15-19` (feilmønster) og `emne.html:27-38` (kortstil).
- `templates/base.html` -- `<body>` får `hx-headers`. `skript`-blokken laster `meny.js`.
- `farequiz/feilmeldinger.py` -- nye tekster for antall og feilet jobb.
- `studier/tests/fabrikk.py` og `studier/tests/test_last_opp.py` (`MedFilerTestCase`, `_innlogget`) -- testmønstre.
- Prototype `_bmad-output/planning-artifacts/ux-designs/ux-G82-bull-knold-skjerven-2026-11-11/prototype/index.html:369-427` (S7-skjema, quizkort og S8).
- `static/css/input.css` -- bygg med `sh scripts/bygg-css.sh` hvis nye Tailwind-klasser trengs.

## Tasks & Acceptance

**Execution:**
- [x] `farequiz/feilmeldinger.py` -- `ANTALL_UGYLDIG` og `GENERERING_FEILET`
- [x] `studier/services/generering.py` -- `aktiv_jobb`, `opprett_jobb`, `kjor_steg`, `generer_synkront` -- AD-9, AD-19
- [x] `studier/forms.py` -- `NyQuizForm`
- [x] `studier/views.py`, `studier/urls.py` -- S7 GET/POST, S8 og stegendepunktet
- [x] `templates/studier/notat.html`, `templates/studier/jobb.html`, `templates/studier/_fremdrift.html`, `templates/base.html`
- [x] `studier/tests/test_generering.py` -- én test per rad i matrisen, pluss `generer_synkront` og at ingen transaksjon er åpen under `ki`-kall

**Acceptance Criteria:**
- Gitt et notat uten quiz, når S7 vises, så står skjemaet øverst med middels og 10 valgt.
- Gitt en ferdig jobb, når S7 vises, så står quizkortet med nivå, antall, dato og «Laget av KI».
- Gitt S8 i en nettleser med JavaScript, når siden lastes, så går stegene fra venter til ferdig, og siden ender på S7.

## Implementation Notes

- **`studier/services/generering.py`:**
  - `kjor_steg` gir `True`/`False` for om et steg ble kjørt. Den kaller `aktiv_jobb` først, så en jobb som henger med `i_gang=True`, også blir satt til timeout.
  - Alle overganger er betinget av at statusen ikke har endret seg (`_overgang`).
  - Et unntak som ikke er `KIFeil`, gir `feilet`/`api_feil`. Loggen har bare jobb-ID, steg og unntakstype.
  - Gjenstående tid regnes ut etter `les_fil`.
  - `opprett_jobb` serialiseres av `transaction_mode: IMMEDIATE`, fordi `select_for_update` er uten virkning på SQLite.
- **S8:**
  - `#fremdrift` (`aria-live`) får innholdet fra `_steg.html`.
  - Spørreelementet `#spor` (`_fremdrift.html`) ligger utenfor og sender `vist` (statusen siden viser).
  - `#fremdrift` byttes med `hx-swap-oob` bare når statusen er endret, så skjermlesere ikke leser opp de samme stegene på nytt (review B2).
- **Ingen ny CSS:** bare klasser som allerede finnes i `app.css`.
- **Verifisert:**
  - ruff, `makemigrations --check` og 288 tester grønne, 1 hoppet over (`EkteMockfilerTest`, som venter på 2.2). 32 av testene er nye i `test_generering.py`.
  - Headless Edge via CDP mot en midlertidig server (egen database, media og mock-mappe, testmodus tvunget). Med «Lett, 6» gikk S7 → S8 gjennom alle tre stegene og endte på S7 med kortet «Lett, 6 spørsmål · Laget av KI». `#fremdrift` ble byttet én gang per statusendring, og konsollen var uten feil.
  - Innloggingen ble gjort med en sesjonskapsel, fordi skriptet ikke fikk sendt innloggingsskjemaet (ikke undersøkt nærmere). Den manuelle sjekken med bare tastatur er ikke gjort.

## Spec Change Log

- **25.11, pass 1, E6 (intent_gap):** Hjelpeteksten på S8 lovet at fanen kunne lukkes. Christian valgte ny tekst: «Dette kan ta opptil to minutter. Hold fanen åpen til quizen er klar.» Det frosne Always-punktet for S8 er endret. Med den gamle teksten fikk en bruker som kom tilbake etter 120 s en feilet jobb og ingen quiz. Etter brukerens valg ble koden ikke rullet tilbake. Bare teksten rettes, sammen med patchene fra pass 1. KEEP: hele tjenesten, viewene, malene og de 29 testene slik de er.

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 25.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | HTMX-kjeden håndterer ikke 5xx, nettfeil eller utløpt økt | low | Stemmer: HTMX bytter ikke ved feil, og spørringen stopper. Appen kjøres lokalt, og 500 kommer bare fra feil i koden. Økten varer langt over 120 s. Rettelsen krever egen feilhåndtering i JavaScript | avvist |
| B2 | Live-regionen leser opp den samme listen hvert sekund når jobben er i gang et annet sted | medium | Bekreftet: med `i_gang=True` (ny fane, eller S8 lastet på nytt mens `lager` kjører) byttes en identisk `<ol>` inn i `aria-live` hvert sekund i opptil 120 s | patch |
| B3 | 5, 30 og 10 står hardkodet i malen og meldingen | low | Intervallet er låst av FR-11 og PRD-en og ventes ikke endret | avvist |
| B4 | Ugyldig eller manglende `vanskelighetsgrad` gir Djangos standardtekst uten `id` og fokus | low | Kan bare nås med en forfalsket POST, fordi radiogruppen alltid har et valg. `LANGUAGE_CODE="nb"`, så teksten er norsk | avvist |
| B5 | `opprett_jobb` gir en aktiv jobb med andre valg uten beskjed, og `generer_synkront` kan gi feil nivå | low | UI-delen er FR-14 og står i matrisen. Seed kjører jobbene etter hverandre, så det finnes ingen aktiv jobb fra før | avvist |
| B6 | `except Exception` er ikke testet og logger ingen stakk | low | Testen: samme som V1. Stakken er utelatt med vilje, fordi meldingen fra et unntak kan inneholde filinnhold | patch (test, se V1) |
| B7 | Gjenstående tid regnes ut før `les_fil` | low | Bekreftet, men lesing av en fil på høyst 5 MB tar millisekunder. Rettelsen er å flytte én linje | patch |
| B8 | `select_for_update` gjør ingenting på SQLite, så kommentaren er misvisende | low | Bekreftet: det er `transaction_mode: IMMEDIATE` som serialiserer. Kommentaren rettes. At notatet slettes mellom kallene, er for sjeldent | patch (kommentar) |
| B9 | AD-19-testen går bare gjennom tjenesten, ikke gjennom viewene | low | `ATOMIC_REQUESTS=False` står eksplisitt i innstillingene, og viewene åpner ingen transaksjon | avvist |
| B10 | S8 kjører ikke tidsfristsjekken før visning | false | Den første spørringen går ved `load` og kaller `aktiv_jobb` i `kjor_steg`, så jobben vises som feilet etter ett kall | avvist |
| B11 | Testene importerer private hjelpere fra andre testmoduler, og bare året i datoen er sjekket | low | Samme mønster som i 2.3. Ingen funksjonell skade | avvist |
| E1 | Feilsvar stopper spørringen | low | Samme som B1 | avvist |
| E2 | Utløpt økt gir innloggingssiden inne i `#fremdrift` | low | Samme som B1 | avvist |
| E3 | Notat eller jobb slettet underveis gir `DoesNotExist` og 500 | low | Det frosne Never-punktet legger sluttfragmentet for slettet jobb eller notat i story 2.5 | avvist (2.5) |
| E4 | `generer_synkront` får en aktiv jobb med andre valg | low | Samme som B5 | avvist |
| E5 | `generer_synkront` hever `api_feil` straks når jobben er i gang et annet sted | low | Seed kjører alene. Rettelsen krever venting og ny grense | avvist |
| E6 | «Du kan lukke fanen og komme tilbake» stemmer ikke: stegene kjører bare mens S8 spør, så etter 120 s er jobben `feilet`/`timeout` | medium | Bekreftet: et `lager`-kall som er i gang, fullføres, men `sjekker` kjøres først når S8 er åpen igjen. Teksten står i det frosne Always-punktet for S8 | intent_gap |
| E7 | Gjenstående tid regnes ut før `les_fil` | low | Samme som B7 | patch |
| E8 | `_feilet` kan selv feile («database is locked») inne i `except` | low | Sjeldent med én lokal bruker og 20 s ventetid. Krever en ny vakt | avvist |
| E9 | Ugyldig `vanskelighetsgrad` | low | Samme som B4 | avvist |
| V1 | Grenen for uventede unntak i `kjor_steg` har ingen test | medium | Godtatt slik den ble levert: ingen test kaster noe annet enn `KIFeil` | patch |

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne

**Manual checks:**
- Med midlertidig mock-mappe og database: last opp et testdokument, lag en quiz, og se at S8 viser stegene og ender på S7 med quizkortet. Sjekk med bare tastatur.
