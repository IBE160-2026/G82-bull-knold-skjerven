---
title: 'Story 2.3: Laste opp notat'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '55e7ce48cbbfa9b17bca6969e3e7f015bc1c36f1'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Knappen «Last opp notat» på Emnesiden (S4) er låst, og det finnes ingen måte å få et notat inn i appen. Uten notater kan ingen quiz lages (FR-8).

**Approach:**
- `studier.services.notater.last_opp` lagrer fil og `Notat` (AD-1, AD-14).
- Opplastingssiden S6 med bekreftelsen S5 første gang, og fremdrift med JavaScript (S6b) og melding om avbrutt opplasting (S6c) som forbedring.
- Et enkelt skall av Notatsiden S7.

## Boundaries & Constraints

**Beslutninger 25.11 (Magnus):**
- **S16 er skilt ut.** Nytt emne med filer (UX-DR34) blir egen story og står i `deferred-work.md`. 2.3 lager `valider_fil` og `last_opp`, slik at den kan gjenbruke dem.
- **Tom fil:** en fil på 0 byte, eller en DOCX eller TXT uten tekst, gir «Filen er tom. Velg en annen fil.»

**Always:**
- **`last_opp(emne, opplastet_fil, bruker)`** er eneste sted som lager `Notat`. Rekkefølgen er:
  1. Hev `PermissionDenied` hvis `bruker.vilkar_godtatt` er tom (FR-7, AD-23).
  2. Kall `valider_fil`.
  3. I `transaction.atomic()`: lås emnet med `select_for_update`, slik at det må finnes og eies av `bruker`. Lagre deretter filen med `notatfil_sti` og raden.
  4. Feiler noe etter at filen er skrevet, slettes filen før feilen hever seg videre. Ingen fil blir liggende uten rad, heller ikke når emnet slettes samtidig (fra spec 1.6).
- **`valider_fil(opplastet_fil)`** hever `ValidationError` med teksten fra `farequiz/feilmeldinger.py`:
  - Ingen fil: «Velg en fil først.»
  - Over 5 MB (5 × 1024 × 1024 byte): «Filen er over 5 MB. Velg en mindre fil.»
  - Endelse eller innhold stemmer ikke: «Formatet støttes ikke. Bruk PDF, DOCX eller TXT.» Innholdet sjekkes slik:
    - En PDF må starte med `%PDF-`.
    - En DOCX må være en zip som inneholder `word/document.xml`.
    - En TXT må kunne dekodes som UTF-8 eller cp1252.
  - 0 byte, eller DOCX/TXT uten annet enn blanke tegn: «Filen er tom. Velg en annen fil.»
- `originalnavn` er filnavnet uten sti, `filtype` er fra `Filtype`, og `storrelse` er i byte.
- Andre brukeres emne gir 404 med `hent_egen`, og ingenting lagres. Filer serveres aldri over HTTP (AD-8). Ingen rute til `MEDIA_ROOT`.
- **Skjema og felter:**
  - Vanlig `<input type="file">` med etiketten «Velg fil» og `accept=".pdf,.docx,.txt"`, uten dra-og-slipp.
  - Hjelpeteksten «PDF, DOCX eller TXT. Maks 5 MB.» er koblet med `aria-describedby`. KI-varselet og knappen «Last opp» hentes fra prototypen.
  - Feil står ved feltet med `role="alert"` og `autofocus`, som i `ny_emne.html`.
  - Skjemaet virker uten JavaScript (AD-13).
- **S5:** vises når brukeren ikke har noen notater i noen emner. Teksten og knappene «Gå videre til opplasting» og «Avbryt» hentes fra prototypen. Lenken går til S15, og «Avbryt» går til S4.
- **S6b og S6c** (`static/js/opplasting.js`, lastes i `skript`-blokken):
  - Nettleseren sjekker format og størrelse før sending.
  - Skjemaet sendes med `XMLHttpRequest` og viser filnavn og prosent i `role="status"`. Knappen låses, og teksten «Ikke lukk fanen …» vises.
  - Ved nettfeil eller avbrudd vises S6c-meldingen med `role="alert"` og fokus.
  - Svarer serveren med skjemaet og en feil, vises det svaret.
