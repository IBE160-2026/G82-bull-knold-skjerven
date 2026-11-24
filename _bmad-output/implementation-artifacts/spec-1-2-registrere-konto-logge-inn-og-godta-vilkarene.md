---
title: 'Story 1.2: Registrere konto, logge inn og godta vilkårene'
type: 'feature'
created: '2026-11-23'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'f0b07ed4ee57676624795695037575161f09d5e4'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Appen har ingen sider. En student kan verken lage konto, logge inn eller ut, og vilkårene (FR-7) godtas ingen steder. Alle senere stories trenger en innlogget bruker som har godtatt vilkårene.

**Approach:** Lag forsiden med innlogging (S1), Registrer (S2), utlogging, personvern-dialogen ved første innlogging (S1b, AD-23) og personvernerklæringen (S15) i `kontoer`, med en enkel `base.html` som story 1.3 senere fyller med toppfelt og design. Startsiden `/` er en midlertidig side som story 1.4 gjør til Oversikt.

## Boundaries & Constraints

**Always:**
- Følg epic-1-context.md, AD-1, AD-8 og AD-23. Norske identifikatorer uten æ, ø og å. Alle tekster i grensesnittet er på norsk bokmål, i du-form og uten utropstegn. Feiltekstene står i `farequiz/feilmeldinger.py`.
- Bare Logg inn, Registrer og Personvernerklæring har `@login_not_required`.
- `vilkar_godtatt` skrives bare av `studier.services.vilkar.godta_vilkar`.
- Utlogging og «Jeg har forstått og godtar» er POST-skjemaer med CSRF. Alt virker uten JavaScript.
- `next` følges bare når den peker på samme vert (Djangos `url_has_allowed_host_and_scheme`).
- WCAG-kravene for skjemaer: synlige etiketter, `autocomplete="email"` og `current-password`/`new-password`, innliming tillatt, ingen CAPTCHA, feilmeldinger over skjemaet koblet med `aria-describedby` og med fokus (`tabindex="-1"` og `autofocus`), én `<h1>`, `<main>` og `lang="nb"`.

- **Beslutning 23.11 (passord):** Bare minst 8 tegn, som FR-1 og prototypen. `AUTH_PASSWORD_VALIDATORS` har bare `MinimumLengthValidator` med `min_length` 8, og meldingen er «Passordet må ha minst 8 tegn.».
- **Beslutning 23.11 (personvernerklæringen):** Kontaktperson er «Ola Normann», og e-post for personvernhenvendelser er «ola@normann.no». Begge plassholderne for e-post fylles med den. «Sist oppdatert» er 23.11.2026. Resten av teksten tas fra prototypen. De åpenbare skrivefeilene («. .» og «, .») rettes.

**Never:**
- Ingen Tailwind, htmx, CSS, toppfelt med Tilbake og Meny, fotlinje eller testmodus-banner. Det er story 1.3.
- Ingen nye migreringer, ingen Django admin og ingen e-postutsending (glemt passord finnes ikke i v1).
- Ingen sjekk av vilkår i `last_opp`. Den kommer i story 2.3.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Ny konto | Gyldig e-post og passord på minst 8 tegn | Bruker med e-post i små bokstaver og hashet passord. Logget inn og sendt til `/`, så videre til S1b | N/A |
| Brukt e-post | «Ola@Eks.no» når «ola@eks.no» finnes | Ingen ny konto. E-posten står igjen | «Det finnes allerede en konto med denne e-posten.» |
| Ugyldig input | Ugyldig e-post, eller passord under 8 tegn | Ingen konto. E-posten står igjen | «Skriv inn en gyldig e-postadresse.» eller «Passordet må ha minst 8 tegn.» |
| Innlogging | Riktig e-post (uansett store og små bokstaver) og passord | Logget inn, sendt til `next` eller `/` | N/A |
| Feil innlogging | Feil passord eller ukjent e-post | Samme melding i begge tilfeller | «Feil e-post eller passord.» |
| Utløpt økt | Utlogget bruker åpner `/emner/3/` | Sendt til innlogging med `next`. Etter innlogging åpnes `/emner/3/` | «Du er logget ut. Logg inn igjen for å fortsette.» vises når `next` finnes og ikke er `/` |
| Vilkår mangler | Innlogget, `vilkar_godtatt` er tom, åpner en side | Sendt til `/vilkar/?next=<siden>` | N/A |
| Unntatt | Samme bruker åpner `/vilkar/`, `/personvern/`, `/logg-ut/` eller en statisk fil | Ikke sendt videre | N/A |
| Godta | POST på `/vilkar/` | Tidspunktet lagres. Sendt til `next` eller `/`. S1b vises ikke igjen | N/A |
| Utlogging | POST på `/logg-ut/` | Logget ut og sendt til innlogging. GET gir 405 | N/A |
| Offentlig side | Utlogget åpner `/personvern/` | Siden vises uten innlogging | N/A |

