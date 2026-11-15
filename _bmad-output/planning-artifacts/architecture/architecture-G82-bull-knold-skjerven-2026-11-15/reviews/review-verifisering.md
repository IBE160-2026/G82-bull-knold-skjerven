---
review: verifisering mot nett
target: ../ARCHITECTURE-SPINE.md
memlog: ../.memlog.md
reviewer: uavhengig reviewer (Claude)
date: 2026-11-15
---

# Review – verifisering av teknologivalg mot nettet

## Verdict

Alle navngitte teknologier finnes og passer til arkitekturen, og de fleste versjonslinjene i memloggen holder. Men Stack-tabellen har én klar feil (Anthropic-SDK-en er på 2.x, ikke 0.x, og «≥ 0.38» er en farlig nedre grense). To valg bør justeres før epics: Python 3.12 og hvordan htmx 2.x lastes inn. Ingen av funnene endrer paradigmet eller noen AD.

Alvorlighetsgrad: **Høy** (bør rettes før epics), **Middels** (bør rettes eller avklares), **Lav** (presisering), **Info** (bekreftet, ingen endring).

## Hva memloggen allerede hadde sjekket

| Memlog-påstand (type version) | Resultat |
| --- | --- |
| Django 5.2 LTS, støtte til apr 2028; 6.1 nyeste; 6.2 LTS apr 2027 | Bekreftet |
| htmx 4.0.0 28.08.2026, npm `latest` = 2.x, 2.x støttes på ubestemt tid | Bekreftet |
| anthropic Python-SDK «~0.10x»; PDF-støtte siden 0.38.0 | **Feil.** Gjeldende er 2.8.0 (se F-1) |
| PDF maks 600 sider (100 under 1M kontekst), 128 MB fra 28.10.2026 | Bekreftet (600/100 og 128 MB). Datoen 28.10 har jeg ikke sett selv |
| Structured outputs `output_config.format`, GA, ingen beta-header, `parse()` med Pydantic | Bekreftet |

Ikke sjekket før denne reviewen: Python-versjon, python-docx, python-dotenv, Tailwind v4 CLI og tokens, uv export, modell-ID-en, effort/latens og betinget constraint på SQLite.

---

## Funn

### F-1 – Anthropic-SDK-versjonen i Stack er utdatert og nedre grense er for lav

- **Alvorlighet:** Høy
- **Hva:** Stack sier `anthropic ≥ 0.38`, og memloggen sier «~0.10x». Gjeldende versjon på PyPI er **2.8.0** (10.11.2026). SDK-en har hatt to store versjoner siden: 1.0.0 (2026-08-20, httpx2 og andre «minor breaking changes») og 2.0.0 (2026-10-21, ny API-versjon `2026-10-21`). Den offisielle dokumentasjonen sier: «In the Python SDK (v1.0 and later), a schema dictionary passed as `output_format={...}` raises a `TypeError`. Use `output_config` instead.» Det gamle `output_format` krever nå beta-headeren `structured-outputs-2025-11-13`, ellers gir API-et 400. Med «≥ 0.38» kan en utvikler som har en gammel SDK installert, havne på en versjon uten `output_config`, og da kan ikke AD-11 implementeres slik den står. Kodeeksempler fra treningsdata eller eldre blogger (beta-namespace, `output_format`) vil også feile.
- **Kilder:**
  - https://pypi.org/project/anthropic/ (2.8.0, 10.11.2026; Python ≥ 3.10)
  - https://raw.githubusercontent.com/anthropics/anthropic-sdk-python/main/CHANGELOG.md (1.0.0 og 2.0.0)
  - https://platform.claude.com/docs/en/build-with-claude/structured-outputs (avsnittet «Migrating from the beta»)
- **Forslag:** Stack: `anthropic | ≥ 2.8, < 3 (låst i uv.lock)`. Rett memlog-linjen. I `ki`: bruk `client.messages.parse(..., output_format=<Pydantic-modell>)` eller `client.messages.create(..., output_config={"format": {"type": "json_schema", "schema": ...}})`. Ikke bruk `client.beta.*` og ikke beta-header.

### F-2 – Python 3.12 er i sikkerhetsfase og har ikke lenger Windows-/macOS-installasjonsprogram

