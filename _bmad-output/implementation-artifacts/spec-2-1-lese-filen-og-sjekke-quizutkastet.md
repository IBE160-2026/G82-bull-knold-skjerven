---
title: 'Story 2.1: Lese filen og sjekke quizutkastet'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'd304f5492f961f5e13d1630eea77b6d2a36320cd'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `ki` kan ikke lese en notatfil eller sjekke et svar fra modellen. Det finnes heller ingen testdokumenter som story 2.2 (mock-svar), 6.1 (seed) og 6.4 (KI-kvalitet) kan bygge på.

**Approach:** Legg `les_fil`, `sjekk`, `KIFeil`, `Innhold` og `QuizUtkast` i `ki` (AD-10, AD-11). Lag de fem testdokumentene i `testdokumenter/` med `KILDER.md`, og la testene for `les_fil` bruke dem. Ingen databasetilgang og ikke noe grensesnitt.

## Boundaries & Constraints

**Always:**
- `ki` importerer ingenting fra `studier` eller `kontoer`. Den eksisterende `KiIsolasjonTest` skal fortsatt være grønn.
- `KIFeil(kode)` godtar bare kodene i AD-10: `timeout`, `format`, `for_lite_innhold`, `for_stor`, `api_nokkel`, `api_feil`. En ukjent kode gir `ValueError`.
- `Innhold` og `QuizUtkast` er uforanderlige (frozen dataclasses). Feltnavnene er låst av AD-11.
- `sha256` er hex-digest av filens bytes. For PDF er `data` bytes. For DOCX og TXT er `data` str.
- Typen bestemmes av filendelsen (`.pdf`, `.docx`, `.txt`, uavhengig av store og små bokstaver). Andre endelser gir `KIFeil("api_feil")`.
- Filinnhold logges aldri.
- `.gitattributes` beholdes som det er (`testdokumenter/** binary`).

**Beslutninger 25.11 (Magnus):**
- **Gruppa lager testdokumentene selv.** Fem korte forelesningsnotater om webutvikling (HTML, CSS, HTTP, med ulike temaer per fil). Ett av dem er på engelsk. Innholdet skrives i repoet, og skriptet lager filene. I `KILDER.md` står det «laget av gruppa G82, CC BY 4.0».
- **Den skannede PDF-en simuleres.** Skriptet tegner sidene som bilder med litt skråstilling og støy, uten tekstlag. Den kan byttes med en ekte skanning senere. Da endres hashen, og mock-svarene i 2.2 må lages på nytt.
- **Spec-en beholdes som én story**, selv om den er ca. 2200 tokens.

**Never:**
- Ikke kall modellen og ikke lag `generer`, mock-filer, `visningsnavn` eller `PROMPT_VERSJON`. Det hører til story 2.2.
- Ikke legg til et PDF-bibliotek i appens avhengigheter. PDF-en sendes hel og leses ikke.
- Ikke endre `studier`, `kontoer` eller maler.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| PDF | testdokument `.pdf` | `Innhold(sha256, "pdf", bytes)`, `data` er hele filen | N/A |
| DOCX | testdokumentet `.docx` | `type="docx"`, `data` er teksten i avsnittene med linjeskift mellom | N/A |
| TXT UTF-8 | testdokumentet `.txt` | `type="txt"`, `data` er teksten | N/A |
| TXT cp1252 | bytes med `æøå` i cp1252 | teksten dekodes riktig med cp1252 som reserve | N/A |
| Fil mangler | sti som ikke finnes | ingen retur | `KIFeil("api_feil")` |
| Tom tekst | DOCX eller TXT med bare blanke tegn | ingen retur | `KIFeil("for_lite_innhold")` |
| Gyldig svar | JSON med N spørsmål, tre alternativer, ett riktig | `QuizUtkast` med alle felt. `forhandslagret` er `False` når feltet mangler | N/A |
| Ugyldig JSON | `"{ikke json"` | ingen retur | `KIFeil("format")` |
| Feil antall spørsmål | N−1 eller N+1 spørsmål | ingen retur | `KIFeil("format")` |
| Feil antall alternativer | 2 eller 4 | ingen retur | `KIFeil("format")` |
| Feil antall riktige | 0 eller 2 | ingen retur | `KIFeil("format")` |
| Like alternativer | to alternativer med lik tekst etter `strip().casefold()` | ingen retur | `KIFeil("format")` |
| Like spørsmål | to spørsmål med lik tekst etter `strip().casefold()` | ingen retur | `KIFeil("format")` |
| Manglende felt | hvert påkrevde felt fjernet, ett om gangen, eller tom streng | ingen retur | `KIFeil("format")` |
| Feil type | `er_riktig` som `"true"`, eller `sporsmal` som objekt | ingen retur | `KIFeil("format")` |

</frozen-after-approval>

## Code Map

