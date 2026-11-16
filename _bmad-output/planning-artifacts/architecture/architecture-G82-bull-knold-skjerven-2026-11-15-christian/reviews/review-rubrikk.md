---
type: architecture-review
target: ../ARCHITECTURE-SPINE.md
rubric: good-spine checklist
reviewer: uavhengig arkitektur-reviewer (Claude)
date: '2026-11-15'
---

# Review av arkitektur-spine – FåreQuiz v1

## Verdict

Spinen er fokusert, og domene-AD-ene (AD-1 til AD-8) er sterke og håndhevbare. Den bør likevel gjennom én revisjonsrunde før epics. Drift og miljø er nesten helt stille: oppstart fra en ny klone, SQLite-samtidighet under lange KI-kall, migrasjoner med tre utviklere og verktøy/CI er ikke bestemt. To kontrakter på tvers av grenser er åpne eller utsatt feil: formatet på `QuizUtkast`/mock-JSON og hvilke spørsmål en økt består av. Et viktig vedtak fra memloggen falt også ut under destilleringen: at originalfiler aldri serveres.

## Sammendrag per sjekkpunkt

| Sjekkpunkt | Vurdering |
| --- | --- |
| Låser de reelle divergenspunktene | Delvis. Domenereglene er godt dekket. Mangler: øktens spørsmålssett og lagringsformat, `QuizUtkast`-kontrakten, innholdet mellom genereringsstegene, ID-er i POST-data, at media aldri serveres, e-postnormalisering, oppstart uten `.env`. |
| Hver Rule er håndhevbar og hindrer divergensen | Stort sett. Svake punkter: AD-8 (innloggingskrav uten mekanisme), AD-9 (låsen og idempotens), AD-14 («i én operasjon» lar seg ikke gjennomføre med filer), AD-15 (sier ikke hva som skjer med `username`). |
| Ingenting under «Utsatt» kan gi divergens | Nei. «Prompttekst og JSON-skjema i detalj» og «PDF mot tekst» kan begge gi divergens (se H4 og M9). |
| Navngitt teknologi er verifisert gjeldende | Delvis. Gulvet `anthropic ≥ 0.38` passer ikke med `output_config.format`. Python 3.12 får bare sikkerhetsfikser. Eksakt modell-ID og htmx-leveranse mangler. |
| Alle dimensjoner er bestemt, utsatt eller åpne | Nei. Drift/miljø (bootstrap, settings-standarder, SQLite-konfig, migrasjoner, CI/lint, linjeskift på tvers av OS) er stille. Hosting er riktig nok utsatt, men lokal drift er en dimensjon i seg selv. |
| Kort, beslutninger, ikke begrunnelser | Stort sett. Noe UX-detalj, PRD-omfang og begrunnelse kan fjernes (se seksjonen «Overflødig innhold»). |

---

## Funn

Alvorlighet: **kritisk** = blokkerer bygging eller gir garantert feil, **høy** = sannsynlig divergens med kostbar opprydding eller brudd på et hovedmål, **middels** = reell divergens som er billig å rette tidlig, **lav** = presisering eller hygiene.

Ingen funn er vurdert som kritiske.

### H1 – Oppstart fra ny klone er ikke låst (drift/miljø)

- **Alvorlighet:** høy
- **Hvor:** Konsistenskonvensjoner → Konfigurasjon; Stack; Kapabilitet-tabellen (FR-29, FR-30); ingen AD
- **Problem:** SM-1 er hovedmålet: ny klone pluss README skal gi hele kjerneflyten i testmodus uten nøkkel. Spinen lister variablene i `.env`, men sier ikke hva som skjer når `.env` mangler eller er kopiert rett fra `.env.example`. Én utvikler gjør `SECRET_KEY` påkrevd (krasj ved oppstart), en annen gir den en standardverdi. Med `DEBUG=False` serverer `runserver` ikke statiske filer, så `app.css` og htmx forsvinner. `ALLOWED_HOSTS` er heller ikke bestemt. Rekkefølgen for oppstart er ikke låst (`uv sync` → `migrate` → `seed_testdata` → `runserver`), og det står ikke om seed tåler å kjøres to ganger.
- **Forslag:** Legg til en AD, for eksempel «AD-16 – Ny klone kjører uten `.env`». Rule: `settings.py` har lokale standardverdier: `DEBUG=True`, `ALLOWED_HOSTS=["localhost","127.0.0.1"]`, en fast utviklingsnøkkel for `SECRET_KEY` merket usikker, og testmodus på når nøkkelen mangler. Kommandoene er nøyaktig `uv sync` (eller `pip install -r requirements.txt`), `python manage.py migrate`, `python manage.py seed_testdata`, `python manage.py runserver`. `seed_testdata` er idempotent: den sletter og lager testbrukeren på nytt, eller hopper over hvis brukeren finnes. README gjengir akkurat disse stegene.