- **Alvorlighet:** Middels
- **Hva:** Django 5.2 støtter Python 3.10–3.14 (3.14 fra 5.2.8, 05.11.2025), så 3.12 *virker*. Men 3.12 har vært i «security»-fasen siden april 2025 (EOL 2028-10). Python.org lager bare kildekode-utgivelser for den, og 3.12.10 var siste versjon med binære installasjonsprogram. En student på Windows som laster ned «Python 3.12» fra python.org, får altså 3.12.10 uten sikkerhetsrettingene fra 3.12.11–3.12.16. 3.13 gikk også over i sikkerhetsfasen i oktober 2026. 3.14 er den eldste versjonen som fortsatt får feilrettinger og installasjonsprogram, og den støttes av Django 5.2.8+, anthropic (≥ 3.10), python-dotenv (≥ 3.10) og python-docx (≥ 3.9).
- **Kilder:**
  - https://docs.djangoproject.com/en/5.2/faq/install/ («5.2 | 3.10, 3.11, 3.12, 3.13, 3.14 (added in 5.2.8)»)
  - https://docs.djangoproject.com/en/5.2/releases/5.2.8/
  - https://devguide.python.org/versions/ (3.14 bugfix, 3.13/3.12 security, 3.10 EOL 2026-10-01)
  - https://www.python.org/downloads/release/python-31216/ (ingen installasjonsprogram)
- **Forslag:** Velg **Python 3.14** (eventuelt 3.13). Sett `requires-python = ">=3.14,<3.15"` i `pyproject.toml` og skriv `.python-version` slik at `uv` henter riktig tolk. Hvis gruppa vil beholde 3.12, bør README si at Python installeres med `uv python install 3.12`, ikke fra python.org. Kjør `uv sync` på alle tre maskiner tidlig for å sjekke at det finnes ferdigbygde pakker (lxml for python-docx, pydantic-core for anthropic).

### F-3 – htmx 2.x er riktig, men en uversjonert CDN-URL vil gi htmx 4 i 2027

- **Alvorlighet:** Middels
- **Hva:** Valget av 2.x er riktig. npm har `latest` = **2.0.11** og `next` = **4.0.1** (begge 01.11.2026). htmx-teamet skriver at «htmx 2 will continue to be supported indefinitely», og at 4.x blir `latest` en gang i (tidlig) 2027. Da får alle som bruker en uversjonert URL (`unpkg.com/htmx.org`, `cdn.jsdelivr.net/npm/htmx.org`) plutselig 4.x. Den har endrede hendelsesnavn (`htmx:afterSwap` → `htmx:after:swap`), eksplisitt arv og fetch-basert motor. Sensor kan kjøre appen etter at taggen er flyttet. Genereringskjeden i AD-9 er nettopp den delen som avhenger av htmx-oppførsel. Spinen sier ikke hvordan htmx lastes.
- **Kilder:**
  - https://registry.npmjs.org/htmx.org (`"dist-tags":{"next":"4.0.1","latest":"2.0.11"}`)
  - https://github.com/bigskysoftware/htmx/releases
  - https://htmx.org/ (forsiden laster 2.0.11; 4.x blir `latest` «at some point in 2027»)
  - https://four.htmx.org/announcements/2026-08-28-htmx-4.0.0-is-released
  - https://four.htmx.org/migration-guide-htmx-2
- **Forslag:** Stack: `htmx | 2.0.11 (lokal fil i static/)`. Legg `htmx.min.js` 2.0.11 i `static/js/` og commit den. Det passer også med at appen bare kjøres lokalt (NFR-4) og virker uten nett når testmodus er på. Bruk aldri en uversjonert CDN-URL.

### F-4 – Sonnet 5.5 tenker som standard på «high» effort, og det er ikke tatt hensyn til i 120-sekundersfristen

- **Alvorlighet:** Middels
- **Hva:** Modell-ID-en `claude-sonnet-5-5` finnes og støtter både PDF og structured outputs (se F-8). Men Sonnet 5.5 har adaptiv tenkning, og standard effort på API-et er `high`. Tenkning kan ikke slås av med `thinking: {"type": "disabled"}` (gir 400). Riktig bryter er `thinking: {"type": "between_tools"}`, eller lavere `output_config.effort`. Tenkning teller mot `max_tokens`. Dokumentasjonen anbefaler `medium` eller `low` for latensfølsomt arbeid. I tillegg gir første forespørsel med et nytt JSON-skjema ekstra ventetid mens grammatikken kompileres, og skjemaet caches i 24 timer etter siste bruk. AD-9 (120 s for hele jobben, ett nytt forsøk ved formatfeil) forutsetter at ett kall er godt under 60 s. Det er ikke verifisert. Dette er ikke en feil i spinen, men en uverifisert forutsetning for AD-9 og AD-11.
- **Kilder:**
  - https://platform.claude.com/docs/en/build-with-claude/effort (avsnittet om Sonnet 5.5)
  - https://platform.claude.com/docs/en/about-claude/models/overview
  - https://platform.claude.com/docs/en/build-with-claude/structured-outputs (grammatikk-cache, 24 t)