</frozen-after-approval>

## Code Map

- `farequiz/settings.py` -- legg til `VilkarMiddleware` etter `LoginRequiredMiddleware`, og `LOGIN_URL = "kontoer:logg_inn"`, `LOGIN_REDIRECT_URL = "/"` og `LOGOUT_REDIRECT_URL = "kontoer:logg_inn"`. `AUTH_PASSWORD_VALIDATORS` får bare `MinimumLengthValidator` (8).
- `farequiz/urls.py` -- er tom. Inkluder `kontoer.urls` og startsiden `/`.
- `kontoer/models.py` -- `Bruker` og `BrukerManager` gjenbrukes uendret. `create_user` og `save()` gir e-post med små bokstaver, og `get_by_natural_key` skiller ikke store og små bokstaver, så Djangos `authenticate` virker med e-post.
- `studier/services/__init__.py` -- tom pakke. `vilkar.py` legges ved siden av.
- `farequiz/testrunner.py` -- tvinger testmodus og bruker MD5-hasher. Nye tester trenger ikke noe eget oppsett.
- `templates/` -- finnes ikke ennå (`TEMPLATES.DIRS` peker dit, og `APP_DIRS=True`).
- Tekstene i S1, S1b, S2 og S15 hentes fra `_bmad-output/planning-artifacts/ux-designs/ux-G82-bull-knold-skjerven-2026-11-11/prototype/index.html` (seksjonene `s1`, `s2`, `s15` og `.dialog`).

## Tasks & Acceptance

**Execution:**
- [x] `farequiz/feilmeldinger.py` -- konstanter for meldingene i I/O-matrisen -- én kilde for tekstene
- [x] `studier/services/vilkar.py` -- `godta_vilkar(bruker)` setter `vilkar_godtatt = timezone.now()` bare hvis feltet er tomt, med `update_fields` -- AD-1 og AD-23
- [x] `kontoer/middleware.py` -- `VilkarMiddleware` etter I/O-matrisen. Unntakene slås opp med `reverse` og `STATIC_URL` -- AD-23
- [x] `kontoer/forms.py` -- `RegistrerForm` (e-post og passord, sjekker brukt e-post uten å skille store og små bokstaver) og `LoggInnForm` (`AuthenticationForm` med e-post og den felles meldingen) -- FR-1, FR-2
- [x] `kontoer/views.py`, `kontoer/urls.py` (`app_name = "kontoer"`) -- `/logg-inn/` (S1 med hero, informasjonskort og skjema), `/registrer/`, `/logg-ut/` (POST), `/vilkar/` (S1b) og `/personvern/` (S15). Registrering logger inn og sender til `/` -- FR-1, FR-2, FR-7
- [x] `farequiz/views.py`, `farequiz/urls.py` -- startsiden `/` sier «Du er logget inn som <e-post>» og har Logg ut. Story 1.4 erstatter den -- midlertidig mål for innlogging
- [x] `templates/base.html`, `templates/startside.html`, `templates/kontoer/{logg_inn,registrer,vilkar,personvern}.html` -- `base.html` har `lang="nb"`, blokkene `title` og `innhold`, og et Logg ut-skjema for innloggede. Sidene bruker tekstene fra prototypen -- grunnlag som 1.3 bygger videre på
- [x] `kontoer/tests_sider.py`, `studier/tests/test_vilkar.py` -- én test per rad i I/O-matrisen, pluss en test for usikker `next` (`https://ond.no`), og en test for at `godta_vilkar` ikke overskriver et tidspunkt som finnes

