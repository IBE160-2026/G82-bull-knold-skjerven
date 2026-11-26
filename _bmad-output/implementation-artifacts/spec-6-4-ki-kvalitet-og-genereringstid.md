---
title: 'Story 6.4: KI-kvalitet og genereringstid'
type: 'feature'
created: '2026-11-26'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '4233d1ec4848551a392c4c69c5ee78e8907192db'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-6-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Ingen har målt om quizene fra ekte modell holder formkravene (SM-4), er gode nok (SM-2, minst 90 %) eller lages godt under 120 s (FR-15, NFR-7). Det finnes heller ikke noe verktøy som gjør dette. Endres prompt, skjema eller `effort` uten at `PROMPT_VERSJON` økes, merker ingen det.

**Approach:** «Bygg nå, kjør senere» (beslutning 26.11): det finnes ingen API-nøkkel her. En målekommando kjører de fem testdokumentene på tre nivåer mot ekte modell, sjekker SM-4 og språket automatisk, måler tiden for 30 spørsmål fra tekst-PDF-en og skriver en rapport med en tabell for den manuelle vurderingen. En dokumentmal tar imot resultatet. En test låser `PROMPT_VERSJON` til innholdet i prompten. Kjøringen, vurderingen og eventuelle endringer av `effort` gjøres senere med nøkkel.

## Boundaries & Constraints

**Always:**
- Kommandoen nekter å kjøre i testmodus, som `lag_mocksvar`, og bruker `ki.generer` og `ki.sjekk` slik appen gjør. Ingen egen modellkode.
- En feil i ett kall (`KIFeil`) stopper ikke kjøringen. Den føres i rapporten med feilkode og tid.
- Rapporten inneholder aldri API-nøkkelen og aldri filinnholdet, bare spørsmålene modellen laget.
- Rapporten skrives først når alle kallene er ferdige, så det aldri ligger en halvferdig rapport.
- Testene gjør ingen nettverkskall. `generer` mockes.

**Never:**
- Ikke endre `EFFORT`, `MAKS_TOKENS`, prompten eller standardmodellen i denne storyen. Det avgjøres etter målingen.
- Ikke bytt til uttrukket tekst for PDF. Valget dokumenteres i malen.
- Ikke kjør kommandoen mot ekte modell i tester eller CI.

**Beslutninger 26.11 (Magnus):**
- Bygg nå, kjør senere. Ingen API-nøkkel i denne økten.
- Kvalitetskjøringen lager 10 spørsmål per quiz som standard, altså 150 spørsmål å vurdere. Tallet kan overstyres med `--antall`. Tidsmålingen bruker 30.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Testmodus | Kommandoen kjøres uten nøkkel | `CommandError`, ingen kall og ingen fil | N/A |
| Alt i orden | 15 kvalitetskall og 3 tidskall gir gyldige svar | Rapport med SM-4 «OK» for hver rad, språk som ventet, tider, typisk (median) og lengste tid, og én vurderingsrad per spørsmål | N/A |
| Feil antall eller form | `sjekk` hever `KIFeil("format")` | Raden får «feil: format» og stoppgrunnen fra svaret. Kjøringen går videre | Føres i rapporten |
| Avkuttet svar | `stop_reason == "max_tokens"` | Stoppgrunnen «max_tokens» står i raden, så avkutting skilles fra andre formatfeil | Føres i rapporten |
| Feil språk | `utkast.sprak` er ulikt det ventede for dokumentet (`en` for TXT, ellers `nb`) | SM-4-raden er OK, men språkkolonnen viser avviket | N/A |
| Tidskall over 120 s | Et tidskall tar 130 s | Tiden står, og raden er merket «over 120 s» | N/A |
| Valg | `--modell claude-haiku-5-5 --effort low --antall 5 --runder 2` | Kallene bruker valgene, og de står i rapportens topp | Ugyldig `--effort` eller `--antall` gir `CommandError` før kall |
| Promptendring | `SYSTEMPROMPT`, `SKJEMA`, `_NIVAER` eller `EFFORT` endres uten ny `PROMPT_VERSJON` | Testen feiler og sier at `PROMPT_VERSJON` må økes og mock-svarene lages på nytt | N/A |

</frozen-after-approval>

## Code Map

