---
title: 'Story 3.3: Levere og se resultatet'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '59793717b140581c22382300de75b722c24eca44'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Studenten kan svare på en quiz (3.1), men ikke levere den. Det finnes ingen poengsum og ingen resultatside, og feilbankregelen fra 3.2 blir aldri kalt (FR-17, FR-19, FR-21).

**Approach:** Legg til `lever_okt` i `studier/services/okter.py` med betinget levering (AD-18) og `registrer_svar` per spørsmål. Gi S10 knappen «Lever». Lag resultatsiden S11 (`/okter/<id>/resultat/`) uten fasit, unntatt for lærte spørsmål (AD-20). Ta med de fire punktene fra 3.1 og 3.2 som står i `deferred-work.md`.

## Boundaries & Constraints

**Always:**
- **`lever_okt(okt)`** kjører i én `transaction.atomic()`:
  1. Første skriving er `Okt.objects.filter(pk=okt.pk, status=pabegynt).update(status=levert, levert_tidspunkt=now())`. Endres 0 rader, gjør den ingenting mer og gir «alt levert».
  2. Har et spørsmål i `okt.innhold` ikke noe `Svar`, rulles transaksjonen tilbake, og funksjonen hever en egen feil med listen over ubesvarte nr.
  3. Ellers kjøres `registrer_svar(sporsmal, riktig=svar.alternativ.er_riktig)` for hvert spørsmål i `innhold`-rekkefølge. Hendelsen lagres i `Svar.hendelse`, og `poengsum` (antall riktige) og `antall` (`len(innhold)`) lagres på økten.
  - `lever_okt` er eneste sted som kaller `registrer_svar`. En kildesjekk-test håndhever det (fra 3.2), med samme mønster som `EnesteStedTest`.
- **`fasit_synlig(sporsmal)`** i `studier/services/feilbank.py`: sann når spørsmålet har en `Feilbankrad` med `laert_tidspunkt` satt.
- **S10 (`/okter/<id>/lever/`):**
  - **GET:** lenkene fra 3.1 står som før, merket «besvart» eller «ikke besvart». Under kommer knappen «Lever» i et POST-skjema.
    - Med ubesvarte spørsmål har knappen `aria-disabled="true"`, og teksten «Du har ikke svart på spørsmål 4 og 7.» står ved den. Hjelpeteksten «Du kan levere når alle spørsmålene er besvart.» er koblet med `aria-describedby`.
    - Formen på oppramsingen er «4», «4 og 7» og «2, 4 og 7».
  - **POST:**
    - Alle besvart: `lever_okt`, så redirect til S11.
    - Ubesvarte: ingenting leveres, og S10 vises igjen med samme tekst i `role="alert"` og lenkene (status 200).
    - Alt levert (dobbeltklikk eller en annen fane): redirect til S11, og feilbanken teller ikke dobbelt.
  - GET på S10 for en levert økt sender til S11.
- **S11 (`/okter/<id>/resultat/`, GET):**
  - h1 «Resultat». «7 av 10 riktige» står i et element med `role="status"` og `tabular-nums`.
  - «N spørsmål er lagt i feilbanken.» vises når N > 0. N er antall `Svar.hendelse == lagt_i` i økten, lest fra `Svar.hendelse` og ikke regnet ut på nytt.
  - Én rad per spørsmål i `innhold`-rekkefølge: «N. <spørsmålstekst>», «Ditt svar: <tekst>» og ✓ «Riktig» eller ✕ «Feil». Ikonet har `aria-hidden`, og fargene er `success`/`error`.
  - Fasiten vises aldri for feil svar. Bare når `fasit_synlig(sporsmal)` er sann, står «Riktig svar: <tekst>» og «Begrunnelse: <tekst>» i raden.
  - `lang` på spørsmålstekst og svar følger regelen fra S9 (`_lang`).
  - Brødsmuler: Oversikt › emne › notat › Resultat. Lenken «Tilbake til notatet» står nederst. Ingen «Øv på feil» (4.1) og ingen «Ta på nytt» (3.4).
  - En påbegynt økt sendes til S10.