- **S7 (`/notater/<id>/`):** h1 er `originalnavn`, brødsmuler Oversikt › emne › notat, og teksten «Lag en quiz for å komme i gang». Etter vellykket opplasting sendes brukeren dit.
- S4 viser notatene som lenker til S7, nyeste først. «Last opp notat» er en lenke til `/emner/<id>/last-opp/`.

**Never:**
- Ingen quiz-skjema, generering eller `ki`-kall (story 2.4). Ingen nedlasting av filen.
- Ikke endre `ki`, modellene, migreringene eller Nytt emne (S16).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Gyldig PDF | `%PDF-…`, 1 MB | Fil i `notater/<eier>/<uuid>.pdf`, `Notat` med riktige felt, redirect til S7 | N/A |
| Gyldig DOCX/TXT | ekte DOCX, UTF-8-TXT med æøå | Som over | N/A |
| Ingen fil | POST uten fil | Ingen rad, ingen fil | «Velg en fil først.» ved feltet |
| For stor | 5 MB + 1 byte | Ingen rad, ingen fil | «Filen er over 5 MB …» |
| Feil endelse | `.mp4`, `.pptx`, `.png` | Ingen rad, ingen fil | «Formatet støttes ikke …» |
| Feil innhold | `.pdf` uten `%PDF-`, `.docx` som ikke er zip | Ingen rad, ingen fil | «Formatet støttes ikke …» |
| Tom | 0 byte, eller TXT med bare mellomrom | Ingen rad, ingen fil | «Filen er tom …» |
| Uten vilkår | `last_opp` kalt med bruker uten `vilkar_godtatt` | Ingen rad, ingen fil | `PermissionDenied` |
| Annens emne | GET eller POST til emne eid av en annen | Ingen rad, ingen fil | 404 |
| Emnet slettet underveis | raden kan ikke lagres | Filen slettes igjen | Feilen hever seg videre |
| Første gang | bruker uten notater åpner «Last opp notat» | S5 | N/A |
| Senere | bruker med minst ett notat | S6 direkte | N/A |

</frozen-after-approval>

## Code Map

- `studier/models.py:65-68,91-104` -- `notatfil_sti` krever `instance.emne`. `Notat` har ingen `ordering`, så sorter med `-opprettet`. Ikke endre modellen.
- `studier/services/emner.py` -- mønster: `transaction.atomic`, `on_commit` og `_slett_filer`. Ny modul `studier/services/notater.py`.
- `studier/tilgang.py:47,55` -- `egne(modell, bruker)` og `hent_egen(modell, pk, bruker)`. `EIERVEI` har allerede `Notat: "emne__eier"`.
- `studier/views.py:16-90` -- mønster for `@require_http_methods`, `hent_egen`, `brodsmuler` (siste uten `url`), `tilbake_url` og `tilbake_tekst`.
- `studier/urls.py` -- nye ruter `emner/<pk>/last-opp/` (`last_opp`) og `notater/<pk>/` (`notat`).
- `studier/forms.py` -- nytt `NotatForm` med ett filfelt. Valideringen ligger i `valider_fil`, og skjemaet kaller den.
- `templates/studier/emne.html:12,27-35` -- den låste knappen blir en lenke. Lista får lenker.
- `templates/studier/ny_emne.html:17-19` -- feilmønsteret.
- `templates/base.html:90` -- `skript`-blokken laster `js/meny.js`. Behold den med `{{ block.super }}`.
- `kontoer/middleware.py:132-143` -- POST uten godtatte vilkår sendes til `/vilkar/`. Tjenesten sjekker likevel selv.
- `farequiz/feilmeldinger.py` -- legg til de fire filtekstene.
- `farequiz/settings.py:149-157` -- `MEDIA_ROOT`, ingen `MEDIA_URL`. Ingen endring.
- `studier/tests/test_slett_emne.py:29-71` -- `_innlogget` og `MedFilerTestCase` (midlertidig `MEDIA_ROOT`). Gjenbruk mønsteret.
- `static/css/app.css` -- bygges med `sh scripts/bygg-css.sh` (`TAILWIND_BIN` er satt på denne maskinen) hvis nye klasser trengs.
- Prototype: `_bmad-output/planning-artifacts/ux-designs/ux-G82-bull-knold-skjerven-2026-11-11/prototype/index.html`, linje 219-271 (S5, S6, S6b, S6c) og 356+ (S7). Tekstene skal hentes derfra. EXPERIENCE.md i samme mappe, linje 27-43 og 85-114.

