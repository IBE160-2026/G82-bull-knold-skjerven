# KI-kvalitet og genereringstid 6.4

Story 6.4, spec `spec-6-4-ki-kvalitet-og-genereringstid.md`. Krav: SM-2, SM-4, FR-12, FR-15, NFR-7.

Malen fylles ut etter kjøringen mot ekte modell. Feltene står tomme med en kort forklaring av hva som skal inn. Rapporten fra kommandoen ligger i `ki-kvalitet/` og er grunnlaget.

## Slik kjører du målingen

Krever gruppas API-nøkkel og koster API-kall (15 kvalitetskall og 3 tidskall med standardvalgene). Sett `ANTHROPIC_API_KEY` og `TESTMODUS=0` i `.env` først.

    uv run python manage.py maal_ki_kvalitet

Kommandoen skriver `ki-kvalitet/ki-kvalitet-<dato-og-tid>-<modell>-<effort>.md` her i mappen. Rapporten committes sammen med den utfylte malen. Den inneholder bare spørsmålene modellen laget, aldri filinnholdet eller nøkkelen. Valg:

- `--antall N`: spørsmål per quiz i kvalitetskjøringen, 1–30 (standard 10, altså 150 spørsmål å vurdere).
- `--runder N`: antall tidsmålinger med 30 spørsmål fra `html-struktur-og-semantikk.pdf` (standard 3).
- `--modell NAVN`: overstyrer `KI_MODELL`, for eksempel `claude-haiku-5-5` for å sammenligne med Haiku.
- `--effort low|medium|high`: overstyrer `EFFORT` under kjøringen, for å prøve en annen verdi før den endres i koden.
- `--ut MAPPE`: en annen mappe for rapporten.

Eksempel som sammenligner Haiku med lavere effort:

    uv run python manage.py maal_ki_kvalitet --modell claude-haiku-5-5 --effort low

Endres `EFFORT`, prompten eller skjemaet i `ki/generering.py` etterpå, økes `PROMPT_VERSJON`, fingeravtrykket i `PromptVersjonTest` oppdateres, og mock-svarene lages på nytt med `uv run python manage.py lag_mocksvar`. Så kjøres `seed_testdata` og testen med ny klone fra story 6.2 igjen.

## 1. Oppsett

| | |
|---|---|
| Dato | *(datoen kjøringen ble gjort)* |
| Modell | *(modellen i svarene, fra rapportens topp)* |
| `PROMPT_VERSJON` | *(fra rapportens topp)* |
| `effort` | *(fra rapportens topp)* |
| `MAKS_TOKENS` | *(fra rapportens topp)* |
| Rapport | *(filnavnet i `ki-kvalitet/`)* |
| Kjørt av | *(navn)* |

## 2. SM-4: form

*(Hvor mange av de 15 quizene besto `sjekk` med nøyaktig valgt antall, tre ulike alternativer, ett riktig og ingen like spørsmål. List radene med «feil» og stoppgrunnen. `max_tokens` betyr avkuttet svar og peker mot `MAKS_TOKENS`.)*

| | |
|---|---|
| Quizer som besto | *( av 15)* |
| Feil | *(dokument, nivå, feilkode, stoppgrunn)* |

## 3. SM-2: kvalitet

*(Fra den manuelle vurderingen i rapporten. Et spørsmål er godt når det er relevant, har riktig fasit og ikke er tvetydig. Målet er minst 90 %.)*

| | |
|---|---|
| Vurderte spørsmål | |
| Gode spørsmål | |
| Andel | *( %, mål ≥ 90 %)* |
| Vurdert av | *(navn)* |

### Eksempler på dårlige spørsmål

*(Noen få eksempler med dokument, nivå, spørsmålet og hva som er galt: ikke relevant, feil fasit eller tvetydig. Ta også med spørsmål meldt som feil i appen (4.3) hvis det finnes noen.)*

## 4. Språk (FR-12)

*(Er spørsmålene på notatets språk, og stemmer `sprak` med ventet: `en` for `javascript-og-dom.txt`, `nb` for de fire andre. List avvikene fra språkkolonnen i rapporten.)*

## 5. Genereringstid (FR-15, NFR-7)

*(30 spørsmål fra `html-struktur-og-semantikk.pdf`, middels. Fra tidstabellen i rapporten. Typisk er medianen av rundene med OK, og lengste gjelder alle rundene.)*

Den målte tiden er bare `generer` og `sjekk` for ett kall. Appens frist på 120 s teller fra jobben starter og tar også med lesingen av filen og ett nytt forsøk ved `format`, så ventetiden i appen kan bli lengre.

| | |
|---|---|
| Runder | |
| Typisk (median) | *( s)* |
| Lengste | *( s)* |
| Mot 120 s | *(godt under, nær grensen eller over)* |

## 6. Valg og begrunnelse

### Hel PDF eller uttrukket tekst

*(Appen sender i dag PDF-en hel til modellen (`ki.les_fil`). Begrunn om det skal fortsette: kvalitet på lysbilde-PDF-en og den skannede PDF-en, som ikke har tekstlag, mot tid og pris. Bytte til uttrukket tekst endrer bare `ki.les_fil`, men er ikke gjort i denne storyen.)*

### Sonnet eller Haiku

*(Sammenlign kvalitet, andel, språk og tid hvis Haiku er kjørt med `--modell claude-haiku-5-5`. Raskere må ikke gå på bekostning av kvaliteten. Bytte gjøres med `KI_MODELL`.)*

## 7. Konklusjon

| | |
|---|---|
| `effort` | *(beholdes som `medium`, eller ny verdi med begrunnelse)* |
| `MAKS_TOKENS` | *(beholdes, eller ny verdi hvis svar ble kuttet av)* |
| Modell | *(standardmodellen som beholdes eller velges)* |
| PRD-endring | *(ingen, eller forslag hvis 120 s ikke holder)* |
| Ny `PROMPT_VERSJON` og mock-svar | *(ja eller nei)* |
