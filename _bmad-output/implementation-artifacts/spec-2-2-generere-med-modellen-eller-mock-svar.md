---
title: 'Story 2.2: Generere med modellen eller mock-svar'
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

**Problem:** `ki` kan lese en fil og sjekke et svar (story 2.1), men kan ikke lage et svar. Uten mock-svar kan ikke sensor kjøre appen uten gruppas API-nøkkel (FR-27, NFR-3).

**Approach:** Legg til `generer(innhold, vanskelighetsgrad, antall, timeout) -> RaattSvar`, `visningsnavn(modell)` og `PROMPT_VERSJON` i `ki` (AD-11, AD-12). Utenfor testmodus kalles modellen. I testmodus hentes svaret fra mock-filene. Kommandoen `lag_mocksvar` lager mock-filene fra de fem testdokumentene.

## Boundaries & Constraints

**Always:**
- `ki` importerer ingenting fra `studier` eller `kontoer`, og hever bare `KIFeil` med kodene fra AD-10.
- `er_testmodus()` er eneste kilde til testmodus. I testmodus gjøres ingen nettverkskall.
- `RaattSvar` er frozen og har `tekst`, `forhandslagret`, `modell` og `prompt_versjon`. `tekst` er JSON som `sjekk(raatt.tekst, antall)` kan lese direkte. `generer` setter `modell`, `prompt_versjon` og `forhandslagret` inn i JSON-objektet når modellen svarer med et gyldig objekt. Ellers returneres teksten uendret, så `sjekk` gir `format`.
- `vanskelighetsgrad` er `lett`, `middels` eller `vanskelig` (samme verdier som `Vanskelighetsgrad` i `studier`, men uten import derfra). `antall` er 1–30.
- Prompten og skjemaet ligger i `ki`. `PROMPT_VERSJON = "1"` er definert ett sted.
- **Modellkallet:**
  - Modellen er `settings.KI_MODELL`. Bruk `anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)` med `timeout=timeout` og `max_retries=0`, så fristen på 120 s holder.
  - En PDF sendes som `document`-blokk (base64). DOCX og TXT sendes som tekst.
  - `output_config` har `format` (JSON-skjema med `sprak` og `sporsmal`) og `effort: "medium"`.
  - Server-side fallback ved avslag (`betas=["server-side-fallback-2026-07-01"]`, `fallbacks="default"`).
  - `modell` i svaret er `response.model`.
- **Feilkoder:**
  - `AuthenticationError` og `PermissionDeniedError` gir `api_nokkel`.
  - `RequestTooLargeError`, `ContentTooLargeError`, og `BadRequestError` der meldingen nevner sider (`page`), gir `for_stor`.
  - `APITimeoutError` gir `timeout`.
  - `stop_reason == "refusal"` og alle andre `anthropic.APIError` gir `api_feil`.
  - Filinnhold logges aldri.
- **Mock:**
  - `ki/mock/manifest.json` er `{"standard": "<dokument>", "filer": {"<sha256>": "<dokument>"}}`.
  - `ki/mock/<dokument>/<vanskelighetsgrad>.json` har `sprak`, `modell`, `prompt_versjon` og 30 spørsmål.
  - `generer` returnerer de første `antall`. En ukjent sha256 gir standarddokumentet med `forhandslagret=True`.

**Beslutninger 25.11 (Magnus):**
- **Bygg nå, kjør senere.** Koden og `lag_mocksvar` bygges i denne storyen uten API-nøkkel. Testene av mock-veien bruker egne testfiler gjennom en mappe som kan patches (`ki.generering.MOCK_MAPPE`), ikke `ki/mock/`. Den som har gruppas nøkkel, kjører `lag_mocksvar` senere og committer `ki/mock/`. Story 2.2 står i `review` til da.
- En test går gjennom alle mock-filene som finnes i `ki/mock/`, og sjekker dem med `sjekk(..., 30)`. Den gir ingen feil så lenge mappen er tom.
- **Spec-en beholdes som én story** (ca. 2400 tokens).