- `ki/__init__.py` -- har `er_testmodus` og `tving_testmodus`. Legg til de nye offentlige navnene her, eller re-eksporter dem fra undermoduler.
- `ki/tests.py` -- `KiIsolasjonTest` går gjennom alle `.py`-filer under `ki/`. Nye moduler omfattes automatisk.
- `farequiz/feilmeldinger.py` -- brukertekster per feilkode. Ikke rør denne. Kodene i `KIFeil` skal være de samme som nøklene her.
- `.gitattributes` -- `testdokumenter/** binary` er allerede på plass.
- `pyproject.toml` -- `python-docx==1.2.0` finnes. Ingen nye kjøretidsavhengigheter.
- `scripts/` -- inneholder bare `bygg-css.sh`. Generatorskriptet legges her.

## Tasks & Acceptance

**Execution:**
- [x] `ki/feil.py` -- `KIFeil(Exception)` med `kode` og frozenset `KODER` -- AD-10
- [x] `ki/fil.py` -- `Innhold` og `les_fil(sti)` -- FR-9
- [x] `ki/format.py` -- `QuizUtkast`, `Sporsmal` og `Alternativ` (frozen), og `sjekk(raatt, antall)`. Valgfrie felt i JSON: `forhandslagret` (standard `False`). Påkrevde felt: `sprak`, `modell`, `prompt_versjon` og `sporsmal`, med tekst, begrunnelse og alternativer -- FR-13
- [x] `ki/__init__.py` -- re-eksporter `les_fil`, `sjekk`, `KIFeil`, `Innhold` og `QuizUtkast`
- [x] `scripts/lag_testdokumenter.py` og `testdokumenter/` -- de fem filene, `KILDER.md` og skriptet som lager dem. Skriptet kjøres med `uv run --with` for verktøy som bare trengs her, så `uv.lock` ikke endres -- FR-9, FR-12
- [x] `ki/tests_fil.py` og `ki/tests_format.py` (eller en `ki/tests/`-pakke) -- én test per rad i matrisen, `les_fil` på alle fem testdokumentene, og en test som sjekker at hver fil i `testdokumenter/` står i `KILDER.md`

**Acceptance Criteria:**
- Gitt `testdokumenter/`, når storyen er ferdig, så ligger det der en tekst-PDF på ca. 10 sider, en lysbilde-PDF (liggende sider med lite tekst), en skannet PDF (bare bilder, ingen tekstlag), en DOCX og en TXT. Minst én er på et annet språk enn norsk.
- Gitt `KILDER.md`, så oppgir den kilde og lisens for hver fil.
- Gitt `ki`, når den sjekkes, så importerer den ingenting fra `studier` eller `kontoer`.

## Implementation Notes

- **Moduler:** `ki/feil.py`, `ki/fil.py` og `ki/format.py`, som re-eksporteres fra `ki/__init__.py` (med `__all__`). `KIFeil` har `kode` og en valgfri `detalj` for logg. `detalj` er alltid en fast streng, aldri filinnhold.
- **Valg som spec-en ikke tok:**
  - En ødelagt DOCX gir `api_feil`.
  - En tom PDF, eller en fil som ikke er PDF, godtas av `les_fil`. Opplastingen (2.3) og `leser`-steget (2.4) må validere den.
  - TXT som ikke er UTF-8, dekodes med cp1252 og `errors="replace"`.
  - `sjekk` lagrer tekstfeltene uten mellomrom rundt.
- **Testdokumenter:** `scripts/lag_testdokumenter.py` kjøres med `uv run --with reportlab==5.1.1 --with pillow==13.0.0`, så `uv.lock` ikke endres. Resultatet er likt hver gang, uavhengig av OS (`create_system = 3` i DOCX-zipen). Kontrollert ved å kjøre skriptet to ganger og sammenligne hashene.
- **Kjent begrensning:**
  - `les_fil` leser bare avsnittene i en DOCX. Tekst i tabeller, topptekster og tekstbokser kommer ikke med (B6 i triage-loggen).
  - Den skannede PDF-en har 2 sider og lysbilde-PDF-en lite tekst. Det kan bli tynt for 30 spørsmål per nivå i 2.2.
  - `KILDER.md` regnes som binær i git på grunn av `testdokumenter/** binary`, så den vises uten tekstdiff.
- **Verifisert:** ruff check og format, `makemigrations --check`, og 175 tester grønne (39 i `ki`). Ingen endring i `uv.lock` eller `pyproject.toml`.