- **Leverte økter i flyten fra 3.1** (`deferred-work.md`):
  - S9 (GET og POST) for en levert økt sender til S11. Det betyr at POST på S9 ikke lenger går til S10 for en levert økt.
  - `except OktErLevert` i `sporsmal` sender til S11. En view-test patcher `lagre_svar` til å heve `OktErLevert`.
  - `/jobber/<id>/steg/` for en ferdig jobb der quizen har et levert forsøk og ikke noe påbegynt, gir `HX-Redirect` til S7 i stedet for å lage et nytt forsøk. Ellers som i 3.1.
- **Tilgang:** en annen brukers økt gir 404 på S10 (GET/POST) og S11.
- Ingen JavaScript. Bare vanlige skjemaer. Ingen vannrett rulling ved 360 px.

**Never:**
- Ikke endre `registrer_svar`-regelen, modellene, migreringene eller `ki`.
- Påbegynte forsøk påvirker aldri feilbanken.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| S10 alle besvart | 5 av 5 besvart | Fem lenker «– besvart», «Lever» uten `aria-disabled` | N/A |
| S10 ubesvarte | 4 og 7 ubesvart av 10 | `aria-disabled="true"` og «Du har ikke svart på spørsmål 4 og 7.» | N/A |
| Lever | alle besvart, 3 feil av 5 | `levert`, `levert_tidspunkt`, `poengsum=2`, `antall=5`, tre `lagt_i` og to `ingen` i `Svar.hendelse`, tre `Feilbankrad`, redirect til S11 | N/A |
| Lever med ubesvarte | POST med spørsmål 2 ubesvart | Status fortsatt `pabegynt`, ingen `Feilbankrad`, ingen hendelser, S10 med `role="alert"`-tekst | N/A |
| Dobbel levering | to POST etter hverandre | Ett sett hendelser, teller og rader uendret etter den andre, begge sendes til S11 | N/A |
| Resultat | levert 2/5 | «2 av 5 riktige» med `role="status"`, «3 spørsmål er lagt i feilbanken.», fem rader med «Ditt svar» og Riktig/Feil | N/A |
| Ingen i feilbanken | 5/5 riktige | Ingen «lagt i feilbanken»-tekst | N/A |
| Fasit skjult | feil svar, ikke lært | Ingen «Riktig svar», ingen begrunnelse, og det riktige alternativet nevnes ikke | N/A |
| Fasit synlig | spørsmål med `laert_tidspunkt` satt | «Riktig svar: …» og «Begrunnelse: …» i raden | N/A |
| Påbegynt til S11 | GET resultat for påbegynt økt | Redirect til S10 | N/A |
| Levert til S9 | GET/POST S9 for levert økt | Redirect til S11, ingenting lagret | N/A |
| `OktErLevert` i S9 | `lagre_svar` hever `OktErLevert` | Redirect til S11 | N/A |
| Gammel S8-fane | ferdig jobb, levert forsøk, ingen påbegynt | `HX-Redirect` til S7, ingen ny økt | N/A |
| Påbegynt påvirker ikke | svar lagret, ikke levert | Ingen `Feilbankrad` | N/A |
| Annens økt | GET/POST S10, GET S11 | Ingenting endres | 404 |

</frozen-after-approval>

## Code Map