**Never:**
- Ikke rør `studier`, `kontoer`, maler, `uv.lock` eller `pyproject.toml`.
- Ingen database, jobb eller visning (story 2.3–2.4).
- Ikke håndskrevne eller oppdiktede mock-svar i `ki/mock/`. De skal komme fra ekte genereringer (NFR-9).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Mock, kjent fil | testmodus, sha256 i manifestet, `antall=10` | `RaattSvar` med de første 10 spørsmålene fra riktig fil og nivå, `forhandslagret=False`, `modell` og `prompt_versjon` fra filen. `sjekk(tekst, 10)` godtar den | N/A |
| Mock, ukjent fil | testmodus, ukjent sha256 | Standarddokumentet, `forhandslagret=True` | N/A |
| Mock, 30 | `antall=30` på hvert dokument og nivå | Alle 30, og `sjekk` godtar dem | N/A |
| Mock, blokkert nett | testmodus, `socket.socket.connect` hever | Svar som over | Ingen kall forsøkes |
| Modell, gyldig | ikke testmodus, falsk klient gir JSON | `tekst` har modellens felt pluss `modell=response.model`, `prompt_versjon` og `forhandslagret=false` | N/A |
| Modell, ugyldig JSON | falsk klient gir `"ikke json"` | `tekst` er uendret | `sjekk` gir `format` |
| Ugyldig nøkkel | `AuthenticationError` | — | `KIFeil("api_nokkel")` |
| For stor | `RequestTooLargeError`, eller `BadRequestError` med «page» | — | `KIFeil("for_stor")` |
| Timeout | `APITimeoutError` | — | `KIFeil("timeout")` |
| Andre feil | `APIConnectionError`, `InternalServerError`, avslag | — | `KIFeil("api_feil")` |
| Ugyldig valg | `vanskelighetsgrad="ekstrem"` eller `antall=0` / `31` | — | `ValueError` |
| Visningsnavn | `claude-sonnet-5-5`, `claude-haiku-5-5`, `claude-opus-5` | «Claude Sonnet 5.5», «Claude Haiku 5.5», «Claude Opus 5» | Ukjent form gir strengen uendret |

</frozen-after-approval>

## Code Map

- `ki/__init__.py` -- re-eksporterer `les_fil`, `sjekk`, `KIFeil`, `Innhold` og `QuizUtkast`, og har `er_testmodus` og `tving_testmodus`. Legg til `generer`, `RaattSvar`, `visningsnavn` og `PROMPT_VERSJON`.
- `ki/fil.py` -- `Innhold(sha256, type, data)`. PDF-data er bytes, DOCX/TXT er str.
- `ki/format.py` -- `sjekk(raatt, antall)` krever `sprak`, `modell`, `prompt_versjon` og `sporsmal`. `forhandslagret` er valgfri (standard `false`).
- `ki/tests.py` -- `KiIsolasjonTest` sjekker importene i alle `.py`-filer i `ki`. Testene for `er_testmodus` patcher `ki._tvunget`.
- `farequiz/testrunner.py` -- tvinger testmodus i alle tester. Tester av modellveien må patche `ki._tvunget=False`, sette innstillinger og bytte klienten med en falsk.
- `farequiz/settings.py:50-52` -- `ANTHROPIC_API_KEY`, `KI_MODELL` (standard `claude-sonnet-5-5`) og `TESTMODUS`.
- `testdokumenter/` -- fem filer. `les_fil` gir sha256 for manifestet.
- `.gitattributes` -- `ki/mock/** -text` er på plass.
- `anthropic` 2.11.0 er installert og har `RequestTooLargeError`, `ContentTooLargeError`, `APITimeoutError` og de andre klassene over.

## Tasks & Acceptance