- `ki/generering.py` -- `generer`, `_fra_modell` (`svar.stop_reason` og `svar.model`), `RaattSvar` (frosset dataclass), `EFFORT = "medium"`, `MAKS_TOKENS = 16000`, `PROMPT_VERSJON = "1"`, `SYSTEMPROMPT`, `SKJEMA`, `_NIVAER`, `VANSKELIGHETSGRADER`. Modellen leses fra `settings.KI_MODELL` ved hvert kall.
- `ki/format.py` `sjekk(raatt, antall)` -- gir `QuizUtkast` (`sprak`, `modell`, `sporsmal` med `alternativer`) eller hever `KIFeil("format")`.
- `ki/management/commands/lag_mocksvar.py` -- mønsteret: nekter i testmodus, går gjennom `testdokumenter/` med `ki.fil.TYPER`, `les_fil`, `timeout`, varighet med `time.monotonic()`. Gjenbruk stil, ikke kode.
- `ki/tests_generering.py` `LagMocksvarTest` -- slik kommandoen testes: `mock.patch.object(ki, "_tvunget", False)`, `override_settings(TESTMODUS="0", ANTHROPIC_API_KEY=...)`, falsk `generer` og `lag_quiz` fra testene.
- `testdokumenter/KILDER.md` -- språkene: `javascript-og-dom.txt` er `en`, de fire andre er `nb`.
- `ki/__init__.py` -- `ki` importerer aldri fra `studier` eller `kontoer`.
- `README.md` «For gruppa» -- én linje om kommandoen.

## Tasks & Acceptance

**Execution:**
- [x] `ki/generering.py` -- legg til `stoppgrunn: str = ""` sist i `RaattSvar`, satt fra `svar.stop_reason` i `_fra_modell`. Eksisterende konstruktører virker uendret -- skiller avkutting fra andre formatfeil
- [x] `ki/management/commands/maal_ki_kvalitet.py` -- ny kommando med valgene `--antall` (standard 10, 1–30), `--runder` (tidsmålinger, standard 3), `--modell` (overstyrer `KI_MODELL`), `--effort` (`low`, `medium`, `high`, overstyrer `EFFORT` under kjøringen) og `--ut` (mappe, standard `_bmad-output/implementation-artifacts/ki-kvalitet/`).
  - Kvalitet: hvert testdokument × nivå med `--antall`. Tid: `html-struktur-og-semantikk.pdf`, middels, 30 spørsmål, `--runder` ganger. `timeout=300`, så lange tider måles i stedet for å kuttes.
  - Skriver `ki-kvalitet-<yyyy-mm-dd-HH-MM>-<modell>.md`: topp med dato, modell (fra svaret), `PROMPT_VERSJON`, `effort`, `MAKS_TOKENS` og valgene. SM-4-tabell (dokument, nivå, resultat, antall, språk ventet/fått, tid, stoppgrunn). Tidstabell med median og lengste tid. Per quiz en tabell med ett spørsmål per rad (spørsmål, alternativene med det riktige merket, begrunnelse) og tomme kolonner «Relevant», «Riktig fasit», «Ikke tvetydig» og «Merknad». Nederst en kort instruks for å regne ut andelen (mål ≥ 90 %).
  - Skriver ut én linje per kall med dokument, nivå, resultat og tid, aldri innhold. Til slutt stien til rapporten
- [x] `ki/tests_maal_ki_kvalitet.py` -- dekker matrisen med falsk `generer`: testmodus, alt i orden (antall kall, kolonner, median og lengste), format med stoppgrunn, max_tokens, feil språk, over 120 s, valgene og ugyldige valg. Ingen fil ved `CommandError`. Rapporten inneholder ikke API-nøkkelen
- [x] `ki/tests_generering.py` -- `PromptVersjonTest`: sha256 av `SYSTEMPROMPT`, `json.dumps(SKJEMA, sort_keys=True)`, `_NIVAER` og `EFFORT` er låst i testen for `PROMPT_VERSJON = "1"`. Feilmeldingen sier at `PROMPT_VERSJON` må økes, fingeravtrykket oppdateres og mock-svarene lages på nytt med `lag_mocksvar`
- [x] `_bmad-output/implementation-artifacts/ki-kvalitet-6-4.md` -- dokumentmal for resultatet: oppsett (modell, dato, `PROMPT_VERSJON`, `effort`), SM-4, SM-2 med andel og eksempler på dårlige spørsmål, språk (FR-12), tid (typisk og lengste mot 120 s), valget hel PDF mot uttrukket tekst og Sonnet mot Haiku med begrunnelse, konklusjon (`effort`, eventuell PRD-endring). Feltene står tomme med en kort forklaring av hva som skal inn, og øverst står kommandoene som skal kjøres
- [x] `README.md` -- én linje under «For gruppa» om `maal_ki_kvalitet` og at den krever nøkkel og koster API-kall

**Acceptance Criteria:**
- Given at nøkkelen er satt og testmodus er av, when `uv run python manage.py maal_ki_kvalitet` kjøres, then lages én rapport med 15 kvalitetsrader, 3 tidsmålinger og én vurderingsrad per spørsmål.
- Given vanlig `uv run python manage.py test`, when den kjøres, then gjøres ingen nettverkskall, og alle testene er grønne.

## Implementation Notes

## Spec Change Log

## Review Triage Log