### H2 – SQLite-låsing under lange KI-kall er ikke regulert

- **Alvorlighet:** høy
- **Hvor:** AD-9, AD-2, Stack (SQLite)
- **Problem:** Et steg i genereringen kan holde forespørselen i opptil 120 s. Pakker én utvikler steget i `transaction.atomic`, eller slår på `ATOMIC_REQUESTS=True`, mens en annen skriver statusen før og etter kallet, kan SQLite holde skrivelåsen gjennom hele KI-kallet. Da feiler samtidig lagring av svar (AD-13) med «database is locked» etter standardtimeouten på 5 s. Det oppdages først ved brukertest (SM-6) eller hos sensor.
- **Forslag:** Legg til i AD-9 eller som konvensjon: «Ingen databasetransaksjon er åpen under et KI-kall. `ATOMIC_REQUESTS=False`. Steget oppdaterer jobbraden i korte transaksjoner før og etter kallet.» Lås SQLite-oppsettet i `settings.py`: `OPTIONS={"timeout": 20, "transaction_mode": "IMMEDIATE", "init_command": "PRAGMA journal_mode=WAL;"}` (støttet fra Django 5.1).

### H3 – Spørsmålssett, rekkefølge og svarlagring i en økt er ikke låst

- **Alvorlighet:** høy
- **Hvor:** AD-6, AD-7, AD-2
- **Problem:**
  1. For `oving` står det ikke hvilke spørsmål økten består av. Leveres et forsøk mens en øvingsøkt er påbegynt, endres feilbanken. Én utvikler leser feilbanken på nytt hver gang (spørsmål dukker opp eller forsvinner midt i økten, og «alle besvart» i FR-17 flytter seg), en annen fryser settet.
  2. AD-7 sier at rekkefølgen «lagres på `Okt`», men ikke i hvilket format (JSONField, egen tabell, bare alternativer eller også spørsmål).
  3. «Brukeren kan endre et svar» (FR-17) uten unik `(okt, sporsmal)` gir enten nye `Svar`-rader per endring eller oppdatering av den gamle. Det påvirker AD-2 (hvilket svar telles) og AD-4.
- **Forslag:** Utvid AD-7: «`Okt.rekkefolge` er en JSONField: en liste med `{"sporsmal": id, "alternativer": [id, id, id]}`. Den bestemmer både hvilke spørsmål økten har og i hvilken rekkefølge. For `oving` er den et øyeblikksbilde av åpne `Feilbankrad` for notatet da økten ble opprettet. `Svar` har `UniqueConstraint(okt, sporsmal)`, og endring av svar oppdaterer raden.»

### H4 – `QuizUtkast` og mock-JSON er en grensekontrakt, men står som utsatt