## Tasks & Acceptance

**Execution:**
- [x] `farequiz/feilmeldinger.py` -- filtekstene
- [x] `studier/services/notater.py` -- `valider_fil` og `last_opp` -- FR-7, FR-8, AD-14
- [x] `studier/forms.py` -- `NotatForm`
- [x] `studier/views.py`, `studier/urls.py` -- `last_opp` (S5/S6) og `notat` (S7)
- [x] `templates/studier/last_opp.html`, `templates/studier/bekreft_opplasting.html`, `templates/studier/notat.html` og `emne.html`
- [x] `static/js/opplasting.js` -- S6b og S6c
- [x] `static/css/app.css` -- bygg på nytt hvis nye klasser trengs
- [x] `studier/tests/test_last_opp.py` -- én test per rad i matrisen, pluss at ingen URL gir filen

**Acceptance Criteria:**
- Gitt S6 uten JavaScript, når et gyldig skjema sendes, så lagres notatet, og brukeren havner på S7.
- Gitt S4 etter opplasting, så står notatet øverst som lenke til S7.
- Gitt en hvilken som helst URL under `/media/` eller med filstien, så svarer appen 404.

## Implementation Notes

- **`studier/services/notater.py`:** `valider_fil` returnerer `Filtype`. Rekkefølgen er ingen fil, størrelse, endelse, 0 byte og til slutt innhold.
  - En DOCX åpnes med python-docx. En DOCX som har tekst bare i tabeller, regnes som tom, likt med `ki.les_fil`.
  - En TXT med nullbyte avvises som feil format.
  - `last_opp` låser emnet med `select_for_update().get(pk, eier=bruker)`. Mangler emnet, gir det 404. Feiler noe etter at filen er skrevet, slettes filen (`except BaseException`).
- **Visninger:**
  - «Gå videre til opplasting» på S5 går til `?videre=1`. En POST viser alltid S6.
  - Et skjema med feil gir status 200, som på Nytt emne.
  - S4 sorterer notatene etter `-opprettet` og viser «Lastet opp <dato>».
- **`opplasting.js`:** tekstene kommer fra `data-*`-attributter, så `feilmeldinger.py` er eneste kilde.
  - Fremdriften vises i steg på 10 %, og `xhr.timeout` er 300 s.
  - En omdirigering følges. Status 200 uten omdirigering byttes inn. Alt annet gir S6c.
  - Ny CSS-klasse `.reiserute` i `input.css`. `app.css` er bygget på nytt.
- **Ikke med:** bil- og flaggikonene i reiseruten fra prototypen, Avbryt-knapp og varsel når fanen lukkes.
- **Verifisert:**
  - ruff, `makemigrations --check` og 222 tester grønne (30 nye i `test_last_opp.py`).
  - Hele flyten er prøvd manuelt i headless Edge med og uten JavaScript, med midlertidig database. Det var før JavaScript-rettelsene fra reviewen, som er små og sjekket med `node --check`.