- **Forslag:** I `ki`: sett `output_config.effort` eksplisitt (start med `medium`, og mål `low`), og sett `max_tokens` med rom for tenkning. Effort kan gjerne ligge i `.env` ved siden av `KI_MODELL`, eller som konstant i `ki` som inngår i `PROMPT_VERSJON`. Mål tiden for ett kall med det største testdokumentet og 30 spørsmål i testfasen (spinen har allerede «Valg mellom Sonnet og Haiku … avgjøres i testfasen»). `claude-haiku-5-5` finnes som raskere alternativ.

### F-5 – Structured outputs + PDF fungerer, men to funksjoner må ikke brukes

- **Alvorlighet:** Lav
- **Hva:** PDF som `document`-blokk (base64) og `output_config.format` kan brukes i samme forespørsel. Både PDF-støtte og structured outputs er «stable» for `claude-sonnet-5-5` og `claude-haiku-5-5`, og dokumentinnhold står ikke på lista over inkompatible funksjoner. To ting **er** inkompatible: **citations** (gir 400 sammen med `output_config.format`) og **prefill** av assistentsvaret. Det bekrefter også at egen `sjekk()` er nødvendig. Skjemaet støtter ikke `minLength`/`maxLength`, `minimum`/`maximum` eller `minItems` over 1, og enum-verdier kan komme tilbake med annen store/små bokstav. Antall spørsmål og «nøyaktig ett riktig alternativ» kan altså ikke håndheves av skjemaet alene. Det stemmer med AD-11.
- **Kilder:**
  - https://platform.claude.com/docs/en/build-with-claude/structured-outputs («Feature compatibility», «JSON Schema limitations», «Invalid outputs»)
  - https://platform.claude.com/docs/en/build-with-claude/pdf-support
- **Forslag:** Skriv to setninger i `ki`-modulen eller i story-teksten: «Ikke slå på `citations` på dokumentblokken, og ikke bruk prefill.» Håndter også `stop_reason` = `refusal` og `max_tokens` som `format`-feil (AD-10), siden svaret da kan bryte med skjemaet.

### F-6 – Tailwind v4: formuleringen om tokens bør presiseres, og CLI-versjonen bør låses

- **Alvorlighet:** Lav
- **Hva:** Gjeldende versjon er **v4.3.5** (06.11.2026). Den frittstående CLI-en finnes fortsatt som kjørbar fil per plattform under GitHub Releases, og den offisielle installasjonssiden peker på den for bruk uten Node. v4 er CSS-først: tokens skrives som CSS-variabler i en `@theme { ... }`-blokk (for eksempel `--color-*` og `--font-*`) i inndata-CSS-en, etter `@import "tailwindcss";`. `tailwind.config.js` og `init` er ikke standard lenger. Spinens «Tokens fra DESIGN.md i Tailwinds CSS-konfigurasjon» er altså riktig for v4, men uklar. En utvikler med v3-erfaring kan lage `tailwind.config.js`. v4 finner klasser automatisk og hopper over filer i `.gitignore`. Kilden er ikke nevnt i Strukturfrø. v4.3.5 retter også en manglende kodesignatur på macOS-binærene (de ble stoppet ved oppstart før). Fordi «latest»-nedlastingen endrer seg, kan to gruppemedlemmer bygge ulik `app.css`. Filnavnene på binærene (`tailwindcss-windows-x64.exe`, `tailwindcss-macos-arm64`, `tailwindcss-linux-x64`) kunne jeg ikke lese fra asset-lista. De er bare bekreftet gjennom v3-bloggen, så de er **ikke bekreftet for v4.3.5**.
- **Kilder:**
  - https://github.com/tailwindlabs/tailwindcss/releases (v4.3.5, kodesignatur på macOS)
  - https://tailwindcss.com/docs/installation/tailwind-cli (lenke til standalone executable)
  - https://tailwindcss.com/docs/theme (`@theme`)
  - https://tailwindcss.com/docs/detecting-classes-in-source-files (`@source`, `.gitignore`)
  - https://tailwindcss.com/blog/standalone-cli (v3-tiden, filnavn)