- **Alvorlighet:** høy
- **Hvor:** AD-11, AD-12, Utsatt («Prompttekst og JSON-skjema i detalj»)
- **Problem:** Det `sjekk` returnerer, krysser grensen `ki` → `studier/services/generering` og blir lagret som `Quiz`/`Sporsmal`/`Alternativ`. Mock-filene i `ki/mock/` lages av én person og må ha nøyaktig samme form som det modellen svarer, siden `sjekk` kjører på begge. Utsettes skjemaet, finner den som skriver mock-filene, den som skriver lagringstjenesten og den som skriver `sjekk` hver sin form. NFR-8 (3.1.2) krever i tillegg at spørsmål merkes med notatets språk når det ikke er norsk. Det trenger et språkfelt i utkastet og på `Quiz`, og det felter står ingen steder.
- **Forslag:** Lås formen i AD-11 (prompttekst og formuleringer kan fortsatt utsettes): `QuizUtkast = {sprak: str (BCP 47, f.eks. "nb", "en"), sporsmal: [{tekst: str, alternativer: [{tekst: str, er_riktig: bool}] × 3}]}`. Mock-filene har samme JSON-form som det rå modellsvaret. `Quiz` får feltet `sprak`. Skriv om utsatt-punktet til «Prompttekst utsettes. Skjemaets felter er låst i AD-11.»

### H5 – At originalfiler aldri serveres, falt ut av spinen

- **Alvorlighet:** høy
- **Hvor:** Strukturfrø (`media/`), AD-8; memlog-linje 28 («originalfiler serveres aldri»)
- **Problem:** Vedtaket står i memloggen, men ikke i spinen. Legger en utvikler til `static(settings.MEDIA_URL, document_root=MEDIA_ROOT)` i `urls.py` for å forhåndsvise filer, blir alle opplastede notater tilgjengelige uten eiersjekk. Stiene er riktignok UUID-er, men AD-8 sier at beskyttelsen ikke skal hvile på ID-er som ikke kan gjettes. Ikke-mål i PRD-en: «Ingenting kan lastes ned fra appen.»
- **Forslag:** Legg til i AD-8 eller AD-14: «Ingen URL serverer `media/`. `MEDIA_URL` rutes ikke, og filer leses bare av `ki.les_fil` og slettes bare av `slett_emne`.»

### M1 – Innloggingskravet har ingen mekanisme

- **Alvorlighet:** middels
- **Hvor:** AD-8 (siste setning), NFR-2
- **Problem:** «Alle views unntatt innlogging og registrering krever innlogging» kan løses med en dekoratør på hvert view (lett å glemme ett) eller globalt. Regelen er ikke mekanisk håndhevbar slik den står.
- **Forslag:** Rule: `django.contrib.auth.middleware.LoginRequiredMiddleware` står i `MIDDLEWARE`. Bare innlogging og registrering har `@login_not_required`. Ingen views bruker `@login_required` (det er overflødig). Dette er støttet siden Django 5.1, altså også i 5.2.

### M2 – ID-er fra skjemadata dekkes ikke av eierkontrollen

- **Alvorlighet:** middels
- **Hvor:** AD-8, AD-7
- **Problem:** AD-8 gjelder oppslag på pk i views (URL). Når svaret lagres, kommer `alternativ`-ID-en fra POST-data. Det står ikke at alternativet må høre til et spørsmål i økten. Én utvikler validerer det, en annen lagrer hvilken som helst `Alternativ`-ID. Da kan man koble svar til andres data, og poengsummen kan manipuleres. Det samme gjelder `ModelChoiceField`-querysets (for eksempel valg av emne ved opplasting).
- **Forslag:** Utvid AD-8: «Alle ID-er fra forespørselen (URL, POST, GET) løses gjennom `tilgang.py` eller valideres mot et objekt som allerede er hentet med den. Querysets i skjemaer bygges med `egne(...)`.» I AD-7: «Svartjenesten avviser et alternativ som ikke står i `Okt.rekkefolge` for spørsmålet.»

### M3 – `Okt` med to mulige foreldre gir uklar eiersti og svake constraints

- **Alvorlighet:** middels
- **Hvor:** AD-6, AD-8
- **Problem:** `forsok` peker på `Quiz`, og `oving` peker på `Notat`. Da har `Okt` to eierstier (`quiz__notat__emne__eier` og `notat__emne__eier`), mens AD-8 forutsetter én sti per modell i `tilgang.py`. Det står ikke om feltene er nullable, eller hvilken `CheckConstraint` som sikrer at riktig felt er satt for hver type. «Per notat og bruker» er også overflødig, siden notatet bare har én eier.
- **Forslag:** «`Okt` har alltid `notat` (FK, ikke null) og `quiz` (FK, null for `oving`). `CheckConstraint`: `type=forsok` ⇔ `quiz IS NOT NULL`. Eierstien er `notat__emne__eier`. Historikken (FR-26) spørres per notat.» Stryk «og bruker».