## Spec Change Log

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 25.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | DOCX-hashen avhenger av OS-et som kjørte generatoren (`ZipInfo.create_system`) | medium | Bekreftet: `zipfile.ZipInfo('a').create_system` er 0 på Windows og 3 ellers. Mock-svarene i 2.2 slås opp på hashen | patch |
| B2 | Ingen sjekk av at generatoren gir de committede filene | low | V kjørte skriptet på nytt og fikk like hasher. En CI-sjekk krever ekstra avhengigheter i CI, mer enn en direkte rettelse | avvist |
| B3 | `KIFeil` med `detalj` kan ikke picklers eller kopieres | low | Stemmer (`args` er én streng), men ingen kode krysser en prosessgrense. Jobbkjeden i 2.4 kjører i samme forespørsel (AD-9) | avvist |
| B4 | `les_fil` hever aldri `for_stor` og har ingen størrelsesgrense | false | `for_stor` kommer fra API-et i `generer` (story 2.2, AC 1), og grensen på 5 MB håndheves ved opplasting (2.3) | avvist |
| B5 | En tom PDF, eller en fil som ikke er PDF, godtas | low | Stemmer, men opplastingen i 2.3 og `leser`-steget i 2.4 validerer filen. En vakt her krever et valg av feilkode som spec-en ikke tar | avvist |
| B6 | DOCX: tekst i tabeller, topptekst og tekstbokser blir borte | low | Stemmer, og matrisen sier «teksten i avsnittene». Forelesningsnotater er for det meste avsnitt. Å ta med tabeller i dokumentrekkefølge er mer enn en direkte rettelse. Nevnt for brukeren | avvist |
| B7 | UTF-16-TXT (Notisblokk «Unicode») blir til søppel med cp1252 | low | Stemmer, men Notisblokk lagrer UTF-8 som standard. Ny gren for BOM-sjekk | avvist |
| B8 | `sjekk` tåler ikke ```` ```json ````-gjerder | false | Story 2.2 bruker structured outputs (`output_config.format`), som gir ren JSON | avvist |
| B9 | `sprak` valideres ikke som BCP 47 | low | Spec-en krever ikke validering. Feil verdi gir ingen feil, bare et uvanlig `lang`-attributt | avvist |
| B10 | DOCX-testen regner fasiten med samme uttrykk som koden | low | Stemmer. Direkte rettelse i testen | patch |
| B11 | Ingen test av at skannet PDF mangler tekstlag, av liggende lysbilder eller av sideantall | medium | Samme som V3 | patch |
| B12 | `test_hver_fil_star_i_kilder` teller skjulte filer og sjekker ikke lisens per rad | low | Stemmer. Direkte rettelse i testen | patch |
| B13 | Mangler tester for `detalj` uten filinnhold, `sjekk(None)` og `OSError` som ikke er «finnes ikke» | low | `detalj` er faste strenger. De to andre grenene fører til samme `KIFeil` som testede grener | avvist |
| B14 | `bryt_linjer` legger til en tom linje når første ord er for bredt | low | Stemmer, men skjer ikke med dagens tekst. Direkte rettelse | patch |
| E1 | DOCX leses to ganger, så hash og tekst kan gjelde ulike bytes | low | Stemmer. Direkte rettelse: les fra bytene som allerede er lest | patch |
| E2 | Tom PDF eller fil som ikke er PDF | low | Samme som B5 | avvist |
| E3 | DOCX-tabeller | low | Samme som B6 | avvist |
| E4 | UTF-16-TXT | low | Samme som B7 | avvist |
| E5 | Ingen størrelsesgrense i `les_fil` | false | Samme som B4 | avvist |
| E6 | `sti=None` gir `TypeError` | false | Programmeringsfeil som feiler høylytt. Kallerne sender alltid en sti | avvist |
| E7 | Dypt nøstet JSON gir `RecursionError` | low | Stemmer. Direkte rettelse: legg til i `except` | patch |
| E8 | `antall` på 0, negativt eller tekst | false | Skjemaet i 2.4 begrenser til 5–30 (FR-11). Ingen kaller sender noe annet | avvist |
| E9 | Like tekster med ulikt antall mellomrom inni går gjennom | low | Stemmer. Direkte rettelse av normaliseringen | patch |
| E10 | `KIFeil` med en kode som ikke kan hashes, gir `TypeError` | false | Programmeringsfeil som feiler høylytt | avvist |
| E11 | `bryt_linjer` tom linje | low | Samme som B14 | patch |
| E12 | Skjulte filer i `testdokumenter/` | low | Samme som B12 | patch |
| V1 | UTF-8-testfila er ren ASCII, så dekoding av æøå og BOM testes ikke | medium | Kontrollert av V. Norske UTF-8-notater er det vanlige tilfellet | patch |
| V2 | Ingen test av at `sjekk` fjerner mellomrom rundt feltene | low | Kontrollert av V | patch |
| V3 | Ingen test av egenskapene til PDF-testfilene | medium | Kontrollert av V. Story 6.4 bygger på at skanningen ikke har tekstlag | patch |

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne, også de nye testene i `ki`
- `git diff --stat main -- uv.lock pyproject.toml` -- tom