**Execution:**
- [x] `ki/generering.py` -- `RaattSvar`, `PROMPT_VERSJON`, prompt og skjema, `generer` med modellvei og mock-vei, og `visningsnavn` -- AD-11, AD-12
- [x] `ki/__init__.py` -- re-eksporter de nye navnene
- [x] `ki/management/commands/lag_mocksvar.py` -- nekter å kjøre i testmodus. For hvert testdokument og nivå: `generer(..., 30, timeout=300)` og `sjekk(..., 30)`, med ett nytt forsøk ved `format`. Skriver mock-filene og `manifest.json` (standard: tekst-PDF-en). Skriver ut varighet per kall, ikke innhold
- [x] `ki/tests_generering.py` -- én test per rad i matrisen. Modellveien testes med en falsk klient (ingen nettverk). Kommandoen testes med en falsk `generer`
- [x] `README.md` -- kort avsnitt om testmodus og `lag_mocksvar`

**Acceptance Criteria:**
- Gitt testmodus, når hele testsuiten kjører, så gjøres ingen nettverkskall (NFR-3).
- Gitt `ki`, når den sjekkes, så importerer den ingenting fra `studier` eller `kontoer`, og `PROMPT_VERSJON` er definert ett sted.

## Implementation Notes

- **`ki/generering.py`:** `RaattSvar`, `PROMPT_VERSJON = "1"`, systemprompt, JSON-skjema, `generer` og `visningsnavn`.
  - `MOCK_MAPPE` kan patches i tester.
  - `er_testmodus` importeres lokalt i `generer`, så tester som patcher `ki._tvunget`, virker.
- **Modellkallet:** `client.beta.messages.create` med `KI_MODELL`, `max_tokens=16000`, `output_config` (skjema og `effort: "medium"`), `betas=["server-side-fallback-2026-07-01"]` og `fallbacks="default"`.
  - Klienten har `timeout=timeout` og `max_retries=0`.
  - En PDF sendes som `document`-blokk. Tekst sendes i `<notat>…</notat>`.
  - Feildetaljer inneholder bare navnet på unntaksklassen.
- **Feilkoder:**
  - `RequestTimeoutError` (408) og `GatewayTimeoutError` (504) gir også `timeout`.
  - Siste ledd fanger `anthropic.AnthropicError`, så `generer` bare hever `KIFeil` (og `ValueError` ved ugyldig valg).
- **`lag_mocksvar`:**
  - Ett nytt forsøk ved `format`, `timeout` og `api_feil`.
  - Ingenting skrives før alle 15 er godkjent.
  - Varigheten per kall skrives ut. Den er grunnlaget for å måle mot fristen på 120 s.
- **Ikke prøvd mot ekte API.** Det er ingen nøkkel. Body og header er kontrollert gjennom SDK-en med en falsk HTTP-transport.
  - `ki/mock/` er tom til `lag_mocksvar` kjøres, og til da gir generering i testmodus `api_feil`.
  - `max_tokens` og fjerning av `skipTest`-vakten står i `deferred-work.md`.
- **Verifisert:** ruff, `makemigrations --check` og 226 tester grønne (1 hoppet over: manifestet finnes ikke ennå). Ingen endring i `uv.lock`, `pyproject.toml`, `studier`, `kontoer` eller maler.