- **Forslag:** Stack: `Tailwind CSS (frittstående CLI) | 4.3.5 (låst; ≥ 4.3.5 på macOS)`. CSS-konvensjonen: «Tokens fra DESIGN.md som `@theme`-variabler i `static/css/input.css` (ingen `tailwind.config.js`). Bygg: `tailwindcss -i static/css/input.css -o static/css/app.css --minify`.» Legg til `static/css/input.css` i Strukturfrø, og eventuelt `@source "../../templates";` for å være eksplisitt. README bør lenke til den eksakte release-taggen, ikke `latest`.

### F-7 – python-docx er stabil, men har ikke hatt aktivitet på 17 måneder

- **Alvorlighet:** Lav
- **Hva:** Siste versjon er **1.2.0** (16.06.2025, Python ≥ 3.9). De siste commitene på `master` er fra samme dag, og det er mange åpne issues og PR-er (387/166). Prosjektet er ikke arkivert og er fortsatt standardvalget for å lese tekst fra DOCX. Bruken i FåreQuiz (bare uttrekk av tekst fra avsnitt og tabeller) er enkel og lite utsatt. Lav aktivitet betyr likevel at nye Python-versjoner avhenger av at lxml har ferdigbygde pakker.
- **Kilder:**
  - https://pypi.org/project/python-docx/
  - https://github.com/python-openxml/python-docx/commits/master
- **Forslag:** Stack: `python-docx | 1.2.0 (låst i uv.lock)`. Ingen endring i arkitekturen, siden `ki.les_fil` allerede isolerer avhengigheten.

### F-8 – Modell-ID `claude-sonnet-5-5` er bekreftet

- **Alvorlighet:** Info
- **Hva:** «Claude Sonnet 5.5» finnes med API-ID og alias `claude-sonnet-5-5`, 1M kontekst, 128K maks output, $2/$10 per MTok og pensjonering «not sooner than September 28, 2027». Det er etter emneslutt. `claude-haiku-5-5` finnes også (fra $0.10/$0.50 per MTok, pensjonering tidligst 07.10.2027). Begge står på lista over modeller som støtter PDF og structured outputs.
- **Kilder:**
  - https://platform.claude.com/docs/en/about-claude/models/overview
  - https://platform.claude.com/docs/en/build-with-claude/pdf-support (supportedModels)
- **Forslag:** `.env.example`: `KI_MODELL=claude-sonnet-5-5`. Ingen endring i spinen.

### F-9 – PDF-grensene er bekreftet

- **Alvorlighet:** Info
- **Hva:** Maks 128 MB per forespørsel på første-parts API og maks 600 sider (100 når konteksten er under 1M; Sonnet 5.5 og Haiku 5.5 har 1M). Begge grensene gjelder hele forespørselen. Base64 gjør filen omtrent 33 % større. Hver side blir et bilde pluss tekst, typisk 1 500–3 000 teksttokens per side i tillegg til bildetokens. Krypterte eller passordbeskyttede PDF-er støttes ikke. Tette PDF-er kan fylle konteksten før sidegrensen nås.
- **Kilde:** https://platform.claude.com/docs/en/build-with-claude/pdf-support
- **Forslag:** Ingen endring i spinen. La `ki.les_fil` eller opplastingsvalideringen (FR-8) avvise krypterte PDF-er og filer over gruppas egen grense, og la det gi feilkoden `api_feil` eller `for_lite_innhold` etter det PRD-en sier. Grensen i PRD-en bør ligge godt under 128 MB / 1,33.

### F-10 – Django 5.2 LTS og betinget `UniqueConstraint` på SQLite er bekreftet

- **Alvorlighet:** Info
- **Hva:** Siste utgivelse i 5.2-serien er **5.2.19**. Hovedstøtten sluttet 03.12.2025, og utvidet støtte (sikkerhet) varer til april 2028. Det er nok for prosjektet. `UniqueConstraint(condition=Q(...))` har samme begrensninger som `Index.condition`. Partielle indekser støttes på PostgreSQL og SQLite, mens MySQL/MariaDB ignorerer dem. SQLite har hatt UNIQUE partielle indekser siden 3.8.0 (2013). WHERE-uttrykket kan ikke ha underspørringer, referanser til andre tabeller, ikke-deterministiske funksjoner eller bundne parametere. AD-6 kan altså uttrykkes som
  `UniqueConstraint(fields=["quiz"], condition=Q(type="forsok", status="pabegynt"), name=...)` og
  `UniqueConstraint(fields=["notat"], condition=Q(type="oving", status="pabegynt"), name=...)`.
