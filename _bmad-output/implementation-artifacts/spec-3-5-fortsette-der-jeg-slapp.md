---
title: 'Story 3.5: Fortsette der jeg slapp'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'e40db0a83573011b12f461309979f52ffb389ee9'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Et påbegynt forsøk er usynlig. Quizkortet på S7 sier «Ta quiz» eller «Ta på nytt», S3 viser ingen påbegynte økter, og «Ta på nytt» på S11 fortsetter et påbegynt forsøk uten å si det (FR-18, UX-DR9, UX-DR14).

**Approach:** Vis fremdrift og «Fortsett» på quizkortet (S7) og på S11. Legg boksen «Fortsett der du slapp» øverst på Oversikt (S3), med én rad per påbegynt forsøk. Start- og fortsett-logikken (`start_quiz`, `start_eller_fortsett_okt`, `forste_ubesvarte`) gjenbrukes uendret.

## Boundaries & Constraints

**Always:**
- **Fremdriftstekst:** «spørsmål N av M». M er `len(okt.innhold)`, og N er antall `Svar` i økten, men minst 1. Uten svar står det altså «spørsmål 1 av 10» (avgjort av Christian 25.11). Teksten er lik på S7 og S3.
- **S7 (quizkortet):** med et påbegynt forsøk står «Påbegynt – spørsmål N av M» på kortet, og knappen i POST-skjemaet til `start_quiz` heter «Fortsett». Ellers som i 3.4: «Ta på nytt» med et levert forsøk, og «Ta quiz» uten.
- **S11:** med et påbegynt forsøk på quizen heter knappen «Fortsett» i stedet for «Ta på nytt» (samme skjema til `start_quiz`, fra `deferred-work.md`, 3.4 B4).
- **S3 (`farequiz/views.py` `startside`, `templates/studier/oversikt.html`):**
  - Boksen står over h1 «Oversikt», med overskriften «Fortsett der du slapp» som h2.
  - Den har én rad per påbegynt `forsok` hos brukeren (`egne(Okt, …)`), sortert på `sist_endret` med nyeste først, og `pk` synkende ved likhet.
  - Hver rad viser «<Vanskelighetsgrad>, M spørsmål», «<emne> · <notat> · spørsmål N av M» og lenken «Fortsett quizen» (GET) til `/okter/<id>/sporsmal/<forste_ubesvarte>/`. Lenken har `aria-describedby` til radens tittel.
  - Uten påbegynte forsøk vises ikke boksen (ingen overskrift og ingen tom liste).
- Antall spørringer på S3 avhenger ikke av antall rader (`select_related` og annotering eller prefetch).
- Tilgang: en annen brukers økter vises aldri på S3.
- Ingen JavaScript. Bare klasser som allerede finnes i `app.css`, eller `app.css` bygges på nytt. Ingen vannrett rulling ved 360 px.

**Never:**
- Ikke endre tjenestene i `studier/services/okter.py`, modellene, migreringene eller `ki`.
- Øvingsøkter (`type=oving`) vises ikke ennå. Epic 4 legger dem til i boksen.
- Ingen menyoppføring «Fortsett der du slapp» (Christians UX). Den står ikke i AC-ene.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| S7 påbegynt | forsøk med 5 av 10 svar | «Påbegynt – spørsmål 5 av 10», knappen «Fortsett» | N/A |
| S7 påbegynt uten svar | nytt forsøk, 0 av 5 svar | «Påbegynt – spørsmål 1 av 5» | N/A |
| S7 levert og påbegynt | levert forsøk og nytt påbegynt | «Fortsett», ikke «Ta på nytt» | N/A |
| S7 bare levert | levert, ingen påbegynt | «Ta på nytt», ingen «Påbegynt» | N/A |
| S11 med påbegynt | resultat for eldre forsøk, nytt påbegynt | knappen «Fortsett» | N/A |
| S3 rader | to påbegynte forsøk i ulike emner | to rader, sist endret øverst, riktig tekst og lenke | N/A |
| S3 lenke | 2 og 3 besvart av 5, 1 ikke | lenke til `/okter/<id>/sporsmal/1/` (første ubesvarte) | N/A |
| S3 tom | bare leverte forsøk | ingen boks | N/A |
| S3 tilgang | annen bruker har påbegynt forsøk | ikke vist | N/A |
| S3 spørringer | 1 mot 3 påbegynte forsøk | samme antall spørringer | N/A |

</frozen-after-approval>

## Code Map

- `farequiz/views.py` -- `startside` (S3). Legg til de påbegynte forsøkene: `egne(Okt, request.user).filter(type=forsok, status=pabegynt)`, `select_related("quiz", "notat__emne")`, `annotate(besvart=Count("svar"))`, `order_by("-sist_endret", "-pk")`.
- `templates/studier/oversikt.html` -- boksen over h1. Mønster for kortflate: `rounded-lg border border-border-subtle bg-surface p-4 shadow-md`. `border-accent` finnes. `border-2`, `bg-selected` og `bg-surface-muted` finnes ikke i `app.css`.
- `studier/services/okter.py` -- `forste_ubesvarte(okt)` gjør én spørring per økt. For S3 regnes første ubesvarte ut fra prefetchede `svar` i viewet, eller med en liten hjelper som tar settet med besvarte ID-er. Ikke endre `forste_ubesvarte`.
- `studier/views.py` -- `notat` (S7) har `har_levert = Exists(...)` per quiz. Legg til det påbegynte forsøket med antall svar, for eksempel i én spørring over notatets påbegynte forsøk med `Count("svar")`, koblet på `quiz_id`. `resultat` (S11): send med om quizen har et påbegynt forsøk.
- `templates/studier/notat.html` -- knappetekst og fremdriftslinje. `templates/studier/resultat.html` -- knappetekst.
- Tester: `studier/tests/test_ta_pa_nytt.py` (`TaPaNyttTestCase`, `_kortknapp`) har testene for S7 og S11 fra 3.4. `test_ta_pa_nytt_ogsa_med_nytt_paabegynt_forsok` må nå forvente «Fortsett». `studier/tests/test_emner.py` `OversiktTest` er mønsteret for S3. `OktTestCase` og `_annen_bruker` ligger i `test_okter.py`.
- Prototype S3: `_bmad-output/planning-artifacts/ux-designs/ux-G82-bull-knold-skjerven-2026-11-11/prototype/index.html` (`id="s3"`, `.continue`).