### M4 – Genereringskjeden: tilstand mellom steg, idempotens og lås

- **Alvorlighet:** middels
- **Hvor:** AD-9
- **Problem:**
  1. `les_fil` kjøres i steget `leser`, men resultatet trengs i `lager`, som er en egen forespørsel. Jobbraden har ikke noe felt for det. Én utvikler leser filen på nytt i `lager`, en annen lagrer teksten på jobben (base64 for PDF?).
  2. Det står ikke hva som skjer når steg-endepunktet kalles to ganger for samme status, for eksempel ved oppdatering av siden eller et HTMX-nytt forsøk. Da kan to KI-kall gå samtidig.
  3. «Høyst én aktiv jobb» avhenger av tid og kan ikke være en DB-constraint. Det står ikke hvordan låsen sjekkes uten race ved dobbeltklikk.
  4. Memloggen har statusen `venter`, mens spinen starter i `leser`.
- **Forslag:** Legg til i AD-9: «`leser` validerer bare filen. `generer` kaller `les_fil` på nytt (filinnhold lagres ikke i databasen). Steget går fra status X til Y med `UPDATE ... WHERE status=X`. Påvirkes 0 rader, returneres bare gjeldende fragment uten nytt KI-kall. Opprettelsen av jobben sjekker etter aktiv jobb og oppretter ny i samme `transaction.atomic` (IMMEDIATE, jf. H2). Første status er `leser`.» Oppdater memloggen tilsvarende.

### M5 – HTMX-oppsett: CSRF og leveranse av biblioteket

- **Alvorlighet:** middels
- **Hvor:** Stack (htmx 2.x), AD-9, AD-13, NFR-4
- **Problem:** Steg-endepunktet og HTMX-forbedringene på AD-13 bruker POST. Ingenting sier hvordan CSRF-tokenet sendes. Én utvikler bruker `hx-headers` på `<body>`, en annen `@csrf_exempt`. Det står heller ikke om htmx lastes fra CDN eller ligger i repoet. Lastes det fra CDN, kreves en ekstern tjeneste (i strid med NFR-4 og frakoblet bruk), og versjonen kan drive.
- **Forslag:** Konvensjon: «`static/js/htmx.min.js` (eksakt 2.0.x-versjon) ligger i repoet. Ingen CDN. `base.html` setter `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'` på `<body>`. `csrf_exempt` er forbudt.» Lås at steg-endepunktet er POST.

### M6 – Testdokumentenes SHA-256 påvirkes av linjeskift i git, og hash-tabellen er ikke plassert

- **Alvorlighet:** middels
- **Hvor:** AD-12, Strukturfrø (`testdokumenter/`)
- **Problem:** Tre utviklere på Windows med `core.autocrlf=true` sjekker ut TXT-testdokumentet med CRLF, mens sensor på macOS/Linux får LF. Da blir SHA-256 ulik, filen behandles som ukjent, og appen viser «forhåndslagret» for et ekte testdokument. Det står heller ikke hvor koblingen hash → dokument ligger (hardkodet ordbok eller manifestfil), hvilket dokument som er standard, eller hvordan `TESTMODUS` tolkes (`1`/`true`/`on`).
- **Forslag:** Legg `.gitattributes` med `testdokumenter/** binary` og `ki/mock/** -text` i Strukturfrø. AD-12: «Koblingen står i `ki/mock/manifest.json` (`{sha256: dokumentnavn}`, `standard: <navn>`). `TESTMODUS` er sann for `1`, `true`, `yes` eller `on` (uavhengig av store og små bokstaver). Test-settings tvinger testmodus på.»

### M7 – AD-15 sier ikke hva som skjer med `username`, eller om e-post normaliseres