**Acceptance Criteria:**
- Gitt en utlogget besøkende, når hen åpner `/`, så sendes hen til innlogging, og meldingen om utløpt økt vises ikke.
- Gitt S1, når siden vises, så står hero med «Øv på forelesningene dine», «Registrer deg» og tre flashcards med `aria-hidden`, de tre informasjonskortene, skjemaet «Logg inn» og lenkene til Registrer og Personvernerklæring.
- Gitt S1b, når siden vises, så står de fire punktene fra prototypen, en lenke til S15 og knappen «Jeg har forstått og godtar». Uten JavaScript er den en vanlig side.
- Gitt alle nye sider, når HTML-en sjekkes, så har de én `<h1>`, `<main>`, `lang="nb"` og en `<title>` som «Logg inn – FåreQuiz».

## Implementation Notes

- **24.11, implementert og verifisert lokalt.** Subagenten som implementerte, stoppet etter 10 minutter uten fremdrift. Da var koden og malene laget, men ikke testene og ikke `<h1>` og «Sist oppdatert» i personvernerklæringen. Resten ble fullført i hovedøkten.
- **Verifisert:** ruff check og format, og `makemigrations --check` er grønne. 82 tester er grønne (27 nye). En røyktest mot `runserver` gikk gjennom: registrere, bli sendt til S1b, godta og komme til startsiden.
- **Valg:** `LoginView` og `LogoutView` fra Django gjenbrukes, og `LoginView` er alt `@login_not_required` i 5.2. `VilkarView` bruker `RedirectURLMixin`, slik at `next` sjekkes på samme måte som ved innlogging. `next=/logg-ut/` følges ikke etter innlogging.
- **Etter review (runde 1):** åtte rettinger, se triage-loggen. 91 tester er grønne (36 nye).
- **Tester:** `kontoer/tests_sider.py` bruker en egen URL-konfigurasjon med en beskyttet testside på `/emner/<pk>/`, slik at raden «utløpt økt» kan testes før story 1.4. Unntaket for statiske filer testes direkte mot mellomvaren.

## Spec Change Log

## Review Triage Log