## Spec Change Log

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 25.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | `stop_reason == "max_tokens"` blir `format`, og det nye forsøket feiler trolig likt | maybe-false | Avhenger av om 16000 tokens holder for 30 spørsmål. Avgjøres ved første ekte kjøring. Hvis det stemmer, er det middels | defer |
| B2 | `RequestTooLargeError` er et alias for `ContentTooLargeError` | low | Bekreftet: `RequestTooLargeError is ContentTooLargeError` er `True` i 2.11.0. Direkte rettelse | patch |
| B3 | Treff på «page» i meldingen er for løst | low | Ordlyden i API-et er ikke kjent. En annen 400-feil som nevner «page», er lite sannsynlig, og en bedre sjekk krever kjent feilform | avvist |
| B4 | Utdaterte mock-svar etter at `PROMPT_VERSJON` er økt, oppdages ikke | low | Stemmer. Én linje i testen | patch |
| B5 | Testen av manifestet hopper stille ut med `return` | low | Stemmer. `skipTest` gjør hullet synlig. Fjerning av vakten er utsatt (V1) | patch |
| B6 | README sier ikke at `ki/mock/` mangler | low | Stemmer. Direkte rettelse | patch |
| B7 | Én forbigående feil i `lag_mocksvar` kaster bort alle betalte kall | medium | Bekreftet: `max_retries=0`, og bare `format` får nytt forsøk | patch |
| B8 | Gamle dokumentmapper fjernes ikke | low | Testdokumentene skifter sjelden navn. Rettelsen krever opprydding eller bytte av hele mappen | avvist |
| B9 | Testene importerer `httpx2` uten å deklarere den | low | `anthropic` er låst til < 3. Å endre det krever en annen måte å lage feilene på | avvist |
| B10 | `</notat>` i notatet bryter avgrensningen | low | Gjelder bare brukerens egen quiz fra egen fil. Ingen andre rammes | avvist |
| B11 | Uventet form på svaret gir andre unntak enn `KIFeil` | false | SDK-en gir typede objekter. `content` og `model` finnes alltid på `Message`. `_les_json`-delen tas i E2 | avvist |
| B12 | `except ValueError, RecursionError:` ser ut som Python 2 | false | Gyldig syntaks i Python 3.14 (PEP 758), som prosjektet krever. Ingen feil | avvist |
| B13 | Testhull: `ContentTooLargeError`, DOCX-blokk og varighet | low | Stemmer. Direkte testtillegg. Feil manifest dekkes av V2. Sammenslåtte tekstblokker og færre spørsmål enn `antall` (gir `format`) er avvist | patch |
| B14 | Filtypene er hardkodet to ganger i testene | low | Stemmer. Bruk `ki.fil.TYPER` | patch |
| E1 | Manifestet peker på noe som ikke er tekst, eller på `../x` | low | Manifestet er en committet fil som kommandoen skriver selv. Kan ikke nås fra brukerdata | avvist |
| E2 | Dypt nøstet mock-JSON gir `RecursionError` | low | Stemmer. Direkte rettelse | patch |
| E3 | `timeout` som `None`, 0 eller negativt tall | false | Kallerne sender 120 eller 300. Programmeringsfeil, ikke vist at det kan skje | avvist |
| E4 | 408 og 504 fra serveren blir `api_feil`, ikke `timeout` | low | Bekreftet: `RequestTimeoutError` og `GatewayTimeoutError` arver ikke fra `APITimeoutError`. Direkte rettelse | patch |
| E5 | `CredentialsError` slipper ut av `generer` | low | Bekreftet: arver fra `AnthropicError`, ikke fra `APIError`. Direkte rettelse | patch |
| E6 | Treff på «page» | low | Samme som B3 | avvist |
| E7 | `max_tokens` | maybe-false | Samme som B1 | defer |
| E8 | `</notat>` | low | Samme som B10 | avvist |
| E9 | `testdokumenter/` mangler | low | Utviklerkommando. Traceback er nok | avvist |
| E10 | `les_fil` hever `KIFeil` i kommandoen | low | Testdokumentene er testet i 2.1. Traceback er nok | avvist |
| E11 | To testdokumenter med samme navn eller hash | low | Gruppa styrer mappen selv | avvist |
| E12 | `OSError` midt i skrivingen | low | Kommandoen kjøres på nytt. Atomisk bytte av mappen er mer enn en direkte rettelse | avvist |
| V1 | Mock-veien testes ikke mot ekte `ki/mock/` | medium | Bevisst utsatt etter beslutningen 25.11 | defer |
| V2 | Grenene for ugyldig manifest og ugyldig mock-fil er ikke testet | medium | Kontrollert av V | patch |

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne
- `git diff --stat main -- uv.lock pyproject.toml studier kontoer templates` -- tom