## Tasks & Acceptance

**Execution:**
- [x] `farequiz/views.py`, `templates/studier/oversikt.html` -- boksen «Fortsett der du slapp» på S3.
- [x] `studier/views.py`, `templates/studier/notat.html`, `templates/studier/resultat.html` -- fremdrift og «Fortsett» på S7 og S11.
- [x] `studier/tests/test_fortsette.py` -- én test per rad i matrisen. Oppdater 3.4-testen for nytt påbegynt forsøk.

**Acceptance Criteria:**
- Gitt et påbegynt forsøk med 5 av 10 besvart, når brukeren trykker «Fortsett quizen» på S3, så åpnes S9 på spørsmål 6 med de lagrede svarene.
- Gitt et påbegynt forsøk startet på én klient, når samme bruker logger inn med en annen klient (ny `Client`), så viser S3 og S7 samme fremdrift.

## Implementation Notes

- **Implementert av Sonnet.** Review med tre reviewere på Opus.
- **S3:** `_fortsett_rader` i `farequiz/views.py` gjør én spørring for øktene (`select_related("quiz", "notat__emne")`) og én `Prefetch` av `svar`. Første ubesvarte regnes ut i viewet med samme regel som `forste_ubesvarte`, også at alle besvart gir 1. Det er gjort for å slippe én spørring per økt, og en kommentar peker på originalen.
- **S7:** `notat` henter notatets påbegynte forsøk med `Count("svar")` i én spørring og setter `quiz.fremdrift`. **S11:** `har_pabegynt`. Begge bruker `egne(Okt, …)`.
- **Universell utforming:** fremdriftslinjen har en id og står i `aria-describedby` sammen med tittelen, både på lenken på S3 og på «Fortsett» på S7.
- **3.4-tester:** `test_uten_levert_forsok_heter_knappen_ta_quiz` sletter `setUp`-økten først, og `…_nytt_paabegynt_forsok` forventer «Fortsett».
- **Verifisert:** ruff, `makemigrations --check` og 421 tester grønne, 1 hoppet over. Ikke kjørt i nettleser.

## Spec Change Log

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 25.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | AD-11-kommentaren havnet over `pabegynte` | low | Bekreftet. Flyttet tilbake | patch |
| B2 | «spørsmål N av M» bygges på to steder | low | Stemmer, men testene låser begge tekstene. En felles hjelper ville gitt mer kode enn den sparer | avvist |
| B3 | `_fortsett_rader` kopierer `forste_ubesvarte` | medium | Bekreftet: kan drive fra hverandre. Code Map tillot det for å unngå én spørring per økt. Rettet med kommentar og en paritetstest (alle besvart) | patch (med B4, E2, V2) |
| B4 | Alle besvart uten levering er ikke testet | medium | Samme som V2 | patch |
| B5 | `_boks` klipper fra starten av dokumentet | medium | Bekreftet. Klipper nå `<section>` | patch |
| B6 | Tilgangstesten sletter brukerens eget forsøk | medium | Bekreftet. Har nå positiv kontroll med nøyaktig én rad | patch |
| B7 | Testen for «S3 rader» bruker samme emne | medium | Bekreftet. Avviker fra matrisen | patch (med V1) |
| B8 | Fremdriften står ikke i `aria-describedby` | low | Bekreftet. Skjermlesere hører ikke fremdriften ved knappen. Id lagt til | patch |
| B9 | Malkommentaren på S11 er utdatert | low | Rettet | patch |
| B10 | Docstringene i `farequiz/views.py` er utdaterte | low | Rettet | patch |
| B11 | De nye spørringene bruker ikke `egne()` | low | Trygt fordi notatet og økten er hentet med `hent_egen`, men bryter AD-8-mønsteret. Direkte rettelse | patch |
| B12 | `_svar_n` har et uklart API | low | Bare testkode og kosmetisk | avvist |
| E1 | Tom `innhold` gir «1 av 0» | false | `sjekk` krever 5–30 spørsmål, så en quiz uten spørsmål lagres aldri | avvist |
| E2 | S3 kaller ikke `forste_ubesvarte` | medium | Samme som B3 | patch |
| E3 | S11 viser ikke fremdrift | false | Det frosne punktet for S11 krever bare knappeteksten «Fortsett» | avvist |
| V1 | Sorteringen på `sist_endret` skilles ikke fra `pk` | medium | Bekreftet (filed gap). Ny test: A opprettet først i ett emne, B i et annet, så svar i A, og A står øverst | patch |
| V2 | Fallbacken på S3 (alle besvart) er ikke testet | medium | Bekreftet (filed gap). Ny test: 5 av 5 og lenke til spørsmål 1 | patch |

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne
