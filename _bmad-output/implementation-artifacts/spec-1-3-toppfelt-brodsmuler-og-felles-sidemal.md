---
title: 'Story 1.3: Toppfelt, brødsmuler og felles sidemal'
type: 'feature'
created: '2026-11-24'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '2fc38b3'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Sidene fra story 1.2 er semantisk HTML uten styling. Toppfeltet, brødsmulestien, testmodus-banneret, fotlinjen og designtokenene mangler, og 404-siden finnes ikke. Story 1.4 til 1.6 og alle senere sider trenger en felles mal.

**Approach:** Bygg ut `base.html` med det mørke toppfeltet (logo, «‹ Tilbake», «Meny» og «Logg ut»), brødsmulesti, testmodus-banner, fotlinje og «Hopp til innhold». Sett opp Tailwind v4 med designtokenene fra DESIGN.md, htmx 2.0.11 lokalt og de to SVG-ene fra prototypen. Legg til 404-siden «Fant ikke siden».

**Beslutninger 24.11 (brukeren):**
- **Tailwind:** Tailwind v4 frittstående CLI, bygget til `static/css/app.css` og committet (alternativ A). Binæren lastes ned fra GitHub én gang, og det spørres før nedlasting.
- **Logo:** Logoen vises alltid, også på 320 px (alternativ A).

## Boundaries & Constraints

**Always:**
- Følg epic-1-context.md, AD-1 og AD-8. Norske identifikatorer uten æ, ø og å. Tekst i grensesnittet er norsk bokmål, du-form og uten utropstegn.
- Tokenene i Tailwind `@theme` kommer fra DESIGN.md. Ingen fargeverdier skrives direkte i malene.
- Tailwind bygges til `static/css/app.css`, og den ferdige filen committes, slik at sensor ikke trenger Node.
- Toppfeltet, brødsmulestien og testmodus-banneret ligger på samme sted på alle sider (WCAG 3.2.6).
- Logg ut, Tilbake og Meny vises bare for innloggede brukere. Tilbake vises ikke på S3.
- «Meny» er en `<details>`-meny. Åpning virker uten JavaScript. Lukking med Esc og klikk utenfor krever `static/js/meny.js`. Den inneholder Oversikt, Nytt emne og Personvernerklæringen. **Ikke** Øv på feil, jf. gruppas beslutning 23.11.
- «‹ Tilbake» er en vanlig lenke til forelderen, med `aria-label` som sier hva den går til.
- Fokusringen er 2 px `accent-strong`, og i toppfeltet `focus-inverse`. Den fjernes aldri.
- Knapper og lenker i toppfeltet er minst 44 px høye på mobil.
- Fotlinjen har opphavsrettsklausulen fra S15 og en lenke til personvernerklæringen.

**Never:**
- Ingen modal, ingen fokusfelle og ingen JavaScript-avhengig funksjon. Modal for S1b hører til story 1.3 bare hvis den er tatt med i kriteriene under, og den er ikke det.
- Ingen nye migreringer, ingen endring av modeller eller `kontoer`-logikken.
- Ingen Øv på feil i menyen, og ingen mørk modus.
- Ingen eksterne skrifter. Systemfonter (`font-sans`).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Innlogget på S3 | Åpner `/` | Toppfelt med logo, Meny og Logg ut. Ingen Tilbake. Brødsmulesti viser «Oversikt» | N/A |
| Innlogget på en underside | Åpner `/emner/3/` | Tilbake lenker til forelderen (Oversikt). Brødsmulesti viser «Oversikt › emnenavn» | N/A |
| Utlogget | Åpner `/logg-inn/` | Ingen Logg ut, Tilbake eller Meny. Logo og «Hopp til innhold» finnes | N/A |
| Testmodus på | Alle sider | Testmodus-banneret «Testmodus: quizene bruker mock-svar, ingen KI kalles» under toppfeltet | N/A |
| Ukjent side | Åpner `/finnes-ikke/` | 404 med «Fant ikke siden» og lenke til Oversikt. Ingen data avsløres | 404 |
| Annen brukers emne | Innlogget, åpner `/emner/<annen brukers id>/` | 404 med samme side (FR-3) | 404 |
| Meny | Trykk «Meny» | Rullgardin med Oversikt, Nytt emne og Personvernerklæringen. Lukkes med Esc og klikk utenfor | N/A |
| Smal skjerm | 320 px bredde | Ingen vannrett rulling. Meny og Tilbake er fortsatt synlige | N/A |

## Code Map

**Funnet i kodebasen (24.11):** `templates/base.html` er en enkel grunnmal med `lang="nb"`, blokkene `title` og `innhold`, og et Logg ut-skjema for innloggede. Sidene under `templates/kontoer/` og `templates/startside.html` arver den. `ki.er_testmodus()` finnes i `ki/__init__.py`. Det finnes ikke `static/`, `context_processors.py`, `handler404` eller `STATICFILES_DIRS` ennå. `farequiz/settings.py` har `STATIC_URL = "static/"`. `studier/models.py` har kaskade-sletting på alle relasjonene til `Emne`, men filer på disk slettes ikke av databasen. Det er ikke i denne storyen.

- `templates/base.html` -- toppfelt, Hopp til innhold, testmodus-banner, brødsmulesti (blokk), `<main>` og fotlinje. Bruker `{% block innhold %}` og `{% block title %}`.
- `templates/partials/topbar.html` -- toppfeltet med logo, Tilbake, Meny og Logg ut. Vises bare for innloggede.
- `templates/partials/brodsmuler.html` -- brødsmulesti som tar en liste over steg.
- `templates/404.html` -- «Fant ikke siden» med lenke til Oversikt.
- `farequiz/context_processors.py` -- legg til `testmodus`-flagget i kontekst for banneret, og `brodsmuler` der det trengs. Bruker `ki.er_testmodus()` som eneste kilde.
- `farequiz/settings.py` -- `STATICFILES_DIRS` peker til `static/`. 404 er Djangos standard, med `templates/404.html`.
- `static/css/app.css` -- bygget fra `static/css/input.css` med Tailwind v4 frittstående CLI. `@theme` kommer fra DESIGN.md.
- `static/css/input.css` -- `@import "tailwindcss"`, og `@theme` med fargene, skriftstørrelsene og radiusene fra DESIGN.md.
- `static/js/htmx.min.js` -- htmx 2.0.11, lokal fil. Ingen CDN.
- `static/img/favicon.svg`, `static/img/kart.svg` -- kopieres fra `prototype/` i designbranchen.
- `package.json` eller en `scripts/bygg-css.sh` -- kommando for å bygge CSS. Tailwind-CLI-binæren er ikke en avhengighet i repoet.
- `kontoer/tests_sider.py`, `farequiz/tests_maler.py` -- tester for toppfeltet, Tilbake, Meny, brødsmulestien og 404.

## Tasks & Acceptance

**Execution:**
- [x] `static/css/input.css` og `static/css/app.css` -- Tailwind v4 med `@theme` fra DESIGN.md -- ingen verdier hardkodet i malene
- [x] `static/js/htmx.min.js` -- htmx 2.0.11 lokalt, med lisens i `static/js/LICENSE.htmx`
- [x] `static/img/` -- `favicon.svg` og `kart.svg` fra prototypen
- [x] `templates/base.html` -- `lang="nb"`, `<title>`, toppfelt, Hopp til innhold som første fokuserbare element, testmodus-banner, brødsmulesti, `<main>` og fotlinje
- [x] `templates/partials/topbar.html` -- Tilbake, Meny og Logg ut, vises bare for innloggede
- [x] `templates/404.html` -- «Fant ikke siden» med lenke til Oversikt, brukt av Djangos standard 404 når `DEBUG=False`
- [x] `farequiz/context_processors.py` -- `testmodus` og brødsmulestien
- [x] Oppdater `kontoer`-sidene til å bruke den nye malen, uten å endre innhold eller tekst
- [x] Tester etter I/O-matrisen, pluss en test for at Meny ikke inneholder Øv på feil

**Acceptance Criteria:**
- Gitt en innlogget bruker, når hen er på S3, så vises logo, Meny og Logg ut, og Tilbake vises ikke.
- Gitt en innlogget bruker på en underside, når siden vises, så lenker Tilbake til forelderen, og brødsmulestien viser stiene fra toppen.
- Gitt en utlogget besøkende, når siden vises, så vises ikke Logg ut, Tilbake eller Meny.
- Gitt testmodus, når en side vises, så står banneret mellom toppfeltet og innholdet.
- Gitt en ukjent side eller en annen brukers ID, når siden åpnes, så vises 404-siden med «Fant ikke siden» og lenke til Oversikt.
- Gitt en skjerm på 320 px og 200 % tekst, når en side vises, så er det ingen vannrett rulling (WCAG 1.4.10).
- Gitt en tastaturbruker, når hen trykker Tab fra toppen, så er «Hopp til innhold» det første elementet, og fokusringen er synlig på alle elementer.
- Gitt en side, når den sjekkes med axe, så finnes ingen brudd på WCAG 2.2 A/AA.