- **Alvorlighet:** middels
- **Hvor:** AD-15, FR-1, FR-2
- **Problem:** `AbstractUser` har et påkrevd og unikt `username`. Med e-post som `USERNAME_FIELD` må det enten fjernes (`username = None` og egen manager) eller fylles med en kopi av e-posten. To utviklere velger ulikt, og det låses i første migrering. Det står heller ikke om `Ola@X.no` og `ola@x.no` er samme konto. FR-1 krever avvisning av duplikater, og FR-2 krever innlogging uavhengig av skrivemåte.
- **Forslag:** Rule: «`username = None`, `email = EmailField(unique=True)`, `REQUIRED_FIELDS = []`, egen `BrukerManager`. E-post lagres med små bokstaver (normaliseres i manageren og i registrerings- og innloggingsskjemaet).» Lås også `AUTH_PASSWORD_VALIDATORS` til bare `MinimumLengthValidator(8)`, slik at reglene samsvarer med FR-1 (Djangos standardvalidatorer avviser flere passord enn FR-1 sier).

### M8 – Gulvet for Anthropic-SDK-en passer ikke med structured outputs, og modell-ID er ikke låst

- **Alvorlighet:** middels
- **Hvor:** Stack (`anthropic ≥ 0.38`), AD-11, Konfigurasjon (`KI_MODELL`)
- **Problem:** 0.38 er gulvet for PDF-støtte. `output_config.format` (structured outputs, GA) kom mye senere. Tredjepartskilder peker på rundt 0.74 for `parse()`/structured outputs, og det finnes upålitelige meldinger om en 1.0 med brytende endringer i 2026. Med pip-veien (`requirements.txt`) kan en utvikler eller sensor få en versjon der parameteren ikke finnes. I tillegg står den eksakte API-ID-en for standardmodellen (Sonnet 5.5) ingen steder, så `.env.example` og standardverdien i `settings.py` kan få hver sin streng.
- **Forslag:** Endre til «anthropic: eksakt versjon låst i `uv.lock` og `requirements.txt`, minst den første versjonen med `output_config` (sjekk i SDK-ens changelog)». Lås `KI_MODELL` sin standardverdi som en eksakt modell-ID i spinen og i `.env.example`, sjekket mot modellisten i Anthropic-dokumentasjonen.

### M9 – «PDF mot tekst» står både som låst og som utsatt

- **Alvorlighet:** middels
- **Hvor:** AD-11 («PDF sendes hel som dokument»), Utsatt («Valg mellom Sonnet og Haiku og PDF mot tekst»)
- **Problem:** Det ene stedet sier at det er låst, det andre at det er åpent. En utvikler kan bygge tekstuttrekk for PDF «for å teste». Det påvirker FR-9 (skannede PDF-er) og hva `les_fil` returnerer.
- **Forslag:** Utsatt-punktet skal si: «v1 sender PDF hel (AD-11). Viser testfasen at tekst er bedre, endres bare `ki.les_fil`, og `PROMPT_VERSJON` økes.» Da er punktet et bevisst bytte-punkt og ikke et åpent valg.

### M10 – Migrasjoner og parallelt arbeid er stille

- **Alvorlighet:** middels
- **Hvor:** Strukturfrø (`studier/models.py` med ni modeller); memlog-linje 18
- **Problem:** Memloggen sier at modellene i `studier` lages først i én story. Spinen sier det ikke. Tre utviklere som legger til felt parallelt i samme app får kolliderende `0002_*`-migreringer. Det står heller ikke at migreringer committes.
- **Forslag:** Konvensjon: «Alle modeller i AD-6, AD-7, AD-9 og AD-15 lages i den første storyen. Migreringer committes. Ved konflikt slettes egen, ikke-merget migrering og lages på nytt etter rebase (ingen `--merge` på `main`).»

### M11 – AD-14: «i én operasjon» er ikke mulig for filer