- **Kilder:**
  - https://www.djangoproject.com/download/
  - https://docs.djangoproject.com/en/5.2/ref/models/constraints/
  - https://docs.djangoproject.com/en/5.2/ref/models/indexes/
  - https://www.sqlite.org/partialindex.html
- **Forslag:** Stack: `Django | 5.2 LTS (≥ 5.2.19, < 6.0)`. Én presisering i AD-6 (Lav): «per notat og bruker» kan ikke uttrykkes med en constraint som går gjennom `notat__emne__eier`, fordi en partiell indeks ikke kan referere til andre tabeller. Siden et notat bare har én eier, betyr «per notat» det samme. Skriv «høyst én påbegynt `oving` per notat», eller legg et eget `bruker`-felt på `Okt` hvis gruppa vil ha det eksplisitt.

### F-11 – python-dotenv er aktivt vedlikeholdt

- **Alvorlighet:** Info
- **Hva:** Siste versjon er **1.2.4** (01.10.2026, Python ≥ 3.10). Det har vært jevnlige utgivelser i 2026.
- **Kilde:** https://pypi.org/project/python-dotenv/
- **Forslag:** Stack: `python-dotenv | 1.2.x (låst i uv.lock)`.

### F-12 – uv og `uv export` til requirements.txt er bekreftet, men begge filene kan komme ut av takt

- **Alvorlighet:** Lav
- **Hva:** uv **0.13.8** (12.11.2026). Kommandoen er `uv export --format requirements.txt --output-file requirements.txt`. Formatene er `requirements.txt`, `pylock.toml` og `cyclonedx1.5`. Eksporten tar med hasher som standard (pip går da i hash-sjekkmodus, noe som virker). `--no-dev` og `--no-hashes` finnes, men det er bare bekreftet gjennom tredjepartskilder. Jeg fikk ikke lest den offisielle CLI-referansen for akkurat disse flaggene. uv-dokumentasjonen fraråder å ha både `uv.lock` og `requirements.txt`, fordi de kan komme ut av takt. Spinen velger det likevel bevisst for pip-veien i README, noe som er rimelig for sensor.
- **Kilder:**
  - https://pypi.org/project/uv/
  - https://docs.astral.sh/uv/concepts/projects/export/
  - https://pydevtools.com/handbook/how-to/how-to-export-requirements-txt-from-a-uv-project/ (tredjepart, flagg)
- **Forslag:** Stack: `uv | ≥ 0.13 (pyproject + uv.lock, eksportert requirements.txt)`. Konvensjon: «Etter hver endring i avhengigheter: `uv lock` og deretter `uv export --format requirements.txt --no-dev -o requirements.txt`, i samme commit.» Gjerne som pre-commit-hook (uv har en offisiell `uv-export`-hook).

---

## Anbefalt Stack-tabell

| Navn | Versjon |
| --- | --- |
| Python | 3.14 (alternativt 3.13; ikke 3.12 fra python.org) |
| Django | 5.2 LTS (≥ 5.2.19, < 6.0) |
| htmx | 2.0.11, lokal fil i `static/js/` |
| anthropic (Python-SDK) | ≥ 2.8, < 3, låst i `uv.lock` |
| python-docx | 1.2.0, låst i `uv.lock` |
| python-dotenv | 1.2.x (1.2.4), låst i `uv.lock` |
| Tailwind CSS (frittstående CLI) | 4.3.5 (låst) |
| SQLite | følger med Python |
| uv | ≥ 0.13; pyproject + `uv.lock`, eksportert `requirements.txt` |
| Modell (`KI_MODELL`) | `claude-sonnet-5-5` (alternativ `claude-haiku-5-5`) |

## Ikke bekreftet

- Hvilken anthropic-SDK-versjon som først hadde `output_config` uten beta. Changelog-en jeg fikk lest, stopper ved 0.84.0. Anbefalingen om ≥ 2.8 gjør dette uviktig.
- Filnavnene på Tailwind v4.3.5-binærene (asset-lista ble ikke lastet).
- De offisielle beskrivelsene av `uv export --no-dev` og `--no-hashes` (bare tredjepartskilder).
- Datoen 28.10.2026 for økningen fra 32 til 128 MB (memlog). Selve grensen på 128 MB er bekreftet.
- Faktisk svartid for Sonnet 5.5 med PDF og 30 spørsmål. Den må måles (F-4).