## Implementation Notes

- **24.11, implementert og verifisert lokalt.** Tailwind-CLI v4.3.5 (84 MB) og htmx 2.0.11 er lastet ned etter godkjenning. Binæren ligger utenfor repoet, i `~/.cache/farequiz-verktoy`, og bygges med `scripts/bygg-css.sh`.
- **Verifisert:** ruff check og format er grønne, `makemigrations --check` er grønn, og 101 tester er grønne (10 nye). Alle klasser som brukes i malene finnes i `app.css`.
- **Avvik 1, htmx:** htmx ligger i `static/js/`, men lastes ikke på alle sider. S1b skal være uten JavaScript (kriteriet i 1.2), så `base.html` har et tomt `skript`-blokk som senere fragmenter kan fylle.
- **Avvik 2, Meny (løst 24.11):** Meny lukkes med Esc og klikk utenfor. Det gjøres av `static/js/meny.js`, som lastes på alle sider unntatt S1b, der det ikke skal være JavaScript. Esc flytter fokus tilbake til «Meny».
- **Review (24.11):** Rettet: knapper i toppfeltet er 44 px (`min-h-11`), tom brødsmulesti vises ikke, siste brødsmule har `aria-current`, `aria-label` faller tilbake til «Tilbake», og testmodus-banneret testes når det er av. 404-testen kjører med `DEBUG=False`.
- **Avvik 3, dokumenterte endringer:** `brodsmuler` settes i `startside`-visningen, ikke i `context_processors.py`, som bare har `testmodus`. Personvernerklæringen ble endret etter beslutningen om kontosletting (24.11), og kontoer-sidene er endret for det. Det er ikke en tekstendring utover det.
- **Statiske filer uten DEBUG (24.11):** WhiteNoise serverer `static/` også med `DEBUG=False`, uten `collectstatic`. Pakken er lagt til i `pyproject.toml`. Testet i `StatiskeFilerTest`.
- **Kontakt i personvernerklæringen:** Ola Normann, ola@normann.no, slik teksten sier. Setningen om kontosletting peker dit.
- **Åpent:** «Nytt emne» i menyen går til Oversikt til story 1.4 lager S16. `handler404` er fjernet fra spec-en, siden Djangos standard 404 allerede bruker `templates/404.html`.
- **Manuell sjekk i nettleser (24.11), Chrome headless med `playwright-core` og `axe-core` 4.14.1, utenfor repoet:** 320 px og 200 % tekst (160 px CSS) gir ingen vannrett rulling på innlogging, registrering, personvern og 404 med `DEBUG=False`. Axe finner ingen brudd på WCAG 2.2 A/AA på de sidene som er sjekket. Meny åpnes, lukkes med Esc og klikk utenfor, og fokus går tilbake til «Meny». Første Tab gir «Hopp til innhold».
- **Rettelser fra sjekken:** skjemafelt og lange ord brytes nå, slik at ingenting stikker ut på smale skjermer.
- **Ikke sjekket:** kontrastverdier for alle tokenkombinasjoner, og Oversikt på 320 px, fordi Oversikt bare har én tekstboks.
- Sprint-forslaget for 1.3 er oppdatert til å beholde Tilbake og Meny (gruppas beslutning 24.11). Meny-innholdet i forslaget står med «Øv på feil», som er feil. Det rettes til samme innhold som denne spec-en.

## Spec Change Log

## Design Notes

- **Tilbake** er en lenke til forelderen, ikke `history.back()`. Det gir en forutsigbar adresse som også fungerer uten historikk, og det er det epic-konteksten sier.
- **Meny** bruker `<details>`, så åpning virker uten JavaScript. Lukking med Esc og klikk utenfor ligger i `static/js/meny.js`, og er et akseptansekriterium.
- **S1b-modalen** holdes utenfor denne storyen. Den er en vanlig side i 1.2, og modal-oppførselen legges til når den er tatt inn i kriteriene.

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- expected: 0 funn
- `uv run python manage.py makemigrations --check --dry-run` -- expected: «No changes detected»
- `uv run python manage.py test` -- expected: alle tester grønne
- Bygg CSS med Tailwind-CLI og sjekk at `static/css/app.css` er oppdatert og committet

**Manual checks:**
- `runserver`: logg inn og sjekk toppfeltet på S3 og på en underside. Sjekk Meny, Tilbake og 404.
- Sjekk 320 px bredde og 200 % tekst.
- Kjør axe på alle sider.