- **Alvorlighet:** middels
- **Hvor:** AD-14
- **Problem:** Filsletting er ikke transaksjonell. Slettes filene først og databasesletten så feiler, peker notater i databasen på filer som ikke finnes. Regelen sier «i én operasjon», og det lar seg ikke gjøre.
- **Forslag:** «`slett_emne` samler filstiene, sletter emnet i `transaction.atomic`, og sletter filene i `transaction.on_commit`. En manglende fil ignoreres.»

### L1 – Python 3.12 og versjonsvalg med uv

- **Alvorlighet:** lav
- **Hvor:** Stack
- **Problem:** Python 3.12 får bare sikkerhetsfikser (siden april 2025). uv kan velge nyeste Python (3.14 eller 3.15) hvis `requires-python` er åpen oppover, og Django 5.2 støtter offisielt opptil 3.14.
- **Forslag:** `.python-version` = `3.12` (eller 3.13), og `requires-python = ">=3.12,<3.15"` i `pyproject.toml`.

### L2 – Enum-verdier er ikke låst

- **Alvorlighet:** lav
- **Hvor:** AD-12 (`<vanskelighetsgrad>.json`), AD-4, FR-11
- **Problem:** Verdiene for vanskelighetsgrad brukes i filnavn, modellfelt og vekting, men står ikke i spinen.
- **Forslag:** Legg til «`vanskelighetsgrad` ∈ {`lett`, `middels`, `vanskelig`}» i AD-6 eller i konvensjonstabellen.

### L3 – `forsok_nr` kolliderer med ordlisten

- **Alvorlighet:** lav
- **Hvor:** AD-9; Konvensjoner («Ord fra PRD-ens ordliste brukes med samme betydning»)
- **Problem:** «Forsøk» betyr et forsøk på en quiz (`Okt.type=forsok`). Telleren for ny generering bryter spinens egen navneregel.
- **Forslag:** Gi den nytt navn, for eksempel `runde` (1 eller 2).

### L4 – Verktøy, CI og formatering er stille

- **Alvorlighet:** lav
- **Hvor:** Konvensjoner (Tester)
- **Problem:** Det står ikke om tester kjøres i CI eller bare lokalt, og ingen formaterer eller linter er valgt. Med tre utviklere gir det støy i diffene, og røde tester oppdages sent. Dimensjonen er stille, ikke utsatt.
- **Forslag:** Bestem enten «GitHub Actions kjører `manage.py test` på hver PR, og `ruff format` + `ruff check` er standard» eller eksplisitt «Ingen CI i v1. Tester kjøres lokalt før merge.»

### L5 – Byggingen av Tailwind og `requirements.txt` kan drive

- **Alvorlighet:** lav
- **Hvor:** Konvensjoner (CSS), Stack (uv)
- **Problem:** Inndatafil, kommando og CLI-versjon for Tailwind er ikke angitt, og ferdigbygd `app.css` gir merge-konflikter. Det står ikke hvem som eksporterer `requirements.txt` på nytt.
- **Forslag:** «Inndata: `static/src/app.css` (`@theme` med tokens fra DESIGN.md). Bygg: `tailwindcss -i static/src/app.css -o static/css/app.css --minify`. Ved konflikt i `app.css` bygges filen på nytt. `requirements.txt` eksporteres med `uv export --no-hashes -o requirements.txt` ved hver avhengighetsendring.»

### L6 – Hvor fasiten kan vises, er ikke låst

- **Alvorlighet:** lav
- **Hvor:** AD-7, FR-19, FR-23
- **Problem:** `Alternativ.er_riktig` kan lekke via maler eller HTMX-fragmenter (for eksempel som data-attributter) før spørsmålet er lært.
- **Forslag:** «Maler leser aldri `er_riktig` direkte. Fasiten vises bare via tjenestefunksjonen `kan_vise_fasit(sporsmal)` (sann når spørsmålet er lært).»

### L7 – Mindre uklarheter