Runde 1 (24.11). Lag: B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|---|---|---|---|
| B7, E3, E4, V1 | `next=/logg-ut/` følges etter godta i `VilkarView`, en eksakt strengsammenligning bommer på varianter (`?x=1`, uten skråstrek, absolutt URL), og regelen er ikke testet | low | Stemmer: `POST /vilkar/` med `next=/logg-ut/` sendte til en GET som gir 405, og `/logg-ut/?x=1` slapp gjennom i `LoggInnView`. Felles `UtenUtloggingSomMalMixin` som sammenligner stien, i begge views, med tester. | patch |
| B8, E2 | Innlogget bruker kan åpne Logg inn og Registrer og lage en ny konto som tar over økten | medium | Stemmer: `registrer` sjekket ikke `is_authenticated`, og `login()` byttet økten. `redirect_authenticated_user = True` og en sjekk i `registrer`, med tester. | patch |
| V2 | `IntegrityError`-grenen i `registrer` er ikke testet | low | Stemmer: `test_brukt_epost` stopper i `clean_email`. Test med `mock.patch.object(RegistrerForm, "lagre", side_effect=IntegrityError)`. | patch |
| E1 | Tom POST på `/registrer/` gir et ubundet skjema uten feilmeldinger | low | Stemmer: en tom `QueryDict` er usann, så `request.POST or None` ga `None`. Bindes nå når metoden er POST, med test. | patch |
| E5 | `godta_vilkar` leser feltet i minnet og kan overskrive et lagret tidspunkt | low | Stemmer for et utdatert objekt og to samtidige forespørsler. Betinget `update()` på `vilkar_godtatt__isnull=True`, med test. | patch |
| E6 | Meldingen om utløpt økt forsvinner etter mislykket innlogging | low | Avvik fra matrisen («vises når `next` finnes og ikke er `/`»). Betingelsen `not form.errors` er fjernet, med test. | patch |
| B6 | `VilkarMiddleware` legger `next` på POST og HTMX-forespørsler | low | POST: stemmer, en POST-URL i `next` gir 405 etter godta. Nå får bare GET og HEAD `next`, med test. HTMX finnes ikke ennå, så den delen sikrer en tilstand som ikke er vist. | patch (POST), avvist (HTMX) |
| B10 | Innloggingsfeltet for e-post mangler `maxlength` | low | Stemmer: malen skriver feltet for hånd. `maxlength="254"` er lagt til. Ubrukte widget-innstillinger i skjemaet er ufarlige. | patch |
| B2, E7 | Den nye epic-1-context.md mistet regler som story 1.3–1.6 trenger | medium | Stemmer: build laster bare epic-konteksten, så 1.6 hadde mistet `on_commit`-regelen og 404-testene per modell. Lagt tilbake: `ki`-isolasjon, testmodus, `EIERVEI`, `slett_emne`, HTMX og CSRF, tittelformat, bannertekst, at Tilbake ikke vises på S3, og `seed_testdata`. | patch |
| B3 | Personvernerklæringen lover ting v1 ikke gjør (sletting av konto, varsel per e-post, sletting av logger etter 30 dager) | low | Teksten er Martins fra prototypen og er tatt inn etter beslutningen i spec-en. Den er ikke laget av denne storyen. | defer |
| B4 | Tre lenker i §4.1 går til forsider (`claude.com`, `anthropic.com`), ikke til dokumentene de nevner | low | Kommer fra prototypen. | defer |
| B5 | S1b sier «godtar du våre brukervilkår», men det finnes ingen vilkårsside, og `vilkar_godtatt` har ingen versjon | medium | Teksten kommer fra prototypen, og versjonering er ikke et krav i PRD-en. | defer |
| B1 | Sprint-status sier `in-progress` mens spec-en sier `in-review` | false | Steg 5 setter sprint-status til `review` når spec-en blir `done`. Det er arbeidsflyten, ikke en feil. | avvist |
| B9 | Meldingen er skjult for usikker `next`, og `test_unntatte_sider` dekker flere rader | low | Å skjule meldingen ved usikker `next` er ufarlig og bør ikke låses av en test. At én test dekker flere rader, er kosmetisk. | avvist |
| B11 | `redirect("/")` og `href="/"` er skrevet rett inn | false | `/` forblir startsiden i story 1.4 (Oversikt). `registrer` bruker likevel `LOGIN_REDIRECT_URL` nå. | avvist |
| B12 | Testbrukerens innlogging på S1 i testmodus er ikke lagt til noen story | false | Den står i UX-DR26 og i kriteriene for story 1.3. | avvist |

## Design Notes

- **Meldingen om utløpt økt:** `LoginRequiredMiddleware` sender til `LOGIN_URL?next=…`. Når `next` finnes og ikke er `/`, viser S1 meldingen. En ny besøkende som åpner `/`, får ingen melding.
- **Før story 1.3:** sidene er semantisk HTML uten styling. Story 1.3 bytter ut innholdet i `base.html` (toppfelt, tokens, fotlinje). Sidene i denne storyen skal ikke endres for det.
- **Modal i S1b** (`aria-modal`, fokusfelle) krever JavaScript og hører til story 1.3. Her er S1b en vanlig side.

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- expected: 0 funn
- `uv run python manage.py makemigrations --check --dry-run` -- expected: «No changes detected»
- `uv run python manage.py test` -- expected: alle tester grønne

**Manual checks:**
- `runserver`: registrer en konto, se S1b, godta, logg ut og inn igjen uten S1b, og åpne `/personvern/` utlogget.