| # | Funn | Verdict | Bevis | Rute |
|---|------|---------|-------|------|
| B1/V1/E12 | Fingeravtrykket dekker ikke oppgaveteksten og `<notat>`-innpakningen i `_innhold_blokker` | medium | Bare fire deler hashes. Oppgaveteksten sjekkes bare med delstrenger | patch |
| B2/E5/E6 | Avslag og hvilken formatregel som feilet vises ikke | medium | `_fra_modell` hever før `RaattSvar` lages, og `feil.detalj` skrives ikke i rapporten | patch |
| B3 | «Lengste» utelater runder som feilet | medium | `ok_tider` har bare OK-runder, så en timeout på 300 s skjules i sammendraget | patch |
| B4 | Målt tid er ikke den brukeren venter, siden fristen i appen også dekker `les_fil` og nytt forsøk | medium | `studier/services/generering.py` teller fra `jobb.startet` med ett nytt forsøk ved `format`. Rettes med en forklaring i rapporten og malen | patch |
| B5 | Bare ett dokument tidsmåles, og tidene for kvalitetskallene oppsummeres ikke | low | Den skannede PDF-en og lysbilde-PDF-en kan være tregest. Rettes med en linje for lengste kall og merke over 120 s | patch |
| B6 | Tokenbruken lagres ikke, og det finnes ikke noe valg for uttrukket tekst | low | Spec-en ba ikke om det. Prisen kan leses i Anthropic-konsollen. Avvist | reject |
| B7/E7 | Modellen vises ikke per rad, selv om reservemodellen kan svare | medium | `fallbacks="default"`, og rapporten viser bare settet av modeller | patch |
| B8/E9 | Ventet språk avgjøres av filtypen | low | Direkte rettelse med et fast kart fra filnavn til språk | patch |
| B9 | Et avbrudd kaster bort betalte kall, og skrivingen er ikke atomisk | low | Spec-en krever med vilje at det aldri skrives en halvferdig rapport. Avvist | reject |
| B10/E3 | To kjøringer i samme minutt overskriver hverandre | low | Direkte rettelse: sekunder og effort i filnavnet | patch |
| B11/E11 | Testen av kommandolinjevalgene består av feil grunn (testmodus) | medium | `call_command` uten å slå av testmodus, og bare unntakstypen sjekkes | patch |
| B12 | Feilveiene og standardmappen er ikke testet | low | Avvist bortsett fra språkkoden, som V3 dekker | reject |
| B13 | Sjekken av at filinnhold ikke er med er tynn | low | Avvist | reject |
| B14 | Status ulik. Uklart om rapporten skal committes. Testen med ny klone er ikke navngitt. `FRIST` dupliserer `TIDSFRIST` | low | Status settes i steg 5 (false). Resten rettes direkte i malen og med en kommentar | patch |
| V2 | Ingen test viser at `--effort` og `--modell` kommer fram til forespørselen | medium | Den falske `generer` leser verdiene selv, og `_fra_modell` kjører aldri | patch |
| V3 | `nb-NO` og store bokstaver i språkkoden er ikke testet | medium | Modellen kan svare med BCP 47 og region | patch |
| E1 | HTML-tagger i spørsmålene forsvinner når rapporten vises | medium | HTML-notatet gir spørsmål med `<nav>` og lignende, og `_celle` escaper ikke `<` | patch |
| E2 | En ugyldig `--ut` oppdages først etter alle de betalte kallene | medium | `mkdir` og skrivingen skjer etter kallene | patch |
| E4 | `--runder` har ingen øvre grense | low | Brukeren velger selv. Avvist | reject |
| E8 | En annen fil med samme stamme som tids-PDF-en | low | Finnes ikke i `testdokumenter/`. Avvist | reject |
| E10 | Mappen `testdokumenter` mangler | low | Er i repoet. Avvist | reject |

## Design Notes

Median som «typisk» tid, fordi én treg runde ikke skal flytte den. `--effort` overstyres med `mock.patch.object`-lignende tilordning til `generering.EFFORT` i en `try/finally`, så verdien alltid settes tilbake. `--modell` bruker `override_settings(KI_MODELL=...)`. Rapporten skrives med LF og UTF-8. `|` og linjeskift i spørsmålstekst escapes, så tabellen holder.

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- expected: rent
- `uv run python manage.py test` -- expected: alle grønne, ingen nettverk
- `uv run python manage.py makemigrations --check --dry-run` -- expected: ingen endringer
- `uv run python manage.py maal_ki_kvalitet` uten nøkkel -- expected: `CommandError` om testmodus, ingen fil

**Manual checks (if no CLI):**
- Selve kjøringen mot ekte modell og den manuelle vurderingen gjøres av gruppa med nøkkel og føres i `ki-kvalitet-6-4.md`.