- **Alvorlighet:** lav
- **Hvor:** AD-1, AD-13, Konvensjoner
- **Problem og forslag:**
  - AD-1 nevner «filer på disk», men ikke `Notat`. Det står ikke om opplasting går via tjeneste eller via `ModelForm.save()`. Forslag: legg `Notat` (opprettelse) og `Bruker.vilkar_godtatt` til i lista.
  - URL for navigering i quizen er ikke låst (`?nr=` eller `/sporsmal/<n>/`). Forslag: legg `/okter/<id>/?nr=<n>`, `/okter/<id>/svar/` og `/okter/<id>/lever/` til i URL-raden.
  - `studier/feilmeldinger.py` som eneste kilde gjør at `kontoer` må importere fra `studier`. Forslag: avgrens til generering og opplasting, eller flytt til `farequiz/feilmeldinger.py`.
  - Tegnkoding for TXT er ikke bestemt. Forslag: UTF-8, med cp1252 som reserve i `les_fil`.

---

## Overflødig innhold (hører ikke hjemme i spinen)

| Hvor | Hva | Forslag |
| --- | --- | --- |
| Utsatt: «Kuttrekkefølge» | PRD/epic-anliggende. Spinen sier selv at det ikke er arkitektur. | Fjern. |
| Utsatt: «Glemt passord, endre passord, slette konto» | PRD-omfang (kap. 7.2), ikke en arkitekturbeslutning som er utsatt. | Fjern, eller la stå bare hvis AD-15 eller AD-8 må ta hensyn til det. |
| Utsatt: «Melde spørsmål som feil» | Inneholder begrunnelse («AD-3 og AD-5 gjør det mulig …»). | Kort ned til én linje, eller flytt til memloggen. |
| AD-9: «Steglinjen har `role="status"`», Konvensjoner: «med `role="alert"`» | UX- og a11y-detaljer som EXPERIENCE.md eier. | Erstatt med en henvisning til EXPERIENCE.md. |
| AD-15 Prevents: «Det er svært vanskelig å bytte etter første migrering.» | Begrunnelse. | Fjern setningen. |
| AD-3 Binds: «FR-31 (fremtidig)» | Binder et krav som ikke finnes. | Fjern fra Binds. |
| Designparadigme: tabell og mermaid-diagram | Diagrammet gjentar tabellen. Det eneste nye er `ki -.-x M` og seed → services. | Behold én av dem, helst tabellen pluss setningen om `ki`. |
| AD-11: «PDF sendes hel … DOCX og TXT sendes som uttrukket tekst» | Gjentar FR-9. | Kan stå, men da som låst vedtak (se M9). |

## Det som er bra (bør beholdes)

- AD-2, AD-3 og AD-4 låser den mest divergensutsatte logikken (feilbank, lært, dekningsgrad) på en måte som kan testes direkte, med regneeksemplene fra FR-24 og FR-25.
- AD-7 (alternativ-ID og ingen posisjon) og AD-5 (identitet per quiz) treffer nøyaktig faglærers punkt 4.2.
- AD-8 med eierstiene samlet i `tilgang.py` er mekanisk sjekkbar ved gjennomgang (grep etter `objects.get(pk=` i views).
- AD-10 og AD-12 gir faste feilkoder og én kilde for testmodus, som er riktig for SM-1 og faglærers punkt 4.3.
- Begrensningene fra addendumet er tatt inn og merket.

## Kilder brukt til teknologisjekk

- [Anthropic – Structured outputs (`output_config.format`, GA)](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [openllmetry-commit som hever anthropic-gulvet til 0.74 for structured outputs (tredjepart, indikasjon)](https://backiee.wasmer.app/https_github_com/traceloop/openllmetry/commit/c91f7c6463f9898cb78213cf803a1a5e0ae21c9a)
- [Påstand om anthropic 1.0 med brytende endringer (ikke bekreftet)](https://ecorpit.com/anthropic-python-sdk-v1-httpx2-sampling-params-removed-docs-conflict-2026/)
- [Django – LoginRequiredMiddleware / `login_not_required` (5.1+)](https://git.joshthomas.dev/mirrors/django/commit/c7fc9f20b49b5889a9a8f47de45165ac443c1a21?files=docs)
- Memlog-oppføringer datert 2026-11-15 (Django 5.2 LTS, htmx 2.x/4.0, PDF-grenser) er godtatt som de står.