## Spec Change Log

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 25.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | Ingen grense på størrelsen av forespørselen før 5 MB-sjekken | low | Stemmer, men appen kjøres lokalt (beslutning 28.10). En egen upload handler er mer enn en direkte rettelse | avvist |
| B2 | Zip-bombe i DOCX | low | Lokal kjøring, og brukeren rammer bare seg selv. Krever en ny vakt | avvist |
| B3 | TXT-sjekken godtar nesten all binær data via cp1252 | low | Bekreftet: cp1252 dekoder alle byte unntatt fem. En nullbyte er et sikkert tegn på binær data eller UTF-16. Direkte rettelse | patch |
| B4 | En PDF uten tekst godtas | false | En skannet PDF skal godtas. PDF-en sendes hel, og modellen leser bildene (FR-9) | avvist |
| B5 | `valider_fil` kjører to ganger | low | Bevisst forsvar i tjenesten. Maks 5 MB, så kostnaden er liten | avvist |
| B6 | Filen skrives mens SQLite-låsen holdes | low | Én lokal bruker. Å bytte rekkefølge endrer oppryddingen | avvist |
| B7 | JavaScript: `xhr.timeout` er ikke satt, ingen «Lagrer», ingen Avbryt, ingen `beforeunload` | low | Timeout: stemmer, og en opplasting som henger, låser skjemaet. Direkte rettelse (se E1). Resten står ikke i spec-en eller prototypen | patch (timeout) |
| B8 | Siden lover beskjed når filen er lagret, men S7 viser ingen bekreftelse | low | Teksten kommer fra prototypen. S7 med filnavnet som overskrift er beskjeden | avvist |
| B9 | `visSvar` ser bort fra HTTP-status | low | Bekreftet: 403, 404 og 500 med `#innhold` byttes inn. Direkte rettelse: bare 200 byttes inn, ellers S6c | patch |
| B10 | `opplasting.js` har ingen automatiske tester | medium | Samme som V2 | defer |
| B11 | Grensen og formatene står flere steder | low | Kontrakten mellom visning, mal og skript dekkes av testen i V1. Resten er avvist | avvist |
| B12 | Tittel og tekst i S5 | low | Tekstene kommer ordrett fra prototypen. At S5 kommer igjen etter at alle emner er slettet, følger regelen i spec-en | avvist |
| B13 | `originalnavn` kuttes ved 255 tegn og bidi-tegn fjernes ikke | low | Brukeren ser bare sitt eget filnavn. `filtype` er validert uansett | avvist |
| B14 | `assertNotIn("disabled", html)` er skjør | low | Stemmer. Direkte rettelse i testen | patch |
| E1 | `xhr.timeout` er ikke satt, så skjemaet kan bli låst for alltid | low | Bekreftet. Settes til 300 s | patch |
| E2 | Utløpt økt eller manglende vilkår gir omdirigering til en annen side | false | Nettleseren går dit (innlogging eller `/vilkar/`). Det er riktig, og ingenting er lagret | avvist |
| E3 | Nettfeil etter commit gir «Filen er ikke lagret» | low | Sjeldent. Krever en sjekk mot serveren | avvist |
| E4 | Dobbeltklikk uten JavaScript gir to notater | low | Sjeldent. Krever et engangstoken | avvist |
| E5 | Stor forespørsel | low | Samme som B1 | avvist |
| E6 | Zip-bombe | low | Samme som B2 | avvist |
| E7 | UTF-16 eller binær TXT | low | Samme som B3 | patch |
| E8 | `.txt` som filnavn tolkes ulikt i JavaScript og på serveren | low | Stemmer. Direkte rettelse (`punktum > 0`) | patch |
| E9 | `data-maks` mangler eller er ugyldig | low | Kan bare skje hvis malen er feil. Dekkes av testen i V1 | avvist |
| E10 | Disken blir full midt i lagringen før navnet er satt | low | Sjeldent. Krever endret rekkefølge i lagringen | avvist |
| E11 | S5 vises igjen når alle emner er slettet | false | Følger regelen i spec-en: «ingen notater i noen emner» | avvist |
| V1 | `data-*`-attributtene mellom visning, mal og skript er ikke testet | medium | Kontrollert av V | patch |
| V2 | JavaScript-flyten har ingen automatisk test | medium | Repoet har ikke noe testoppsett for JavaScript. Flyten ble kontrollert manuelt i headless Edge | defer |

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne

**Manual checks:**
- I nettleseren: S6 med bare tastatur, en feil fil gir feilmelding med fokus, og en gyldig fil viser fremdrift og ender på S7.