- `studier/services/okter.py` -- `SvarAvvist`, `OktErLevert`, `element`, `besvarte`, `forste_ubesvarte`, `lagre_svar` (mønster med betinget `update` som første skriving). `lever_okt` legges her.
- `studier/services/feilbank.py` -- `registrer_svar(sporsmal, *, riktig) -> Hendelse`. `fasit_synlig` legges her.
- `studier/tests/test_feilbank.py` -- `EnesteStedTest` er mønsteret for kildesjekken av kall til `registrer_svar` (bare `studier/services/okter.py` er tillatt, utenom feilbank.py selv og tester).
- `studier/views.py` -- `sporsmal` (`redirect(lever_url)` for levert og `OktErLevert`, rundt linje 418-437), `lever` (S10-skall), `steg` (ferdig jobb → `start_eller_fortsett_okt`), `_vis_sporsmal`, `_lang`, `_emne_kontekst(..., notat=)`.
- `studier/urls.py` -- ny rute `okter/<pk>/resultat/` (`resultat`).
- `templates/studier/lever.html` (S10) og ny `templates/studier/resultat.html` (S11). `sporsmal.html` har mønster for knapper og `role="alert"`.
- `farequiz/feilmeldinger.py` -- tekstene for ubesvarte spørsmål og hjelpeteksten.
- `studier/tests/test_okter.py` -- `OktTestCase` (`_quiz`, `_okt`) og testene for levert økt (`test_levert_okt_lagrer_ingenting_og_sender_til_s10` må endres til S11).
- `static/css/input.css` og `app.css` -- bygg som i 3.1 hvis nye klasser trengs (Tailwind 4.3.5 midlertidig fra npm i scratchpad).
- Prototype S10/S11: `_bmad-output/planning-artifacts/ux-designs/ux-G82-bull-knold-skjerven-2026-11-11/prototype/index.html` (`id="s10"` og `id="s11"`).

## Tasks & Acceptance

**Execution:**
- [x] `studier/services/okter.py`, `studier/services/feilbank.py` -- `lever_okt`, `fasit_synlig`
- [x] `studier/views.py`, `studier/urls.py` -- S10 POST, S11, leverte økter i S9 og `steg`
- [x] `templates/studier/lever.html`, `templates/studier/resultat.html`, `farequiz/feilmeldinger.py`
- [x] `studier/tests/test_levering.py` -- én test per rad i matrisen, pluss kildesjekken for `registrer_svar`. Oppdater 3.1-testene for levert økt.

**Acceptance Criteria:**
- Gitt en quiz besvart helt med feil på to spørsmål, når brukeren leverer fra S10, så viser S11 poengsummen og «2 spørsmål er lagt i feilbanken.», og de to spørsmålene har hver sin `Feilbankrad`.

## Implementation Notes

- **Implementert av Sonnet** (første story med `_bmad/custom/bmad-build.user.toml`). Review med tre reviewere på Opus.
- **`lever_okt(okt)`** gir `True` eller `False` og hever `UbesvarteSporsmal` (med `.nr`), som ruller tilbake. `fasit_synlig(sporsmal)` ligger i `feilbank.py` og leser bare.
- **Tekster:** `feilmeldinger.ubesvarte_tekst(nr)` gir «4», «4 og 7» og «2, 4 og 7». `LEVER_HJELP` er hjelpeteksten.
- **S10:** POST som avvises, viser `UbesvarteSporsmal.nr` fra `lever_okt` (review E6). Bare GET regner ut listen fra `besvarte`.
- **`steg`:** en ferdig jobb der quizen har et levert forsøk og ikke noe påbegynt, gir `HX-Redirect` til S7.
- **CSS:** `app.css` er bygget på nytt med Tailwind 4.3.5 fra scratchpad. Ny klasse: `.text-success`.
- **Verifisert:** ruff, `makemigrations --check` og 393 tester grønne, 1 hoppet over. 26 tester i `test_levering.py`, én per rad i matrisen, pluss kildesjekken og de to testene fra review (V1, V2). Ikke kjørt i nettleser.

## Spec Change Log

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 25.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | «lagt i feilbanken» teller ikke et lært spørsmål som besvares feil (`nullstilt`) og dermed kommer tilbake | low | Stemmer, men det frosne punktet definerer N som antall `lagt_i`. `Svar.hendelse` skiller ikke `nullstilt` fra lært og fra i feilbanken. Krever en beslutning i spec-en, og kan først skje ved ny quiz (3.4) | defer |
| B2 | Fasit regnes ut på nytt hver gang S11 vises, i stedet for å være et øyeblikksbilde | low | Det frosne punktet: fasit bare når `fasit_synlig(sporsmal)` er sann | avvist |
| B3 | S11 kjører én eller to spørringer per spørsmål | low | Høyst 30 spørsmål, lokal app | avvist |
| B4 | `resultat` gir `KeyError` hvis et `Svar` mangler | low | Kan ikke nås: `lever_okt` krever alle svar. `Svar` slettes bare sammen med økten (forsøk) | avvist |
| B5 | `_vis_lever` tar imot `ubesvarte_nr` uten å bruke den | low | Bekreftet. Direkte rettelse: bruk `UbesvarteSporsmal.nr` (se E6) | patch |
| B6 | `ubesvarte_tekst([])` gir `IndexError` | low | Kalles bare med en liste som ikke er tom. Feiler høylytt hvis det skulle skje | avvist |
| B7 | `role="status"` gjør ingenting ved første visning | low | AC-en og det frosne punktet krever det | avvist |
| B8 | Meldingen på S10 kan leses opp flere ganger | low | Følger det frosne punktet (`role="alert"` og `aria-describedby`) | avvist |
| B9 | Avvist levering gir 200 uten POST/redirect/GET | low | Det frosne punktet: «status 200» | avvist |
| B10 | Regelen for gammel S8-fane ligger i viewet og er utestet med både levert og påbegynt forsøk | medium | Plasseringen er et designvalg. Testhullet: samme som V1 | patch (test, V1) |
| B11 | Kildesjekkene er skjøre (linjetelling, hele `feilbank.py` er unntatt) | low | Ville krevd AST. Teller- og hendelsestestene dekker selve oppførselen | avvist |
| B12 | Påstanden om samtidig levering er ikke testet | medium | Samme som V2 | patch (test, V2) |
| B13 | Mangler tester for `oving`, HEAD og oppdatert objekt etter `False` | low | `oving` er Epic 4. HEAD følger GET | avvist |
| B14 | «denne kallet» i docstringen | low | Direkte rettelse | patch |
| E1 | `KeyError` på S11 | low | Samme som B4 | avvist |
| E2 | `poengsum`/`antall` er `None` for en økt levert utenom `lever_okt` | low | Kan ikke nås: `lever_okt` er eneste vei til `levert` | avvist |
| E3 | Et lært spørsmål uten riktig alternativ gir `DoesNotExist` | low | Kan ikke nås: `sjekk` krever nøyaktig ett riktig alternativ | avvist |
| E4 | `ubesvarte_tekst([])` | low | Samme som B6 | avvist |
| E5 | Tom `innhold` leveres som «0 av 0» | low | En quiz har alltid 5–30 spørsmål | avvist |
| E6 | Et samtidig svar mellom tilbakerullingen og `_vis_lever` gir 200 uten melding | low | Bekreftet. Direkte rettelse: vis `feil.nr` fra `lever_okt` | patch |
| E7 | Kappløp mellom S8-sjekken og `start_eller_fortsett_okt` | low | Et vindu på millisekunder. Krever en ny transaksjon | avvist |
| E8 | Gammelt resultat endrer seg når fasiten blir synlig senere | low | Samme som B2 | avvist |
| E9 | `…bare_en_gang_i_lever_okt` sjekker ikke at kallet står i `lever_okt` | low | Samme som B11 | avvist |
| V1 | Ingen test for gammel S8-fane med både levert og påbegynt forsøk | medium | Godtatt som levert | patch |
| V2 | Sperren mot dobbel levering er bare testet med et nyhentet objekt | medium | Godtatt som levert | patch |

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne
