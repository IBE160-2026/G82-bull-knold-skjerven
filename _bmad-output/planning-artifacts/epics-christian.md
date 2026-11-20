---
stepsCompleted: [1, 2, 3, 4]
author: Christian
created: 2026-11-16
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-G82-bull-knold-skjerven-2026-11-11/prd.md
  - _bmad-output/planning-artifacts/prds/prd-G82-bull-knold-skjerven-2026-11-11/addendum.md
  - _bmad-output/planning-artifacts/prds/prd-G82-bull-knold-skjerven-2026-11-11/tilbakemelding-prd.md
  - _bmad-output/planning-artifacts/architecture/architecture-G82-bull-knold-skjerven-2026-11-15-christian/ARCHITECTURE-SPINE.md
  - _bmad-output/planning-artifacts/ux-designs/ux-G82-bull-knold-skjerven-2026-11-15-christian/DESIGN.md
  - _bmad-output/planning-artifacts/ux-designs/ux-G82-bull-knold-skjerven-2026-11-15-christian/EXPERIENCE.md
---

# FåreQuiz (G82-bull-knold-skjerven) – epics og stories (Christians versjon)

## Oversikt

Christians individuelle versjon, laget med `bmad-create-epics-and-stories`. Dokumentet deler kravene i PRD-en, UX-designet (Christians versjon, 15.11) og arkitekturen (Christians versjon, AD-1 til AD-22) opp i epics og stories som kan implementeres. Ordene fra PRD-ens ordliste brukes med samme betydning. AD-numrene viser til [ARCHITECTURE-SPINE.md](architecture/architecture-G82-bull-knold-skjerven-2026-11-15-christian/ARCHITECTURE-SPINE.md).

## Kravoversikt

### Funksjonelle krav (FR)

FR-1: En besøkende kan registrere seg med e-post og passord. En e-post som allerede er registrert, og en ugyldig e-post gir feilmelding, og ingen konto lages. Passordet må ha minst 8 tegn.
FR-2: En bruker kan logge inn og ut. Feil passord og ukjent e-post gir samme melding. Etter utlogging sendes sider som krever innlogging, til innloggingssiden.
FR-3: En bruker kan bare se og endre sine egne emner, notater, quizer, forsøk og feilbanker. En annen brukers ID i URL-en gir «ikke funnet». Gjelder alle sider og alle handlinger som endrer data.
FR-4: En bruker kan opprette et emne med et navn. Navnet kan ikke være tomt og må være unikt hos brukeren.
FR-5: En bruker kan gi et emne nytt navn uten at notater, quizer og historikk påvirkes.
FR-6: En bruker kan slette et emne etter bekreftelse. Alle notater i emnet slettes med filer, quizer, forsøk, feilbanker og historikk. Andre emner påvirkes ikke. Dette er den eneste måten å slette data på i v1.
FR-7: En bruker må godta vilkårene før første opplasting. Vilkårene vises bare til de er godtatt, og sier at brukeren er ansvarlig for personopplysninger, at innholdet sendes til Anthropic, og at quizene lages av KI og kan inneholde feil. Tidspunktet lagres på brukeren.
FR-8: En bruker kan laste opp PDF, DOCX eller TXT på maks 5 MB, uansett sideantall, under et emne. For stor fil og feil format avvises med melding som oppgir grensen eller formatene. Filen lagres for nye quizer. Siden viser at innholdet sendes til en ekstern KI-tjeneste.
FR-9: PDF sendes hel til KI-modellen. Fra DOCX og TXT hentes teksten ut. Alle fem testdokumentene gir en quiz, også lysbilde-PDF-en og den skannede PDF-en.
FR-10: (Fjernet 11.11.2026. Notater slettes bare sammen med emnet.)
FR-11: Brukeren velger vanskelighetsgrad (lett, middels, vanskelig) og antall spørsmål (5–30) før generering. Standard er middels og 10.
FR-12: Appen lager en quiz med valgt antall og vanskelighetsgrad. Hvert spørsmål har tre ulike alternativer og nøyaktig ett riktig. Ingen like spørsmål. Spørsmålene er på notatets språk.
FR-13: Appen sjekker formatet fra KI-modellen (antall spørsmål, tre alternativer, ett riktig, ingen like alternativer eller spørsmål). Ved feil genereres det på nytt én gang. Feiler det igjen, får brukeren feilmelding og ingen quiz lagres.
FR-14: Brukeren ser steget («Leser filen», «Lager spørsmål», «Sjekker quizen»). «Lag quiz» er låst fra trykk til ferdig eller feilet, og ny generering for samme notat kan ikke startes imens.
FR-15: Generering som tar over 120 sekunder, avbrytes. Brukeren får «Prøv igjen», som bruker den lagrede filen og samme valg.
FR-16: En bruker kan lage flere quizer per notat. Hver quiz vises på notatsiden med vanskelighetsgrad, antall og dato. En quiz kan ikke slettes alene.
FR-17: Brukeren svarer og leverer. Levering krever at alle spørsmål er besvart, og appen viser hvilke som mangler. Svar kan endres før levering.
FR-18: Svar lagres underveis, og et påbegynt forsøk kan fortsettes senere, også fra en annen enhet. Påbegynte forsøk vises som «påbegynt» og påvirker ikke feilbank, dekningsgrad eller historikk. Høyst ett påbegynt forsøk per quiz. Å starte quizen igjen fortsetter det påbegynte.
FR-19: Etter levering ser brukeren poengsummen og om hvert svar var riktig eller galt. Fasiten vises ikke for feil svar. Forsøket lagres i historikken med dato og poengsum.
FR-20: En levert quiz kan tas på nytt som et nytt forsøk. Alle leverte forsøk vises i historikken.
FR-21: Ved levering legges hvert feilbesvarte spørsmål i notatets feilbank, høyst én gang. Feil svar på et spørsmål som alt ligger der, nullstiller telleren.
FR-22: «Øv på feil» gir spørsmålene i feilbanken med alternativene stokket på nytt for hver økt og uten fasit. Tom feilbank gir låst knapp. Alle spørsmål må besvares før levering, og svar lagres underveis. Økten vises ikke i historikken.
FR-23: Et spørsmål er lært etter to riktige svar på rad etter at det kom i feilbanken. Det tas ut av feilbanken, og fasiten vises. Nytt feilsvar nullstiller. Svar i «Øv på feil» og i nye forsøk teller begge.
FR-24: Dekningsgrad per notat = 20 % × lett + 30 % × middels + 50 % × vanskelig, der hvert nivå er andelen dekkede spørsmål. Nivå uten quiz = 0 %. Lett 100 %, middels 50 %, vanskelig uten quiz gir 35 %. Spørsmål som ikke er besvart i et levert forsøk, er ikke dekket.
FR-25: Dekningsgrad per emne = snittet av notatenes dekningsgrad. 80 % og 40 % gir 60 %. Emne uten notater viser ingen dekningsgrad. (Arkitekturen presiserer: bare notater med minst én quiz telles, AD-4.)
FR-26: Historikk per notat med alle leverte forsøk, dato, quiz og poengsum, nyeste øverst.
FR-27: I testmodus brukes mock-svar fra ekte genereringer på testdokumentene. 30 spørsmål per testdokument og nivå, og appen bruker de første N. Ukjent fil gir et standard testdokument med melding om det. Testmodus er på når flagget i `.env` er på, eller når API-nøkkel mangler.
FR-28: En testbruker med e-post og passord i README-en har et emne med notater, quizer, leverte forsøk og en feilbank.
FR-29: API-nøkkel, modellnavn og testmodus settes i `.env`. Repoet har `.env.example`. Standardmodell er Claude Sonnet 5.5. `.env` med ekte nøkkel ligger ikke i repoet.
FR-30: README-en beskriver installasjon, lokal kjøring, innlogging som testbruker og hvordan man legger inn egen nøkkel. En ny klone kjører hele kjerneflyten i testmodus uten nøkkel.
FR-31 (ny, fra TF-1, besluttet 16.11): En bruker kan melde et spørsmål som feil eller uklart. Spørsmålet tas ut av feilbanken, telles ikke i nevneren i dekningsgraden og kommer ikke med i nye økter. Meldingen lagres med tidspunkt. Krever en tilføyelse til AD-3, AD-4 og AD-16, og en oppdatering av PRD-en.

### Ikke-funksjonelle krav (NFR)

NFR-1: Mobil. Quiz, «Øv på feil», feilbank og historikk kan brukes på 360 px bredde uten vannrett rulling.
NFR-2: Sikkerhet. Passord lagres bare som hash. Alle sider unntatt innlogging og registrering krever innlogging. Eier sjekkes for hver forespørsel.
NFR-3: Personvern. Filer og data lagres bare lokalt. Innhold sendes til KI-tjenesten bare ved generering, og aldri i testmodus.
NFR-4: Lokal kjøring. Ingen betalte kontoer, ingen eksterne tjenester utenom KI-modellen og ingen database-server.
NFR-5: Alle KI-kall går gjennom én modul.
NFR-6: Grensesnittet er på norsk. Quizen lages på notatets språk.
NFR-7: Hver quiz lagrer modell og prompt-versjon.
NFR-8: WCAG 2.2 A og AA på alle sider: hele kjerneflyten med bare tastatur, synlig fokus som ikke skjules, klikkflater ≥ 24 × 24 px, svaralternativer som radioknapper med etikett, kontrast 4,5:1 (3:1 for store tekster og grensesnittelementer), riktig/galt med tekst eller ikon i tillegg til farge, innlogging som godtar innliming og passordbehandlere, feilmeldinger ved feltet som leses opp, statusmeldinger for fremdrift og resultat, `lang` på sidene og på spørsmål på andre språk, 200 % tekst og 320 px uten vannrett rulling, ingen dra-og-slipp. Hver story med grensesnitt har akseptansekriterier for universell utforming.
NFR-9: KI-merking (AI Act). Hver quiz er merket «Laget av KI» med modellnavn og at den kan inneholde feil, på notatsiden, mens den tas og i «Øv på feil». Gjelder også i testmodus. Vilkårene sier det samme.

### Tilleggskrav fra arkitekturen

**Startmal:** Arkitekturen bruker ingen startmal. Prosjektet settes opp fra bunnen med `django-admin startproject` og uv. Første story i Epic 1 må derfor sette opp prosjektskjelettet og alt som AD-ene krever fra start:

- Prosjektoppsett: Python 3.14, Django ≥ 5.2.19 < 6, uv ≥ 0.13 med `pyproject.toml`, `uv.lock` og `requirements.txt` fra `uv export --no-hashes`. Appene `farequiz`, `kontoer`, `studier` og `ki` etter strukturfrøet.
- `kontoer.Bruker` med e-post som brukernavn og `vilkar_godtatt`, og `AUTH_USER_MODEL` satt før første `migrate` (AD-15).
- Alle modeller i AD-6, AD-7, AD-9, AD-14 og AD-15 lages og migreres i første story (konvensjon for migreringer), sammen med det nullbare feltet `Sporsmal.meldt_tidspunkt` for FR-31.
- `.env`-oppsett med standardverdier, slik at en ny klone kjører uten `.env`: `DEBUG=True`, fast usikker utviklingsnøkkel, `ALLOWED_HOSTS=localhost,127.0.0.1`, testmodus på (AD-22). `.env.example` med `ANTHROPIC_API_KEY`, `KI_MODELL`, `TESTMODUS`, `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`.
- `.gitattributes` med `testdokumenter/** binary` og `ki/mock/** -text`, slik at hashene stemmer på Windows (AD-12).
- CI: `.github/workflows/test.yml` kjører `ruff check`, `ruff format --check` og `manage.py test` i testmodus på hver pull request mot `main`. Rød CI merges ikke.
- Tailwind v4 frittstående CLI: `static/src/app.css` med `@theme` bygges til `static/css/app.css`, som committes. htmx 2.0.11 som lokal fil `static/js/htmx.min.js`, aldri via CDN. Dette settes opp i story 1.3, den første storyen med grensesnitt.
- SQLite med `OPTIONS = {"transaction_mode": "IMMEDIATE", "timeout": 20}` og `ATOMIC_REQUESTS` av (AD-19). `USE_TZ=True`, `TIME_ZONE="Europe/Oslo"`.

**Lagdeling og tilgang:**

- Views → `studier.tilgang` / `studier.services` → modeller. Services → `ki`. `ki` importerer aldri fra `studier` eller `kontoer`.
- Bare `studier/services/` skriver `Notat`, `Quiz`, `Okt`, `Svar`, `Feilbankrad`, `Genereringsjobb`, filer og `Bruker.vilkar_godtatt`. `Emne` kan lagres fra skjema, med `eier` i konstruktøren og unikt navn uten å skille store og små bokstaver (AD-1).
- `hent_egen` og `egne` i `studier/tilgang.py` for alle ID-er fra URL, GET og POST. `LoginRequiredMiddleware`, med `@login_not_required` bare på innlogging og registrering. Originalfiler serveres aldri (AD-8).

**Domeneregler:**

- `registrer_svar(sporsmal, riktig) -> Hendelse` er eneste vei til `Feilbankrad`, kalles bare fra `lever_okt`, og hendelsen lagres på `Svar.hendelse` (AD-2).
- `Feilbankrad` slettes aldri. Høyst én per spørsmål. «I feilbanken» = `laert_tidspunkt IS NULL` (AD-3).
- `services.dekningsgrad` regner ut dekningsgraden og lagrer den aldri. Dekket = minst ett riktig svar i en levert økt og ingen åpen feilbankrad. Avrundes bare i malen (AD-4).
- Spørsmål har identitet per quiz. Lik tekst i to quizer er to spørsmål (AD-5).
- Én modell `Okt` for forsøk og øvingsøkt, med `type`, `status`, betinget unikhet for påbegynte økter og `start_eller_fortsett_okt` som POST (AD-6).
- `Svar` peker på `Alternativ`, aldri på posisjon. `UniqueConstraint(okt, sporsmal)` (AD-7).
- `Okt.innhold` låser spørsmål og stokket alternativrekkefølge når økten opprettes. Fortsett-lenken peker på første ubesvarte spørsmål. «Øv på feil» er bare låst når feilbanken er tom og det ikke finnes noen påbegynt øvingsøkt (AD-16).
- `lagre_svar` er eneste måte å skrive svar på, og avviser svar i leverte økter og alternativer fra feil spørsmål (AD-17).
- `lever_okt` er en betinget statusovergang i én transaksjon og tåler dobbeltklikk (AD-18).
- `er_riktig` og `begrunnelse` sendes aldri til malene for Quiz og Øv på feil. Fasit vises bare når spørsmålet er lært (AD-20).
- Sletting skjer bare via `slett_emne`, med cascade i `atomic` og filsletting i `on_commit`. Filer lagres som `notater/<eier-id>/<uuid4><endelse>` (AD-14).

**Generering og KI:**

- Stegvis HTMX-kjede med `Genereringsjobb`: `/jobber/<id>/steg/` tar jobben med en betinget oppdatering. Stegene `leser` → `lager` → `sjekker` → `ferdig`/`feilet`, med én ny runde ved formatfeil. `aktiv_jobb(notat)` er eneste definisjon av aktiv jobb, med timeout etter 120 s. `Quiz.jobb` er `OneToOneField` (AD-9).
- Faste feilkoder: `timeout`, `format`, `for_lite_innhold`, `for_stor`, `api_nokkel`, `api_feil`. Tekstene står i `farequiz/feilmeldinger.py` (AD-10).
- `ki`-kontrakten: `les_fil`, `generer` med structured outputs og eksplisitt `effort`, `sjekk` → `QuizUtkast` med `sprak`, `modell`, `prompt_versjon`, `forhandslagret` og spørsmål med `begrunnelse`. `ki.visningsnavn(quiz.modell)` i malene. `PROMPT_VERSJON` økes ved hver endring (AD-11).
- Bare `ki` vet om testmodus. Mock-svar slås opp på SHA-256 i `ki/mock/manifest.json`. `manage.py lag_mocksvar` lager mock-filene. Context processor gir malene flagget (AD-12).
- Ingen KI-kall inne i en databasetransaksjon (AD-19).

**Grensesnitt og drift:**

- Neste, Forrige og Lever er POST-skjemaer som virker uten JavaScript. HTMX bare som forbedring. Bare genereringen krever JS (AD-13).
- `manage.py seed_testdata` kjører i tvunget testmodus, bruker bare tjenestene og kan kjøres flere ganger (AD-21).
- README og kode bruker nøyaktig stegene `uv sync` (eller `pip install -r requirements.txt`), `migrate`, `seed_testdata`, `runserver` (AD-22).
- URL-er: `/emner/<id>/`, `/notater/<id>/`, `/quizer/<id>/`, `/okter/<id>/sporsmal/<nr>/`, `/okter/<id>/lever/`, `/okter/<id>/resultat/`, `/jobber/<id>/steg/`.
- POST/redirect/GET. HTMX-fragmenter i `templates/<app>/_<navn>.html`. CSRF-token i `hx-headers` på `<body>`.
- Tester: `manage.py test` med testmodus tvunget på. Regneeksemplene i FR-24 og FR-25 er testtilfeller. En test sjekker at quizsiden ikke skiller ut det riktige alternativet.
- Logging til konsollen. Feilede jobber logges med jobb-ID og feilkode, aldri med filinnhold.

### Krav fra faglærers tilbakemelding (12.11)

TF-1 (4.1, høy): Melde et spørsmål som feil eller uklart. **Besluttet 16.11:** med i v1 som FR-31, merket «kan kuttes».
TF-2 (4.1): Begrunnelse per spørsmål, vist når spørsmålet er lært. **Avklart i arkitekturen** (`Sporsmal.begrunnelse`, AD-11, AD-20). Mangler i PRD-en.
TF-3 (4.2, høy): Spørsmålsidentitet. **Avklart i arkitekturen** (AD-5).
TF-4 (4.3): Feil for innhold som ikke gir en god quiz, for store filer og API-feil, med melding og «Prøv igjen». **Avklart i arkitekturen** (AD-10). Test med minst én kort fil og én ugyldig nøkkel.
TF-5 (4.4): Kuttrekkefølge. **Besluttet 16.11:** faglærers forslag, se «Prioritering» under.
TF-6 (4.5): Dekningsgraden kan gå ned når en ny quiz lages, og kan ikke bli over 50 % uten quiz på vanskelig. Skal stå som akseptansekriterier og forklares i grensesnittet.
TF-7 (kap. 5): «Øv på feil» er en øvingsøkt, ikke et forsøk. **Avklart i arkitekturen** (`Okt.type`, AD-6).

### Prioritering (TF-5)

Epics og stories ordnes slik at kjerneløpet er ferdig først. Hver story merkes med gruppen sin.

| Gruppe | Krav |
|---|---|
| **Kjerne** | FR-1, FR-2, FR-3, FR-4, FR-7, FR-8, FR-9, FR-11, FR-12, FR-13, FR-17, FR-19, FR-20, FR-21, FR-23, FR-27, FR-28, FR-29, FR-30 |
| **Bør** | FR-5, FR-6, FR-14, FR-15, FR-16, FR-18 (lagring underveis og fortsette), FR-22 (øving uten ny stokking), FR-24, FR-26 |
| **Kan kuttes først** | FR-18 (fortsette fra annen enhet), FR-22 (ny stokking for hver økt), FR-25, FR-31 |

NFR-ene kuttes ikke. De bygges inn i hver story som akseptansekriterier. Merk at noen «bør»-krav i praksis følger med kjernen på grunn av arkitekturen: genereringskjeden i AD-9 gir fremdrift og timeout (FR-14, FR-15), og vanlige POST-skjemaer i AD-13 lagrer svar underveis (FR-18).

**Endret 20.11 (review):** FR-20 (ta en quiz på nytt) er flyttet fra «bør» til «kjerne». Ellers kan ikke FR-23 (kjerne) nås hvis alle «bør»-krav kuttes, fordi både nye forsøk (FR-20) og «Øv på feil» (FR-22) var «bør». Nye forsøk er den minste veien til «lært», og «Øv på feil» blir værende «bør». PRD-en må oppdateres tilsvarende.

### UX-designkrav (UX-DR)

UX-DR1: Design-tokens fra DESIGN.md i Tailwind v4 `@theme`: alle farger (tema «Frisk grønn» og practice-familien), typografi (systemfonter, 16/14/12 px, h1 26/22 px, spørsmål 18 px, alternativ 17 px, dekning 36/32 px, poeng 56 px), radius (4/8/10/full), avstandsskala 4–48 px, `content-max` 760 px, `gutter` 16 px og `target-min` 44 px. Størrelser i `rem`. Ingen mørk modus.
UX-DR2: Grunnmal for alle sider etter innlogging: topplinje (ikke klistret) med Tilbake, logoen «FåreQuiz» og menyknapp, brødsmuler over overskriften, landemerkene `<header>`, `<nav aria-label="Hovedmeny">` og `<main>`, én `<h1>`, `<title>` på formen «Side – sted – FåreQuiz», `lang` på siden og sentrert kolonne på maks 760 px.
UX-DR3: Tilbake-knapp som vanlig lenke til forelderen i hierarkiet (Emneside → Mine emner, Notatside og Last opp → emnet, Quiz, Resultat og Øv på feil → notatet), med `aria-label` som sier hvor, for eksempel «Tilbake til HTML». Vises ikke på Mine emner.
UX-DR4: Menypanel med `<details>` som virker uten JS: *Mine emner* (alle emnene som lenker), *+ Nytt emne*, *Fortsett der du slapp* og *Logg ut*. Åpnes med klikk, Enter og mellomrom. Esc lukker og setter fokus tilbake. Klikk utenfor lukker. 260 px bredt, eneste element med skygge.
UX-DR5: Knappevarianter: primær (grønn), sekundær (grønn kant), øve (oransje, bare «Øv på feil»), fare (rød, bare «Ja, slett emnet») og låst (grå). Minst 44 px høye. Ett fylt hovedvalg per skjerm. Knappetekster sier hva som skjer.
UX-DR6: Fokusring på 3 px i primærfargen med 2 px avstand, oransje i «Øv på feil». Fokus skjules aldri.
UX-DR7: Listerad der hele raden er én lenke, med navn, metadata og dekningsstolpe med prosent. Emner og notater sorteres alfabetisk. Quizer og historikk sorteres med nyeste øverst.
UX-DR8: Dekningsstolpe (10 px) alltid med prosenttall. Dekningskort med stort tall. På notatsiden tre nivåbokser «Lett · 20 %», «Middels · 30 %», «Vanskelig · 50 %». Emne uten dekningsgrad viser «Ingen dekningsgrad». Nivå uten quiz viser «Ingen quiz».
UX-DR9: Fortsett-boksen «Fortsett der du slapp» nederst på Mine emner og i menyen: alle påbegynte forsøk og øvingsøkter, nyeste først, med tekst som «Webutvikling › HTML · Middels · 5 av 10 besvart». Hver rad lenker til første ubesvarte spørsmål. Vises ikke når det ikke finnes noen.
UX-DR10: Spørsmålsboks og svaralternativer: spørsmålet er `<legend>` for tre radioknapper i `<label>`, så hele boksen er klikkbar. Alternativene er minst 56 px. Valgt alternativ har blekgrønn flate og 2 px grønn kant (oransje i øving). Piltastene flytter mellom alternativene. `lang` fra quizen når språket ikke er norsk.
UX-DR11: Quizfremdrift med «Spørsmål N av M», en 8 px stolpe og KI-merket ved siden av.
UX-DR12: Forrige, Neste og Lever: Neste og Forrige lagrer svaret og går videre, og det går an å gå videre uten å svare. På siste spørsmål er Neste byttet ut med Lever. Mislykket lagring gir «Svaret ble ikke lagret. Sjekk nettet og prøv igjen.» ved knappen, og studenten blir på samme spørsmål.
UX-DR13: KI-merket «Laget av KI (<modell>) · kan inneholde feil», med modellnavnet fra quizen, ved hver quiz på Notatside og over spørsmålet i Quiz og i Øv på feil. Vises også i testmodus.
UX-DR14: Merkelapper: gul «Påbegynt N/M» med knappen «Fortsett» i stedet for «Ta på nytt», og oransje «Øv på feil».
UX-DR15: Valg av vanskelighetsgrad som tre radioknapper i bokser, med middels valgt. Tallfelt for antall, 5–30, standard 10, med feilmelding ved feltet ved verdi utenfor.
UX-DR16: Last opp notat på én side: vanlig filvelger uten dra-og-slipp, sjekk av format og størrelse i nettleseren når det går og alltid på serveren, nivå, antall, KI-merknad (blekgrønn med grønn stripe), vilkårsboks bare første gang med «Jeg godtar vilkårene» og «Les vilkårene» som folder ut teksten, og «Lag quiz». Ved avvist fil står valgene igjen.
UX-DR17: Ventepanel som erstatter skjemaet mens quizen lages: spinner, den faste overskriften «Lager quiz, håper du er klar!», steglinjen «Steg 1 av 3: Leser filen» → «Steg 2 av 3: Lager spørsmål» → «Steg 3 av 3: Sjekker quizen» med `role="status"` og `aria-live="polite"`, og tre små stolper som fylles. Ved suksess åpnes Quiz på spørsmål 1.
UX-DR18: Feiltilstander for generering: timeout gir «Det tok for lang tid å lage quizen. Filen er lagret, så du trenger ikke laste den opp på nytt.» og «Prøv igjen» med samme valg. Formatfeil to ganger gir «Vi klarte ikke å lage en gyldig quiz. Prøv igjen, eller velg færre spørsmål.» De andre feilkodene i AD-10 får egne tekster i samme tone.
UX-DR19: Feilmelding-komponent: lys rød flate, fet overskrift, står ved feltet eller knappen, får fokus eller har `role="alert"`, og lenker hopper til feltet eller spørsmålet. Manglende svar ved levering gir «Du har ikke svart på alle spørsmålene. Disse mangler: spørsmål 4, spørsmål 7.» med lenker.
UX-DR20: Resultatside: poengkort med «7 av 10» i 56 px og «riktige svar» med `role="status"`, resultatrader med «✓ Riktig» eller «✗ Feil» og spørsmålsnummer, ingen fasit for feil svar, «N spørsmål er lagt i feilbanken. Øv på dem til du kan dem.» og knappen «Øv på feil».
UX-DR21: «Øv på feil» som egen modus med samme oppsett som Quiz, der practice-familien (oransje) erstatter primary-familien helt: knapper, valgt svar, fremdrift og fokus.
UX-DR22: Øv-resultat: poengsum, lært-boks øverst for hvert spørsmål som ble lært i økten, med «Lært! ✓», spørsmålet og «Fasit: …» (og begrunnelsen, TF-2), deretter riktig/feil og telleren for resten. Når feilbanken er tom: «Feilbanken er tom. Godt jobba!» og «Tilbake til <notat>». Lært er det eneste stedet med en liten feiring.
UX-DR23: Notatside med seksjonene under hverandre: dekningskort med nivåbokser, feilbank-rad («N spørsmål å øve på» og «Øv på feil», eller låst knapp med «Ingen feil å øve på»), quizer med nivå, antall, dato, KI-merke og «Ta på nytt»/«Fortsett», «Lag ny quiz» med nivå og antall, og historikktabell med Dato, Quiz og Poengsum.
UX-DR24: Slett emne på en egen bekreftelsesside, ikke popup: «Slette «<navn>»? Dette sletter N notater og alle quizene …». «Avbryt» er like lett å nå som «Ja, slett emnet».
UX-DR25: Tomtilstander: velkomstkort for ny bruker («Velkommen til FåreQuiz», én setning og «Opprett ditt første emne»), og emne uten notater med «Ingen notater ennå» og «+ Last opp notat».
UX-DR26: Testmodus-stripe øverst på alle sider: «Testmodus – quizene er forhåndslagret og laget av KI tidligere.» Quiz fra ukjent fil får merknaden «Testmodus: denne quizen er laget fra et forhåndslagret testdokument, ikke fra filen din.» på Notatside og Quiz.
UX-DR27: «Ikke funnet»-side med «Fant ikke siden» og lenke til Mine emner, som ikke avslører om dataene finnes hos andre.
UX-DR28: Innlogging og registrering som vanlige skjemaer med synlige etiketter, `autocomplete="email"` og `current-password`/`new-password`, innliming tillatt og «Feil e-post eller passord.» som felles melding.
UX-DR29: Responsivt oppsett: over 760 px sentrert kolonne, 400–760 px full bredde med 16 px marg og knapper som brytes, under 480 px mindre overskrifter og tall, under 400 px skjules logoen. Ingen vannrett rulling ned til 320 px og ved 200 % tekst.
UX-DR30: Stemme og tone etter EXPERIENCE.md: kort, vennlig, du-form, tekstene i tabellen «Gjør» brukes ordrett der de finnes.

### Kravdekning (FR → epic)

FR-1: Epic 1 – Registrere konto
FR-2: Epic 1 – Logge inn og ut
FR-3: Epic 1 – Bare egne data (eierhjelperne brukes i alle senere epics)
FR-4: Epic 1 – Opprette emne
FR-5: Epic 1 – Gi emne nytt navn
FR-6: Epic 1 – Slette emne med alt innhold
FR-7: Epic 2 – Godta vilkår én gang
FR-8: Epic 2 – Laste opp fil
FR-9: Epic 2 – Lese innholdet i filen
FR-11: Epic 2 – Velge vanskelighetsgrad og antall
FR-12: Epic 2 – Generere quiz
FR-13: Epic 2 – Sjekke formatet og generere på nytt én gang
FR-14: Epic 2 – Vise fremdrift og låse knappen
FR-15: Epic 2 – Timeout og «Prøv igjen»
FR-16: Epic 2 – Flere quizer per notat
FR-17: Epic 3 – Svare og levere
FR-18: Epic 3 – Fortsette et påbegynt forsøk, med «Fortsett der du slapp»
FR-19: Epic 3 – Se resultat uten fasit
FR-20: Epic 3 – Ta en quiz på nytt
FR-21: Epic 3 – Feilsvar havner i feilbanken
FR-22: Epic 4 – Øv på feil
FR-23: Epic 3 (regelen for to riktige på rad) og Epic 4 (fasit vises når spørsmålet er lært)
FR-24: Epic 5 – Dekningsgrad per notat
FR-25: Epic 5 – Dekningsgrad per emne
FR-26: Epic 5 – Historikk
FR-27: Epic 2 – Testmodus med mock-svar
FR-28: Epic 6 – Testbruker med eksempeldata
FR-29: Epic 1 (`.env` med standardverdier) og Epic 2 (API-nøkkel og modell)
FR-30: Epic 6 – README for lokal kjøring
FR-31: Epic 4 – Melde spørsmål som feil

NFR-1 til NFR-9 bygges inn som akseptansekriterier i alle stories med grensesnitt. NFR-5 og NFR-7 hører hjemme i Epic 2, NFR-9 i Epic 2 til 4. Sluttkontrollen av NFR-8 (SM-7) ligger i Epic 6.

## Epic-liste

**Rekkefølge:** 1 → 2 → 3 → 4 → 5, og 6 til slutt. Etter Epic 3 er kjerneløpet notat → quiz → feilbank → lært ferdig. Når story 1.1 er ferdig, kan resten av Epic 1 og `ki`-modulen i Epic 2 bygges parallelt. Epic 5 kan bygges parallelt med Epic 4.

### Epic 1: Konto og emner
Studenten kan registrere seg, logge inn og ut, og opprette, gi nytt navn til og slette emner, og ser bare sine egne data. Første story setter opp prosjektskjelettet med alle modeller og CI. Tailwind-tokens og grunnmalen kommer i story 1.3.
**FR dekket:** FR-1, FR-2, FR-3, FR-4, FR-5, FR-6, FR-29
**Prioritet:** kjerne (FR-5 og FR-6: bør)

### Epic 2: Fra notat til quiz
Studenten godtar vilkårene, laster opp et notat, velger nivå og antall, og får en KI-laget quiz med fremdrift, låst knapp og «Prøv igjen». Alt virker i testmodus uten API-nøkkel.
**FR dekket:** FR-7, FR-8, FR-9, FR-11, FR-12, FR-13, FR-14, FR-15, FR-16, FR-27, FR-29
**Prioritet:** kjerne (FR-14, FR-15 og FR-16: bør)

### Epic 3: Ta quiz, se resultat og fyll feilbanken
Studenten tar quizen med svar som lagres underveis, kan fortsette der hen slapp, leverer, ser poengsummen uten fasit, og feilsvarene havner i feilbanken. En levert quiz kan tas på nytt.
**FR dekket:** FR-17, FR-18, FR-19, FR-20, FR-21, FR-23
**Prioritet:** kjerne (fortsette fra annen enhet: kan kuttes)

### Epic 4: Øv på feil til det sitter
Studenten øver på feilbanken i oransje øvemodus, ser «Lært! ✓» med fasit og begrunnelse, og kan melde et spørsmål som feil.
**FR dekket:** FR-22, FR-23, FR-31
**Prioritet:** bør (FR-31 og ny stokking: kan kuttes)

### Epic 5: Se progresjonen
Studenten ser dekningsgraden per notat med fordeling per nivå, dekningsgraden per emne, og historikken med alle forsøk.
**FR dekket:** FR-24, FR-25, FR-26
**Prioritet:** bør (FR-25: kan kuttes)

### Epic 6: Klar for sensor
Sensor kloner repoet, følger README-en, logger inn som testbrukeren med ferdige data og kjører hele kjerneflyten uten nøkkel. Epicen har også sluttkontroll av universell utforming og KI-kvalitet.
**FR dekket:** FR-28, FR-30
**Prioritet:** kjerne

## Epic 1: Konto og emner

Studenten kan registrere seg, logge inn og ut, og opprette, gi nytt navn til og slette emner, og ser bare sine egne data. Første story setter opp prosjektskjelettet som resten av gruppa bygger på.

### Story 1.1: Prosjektskjelett med datamodell og CI

Som utvikler i gruppa,
vil jeg ha et kjørbart Django-prosjekt med hele datamodellen, testmodus på som standard og CI på hver pull request,
slik at vi kan jobbe parallelt i hver vår story uten migreringskonflikter og uten API-nøkkel.

*Prioritet: kjerne. Avvik fra BMad-regelen om tabeller per story: arkitekturen krever at alle modeller lages her (konvensjon for migreringer), fordi tre personer jobber parallelt. Tailwind og htmx er flyttet til story 1.3 (20.11), slik at denne storyen bare inneholder det alle andre stories venter på.*

**Akseptansekriterier:**

**Gitt** en ny klone uten `.env`
**Når** utvikleren kjører `uv sync`, `python manage.py migrate` og `python manage.py runserver`
**Så** starter appen på `localhost:8000` med `DEBUG=True`, en fast usikker utviklingsnøkkel, `ALLOWED_HOSTS=localhost,127.0.0.1` og testmodus på (AD-22)
**Og** `pip install -r requirements.txt` gir de samme pakkene, og `requirements.txt` er laget med `uv export --no-hashes`

**Gitt** prosjektet
**Når** strukturen sjekkes
**Så** finnes appene `farequiz`, `kontoer`, `studier` og `ki` etter strukturfrøet, med Python 3.14, Django ≥ 5.2.19 < 6, `anthropic` ≥ 2.8 < 3, `python-docx` 1.2.0 og `python-dotenv` 1.2.4
**Og** `.env.example` har `ANTHROPIC_API_KEY`, `KI_MODELL=claude-sonnet-5-5`, `TESTMODUS`, `SECRET_KEY`, `DEBUG` og `ALLOWED_HOSTS` uten ekte verdier, og `.env`, `db.sqlite3` og `media/` står i `.gitignore` (FR-29)
**Og** `.gitattributes` har `testdokumenter/** binary` og `ki/mock/** -text`

**Gitt** første `migrate`
**Når** migreringene kjøres
**Så** finnes `kontoer.Bruker` med e-post som `USERNAME_FIELD`, uten `username`, med `vilkar_godtatt` og `BrukerManager.create_user(email, password)` som lagrer e-post med små bokstaver, og `AUTH_USER_MODEL = "kontoer.Bruker"` (AD-15)
**Og** `Emne`, `Notat`, `Quiz`, `Sporsmal`, `Alternativ`, `Okt`, `Svar`, `Feilbankrad` og `Genereringsjobb` finnes med feltene og constraints fra AD-3, AD-6, AD-7, AD-9, AD-11, AD-14 og AD-16, blant annet `CheckConstraint` for `Okt.quiz`, betinget `UniqueConstraint` for påbegynte økter, `UniqueConstraint(okt, sporsmal)` på `Svar`, unik `Feilbankrad.sporsmal` og `Quiz.jobb` som `OneToOneField`
**Og** `Sporsmal` har det nullbare feltet `meldt_tidspunkt` for FR-31. Det brukes først i story 4.3, men lages her, slik at 4.3 ikke trenger en ny migrering
**Og** faste verdier er `TextChoices`, og migreringene er committet

**Gitt** innstillingene
**Når** de leses
**Så** er `ATOMIC_REQUESTS` av, SQLite har `OPTIONS = {"transaction_mode": "IMMEDIATE", "timeout": 20}`, `USE_TZ=True` og `TIME_ZONE="Europe/Oslo"` (AD-19)
**Og** `LoginRequiredMiddleware` er på (AD-8)

**Gitt** `ki/__init__.py`
**Når** `ki.er_testmodus()` kalles
**Så** er den sann når `TESTMODUS` er `1`, `true`, `yes` eller `on`, eller når `ANTHROPIC_API_KEY` mangler, og `ki.tving_testmodus()` slår den på i tester (AD-12)
**Og** `ki` importerer ingenting fra `studier` eller `kontoer`

**Gitt** `studier/tilgang.py`
**Når** `hent_egen(modell, pk, bruker)` eller `egne(modell, bruker)` kalles med en annen brukers objekt
**Så** gir `hent_egen` `Http404`, og `egne` tar ikke med objektet, for alle modellene i `studier` med eierveiene fra AD-8
**Og** enhetstester dekker begge hjelperne for hver modell

**Gitt** en pull request mot `main`
**Når** CI kjører `.github/workflows/test.yml`
**Så** kjøres `ruff check`, `ruff format --check` og `python manage.py test` uten API-nøkkel og med testmodus på
**Og** CI er grønn på denne storyen

### Story 1.2: Registrere konto og logge inn og ut

Som student,
vil jeg registrere meg med e-post og passord og logge inn og ut,
slik at notatene og quizene mine er mine og bare mine.

*Prioritet: kjerne. FR-1, FR-2, NFR-2, UX-DR28.*

**Akseptansekriterier:**

**Gitt** en besøkende på Registrer
**Når** hen sender en gyldig e-post og et passord på minst 8 tegn
**Så** lages kontoen med e-post i små bokstaver og passordet som hash, brukeren logges inn og sendes til startsiden `/`, som foreløpig er en enkel side som story 1.4 gjør til Mine emner
**Og** en e-post som finnes fra før, også med andre store og små bokstaver, gir feilmelding ved feltet og ingen ny konto
**Og** ugyldig e-post og for kort passord gir feilmelding ved feltet, og den utfylte e-posten står igjen

**Gitt** en registrert bruker på Logg inn
**Når** hen sender riktig e-post og passord
**Så** logges hen inn og sendes til startsiden `/`
**Og** feil passord og ukjent e-post gir den samme meldingen «Feil e-post eller passord.»

**Gitt** en innlogget bruker
**Når** hen logger ut med et POST-skjema
**Så** sendes hen til Logg inn, og alle sider unntatt Logg inn og Registrer sender hen til Logg inn
**Og** bare Logg inn og Registrer har `@login_not_required`

**Gitt** skjemaene for Logg inn og Registrer
**Når** de brukes med tastatur, skjermleser og passordbehandler
**Så** har alle felt synlige etiketter, `autocomplete="email"` og `current-password` eller `new-password`, innliming virker, og det finnes ingen kognitiv test (3.3.8)
**Og** feilmeldinger står ved feltet og har `role="alert"` eller får fokus (3.3.1)
**Og** sidene har `lang="nb"`, én `<h1>`, `<main>` og en `<title>` som «Logg inn – FåreQuiz»

### Story 1.3: Topplinje, meny og felles sidemal

Som innlogget student,
vil jeg ha samme topplinje, meny og navigasjon på alle sider,
slik at jeg alltid vet hvor jeg er og kommer meg tilbake.

*Prioritet: kjerne. UX-DR1 til UX-DR6, UX-DR26 (stripen), UX-DR27, UX-DR29, UX-DR30. Første story med grensesnitt, og derfor den som setter opp Tailwind og htmx (flyttet fra story 1.1 20.11).*

**Akseptansekriterier:**

**Gitt** Tailwind v4 frittstående CLI
**Når** `tailwindcss -i static/src/app.css -o static/css/app.css --minify` kjøres
**Så** inneholder `@theme` alle farger, typografi, radius og avstander fra DESIGN.md, i `rem`, og `static/css/app.css` er committet (UX-DR1)
**Og** htmx 2.0.11 ligger som `static/js/htmx.min.js`, ikke via CDN

**Gitt** en side etter innlogging
**Når** den vises
**Så** har den `<header>` med en topplinje som ikke er klistret (Tilbake, logoen «FåreQuiz» som lenker til Mine emner, og «☰ Meny»), plass til brødsmuler over overskriften, én `<h1>`, `<main>` og en sentrert kolonne på maks 760 px med 16 px marg
**Og** `<title>` følger formen «Side – sted – FåreQuiz», og CSRF-tokenet ligger i `hx-headers` på `<body>`

**Gitt** menyen
**Når** den åpnes og lukkes med klikk, Enter, mellomrom og Esc
**Så** er den en `<details>` i `<nav aria-label="Hovedmeny">` som virker uten JavaScript, Esc lukker og setter fokus tilbake på knappen, og klikk utenfor lukker
**Og** menyen har *Logg ut* (POST). *Mine emner*, *+ Nytt emne* og *Fortsett der du slapp* legges til av storyene som lager de sidene

**Gitt** en side med forelder i hierarkiet
**Når** Tilbake vises
**Så** er den en vanlig lenke til forelderen med `aria-label` som sier hvor, og den vises ikke på Mine emner (UX-DR3)

**Gitt** at testmodus er på
**Når** en side vises
**Så** står stripen «Testmodus – quizene er forhåndslagret og laget av KI tidligere.» øverst, med flagget fra en context processor som kaller `ki.er_testmodus()` (AD-12)

**Gitt** en URL som ikke finnes, eller en ID som tilhører en annen bruker
**Når** siden åpnes
**Så** vises «Fant ikke siden» med lenke til Mine emner og status 404, uten å si om dataene finnes hos andre (FR-3)

**Gitt** knappekomponentene og fokusringen
**Når** de brukes
**Så** er primær-, sekundær-, øve-, fare- og låst knapp minst 44 px høye med tokenfargene, og fokusringen er 3 px i primærfargen med 2 px avstand (UX-DR5, UX-DR6)
**Og** ved 320 px bredde og 200 % tekst er det ingen vannrett rulling, og under 400 px skjules logoen (UX-DR29)

**Gitt** tekstene i grensesnittet i denne og alle senere stories
**Når** de skrives
**Så** følger de stemmen og tonen i EXPERIENCE.md: kort, vennlig og du-form, med tekstene fra «Gjør»-tabellen ordrett der de finnes, og knapper som sier hva som skjer (UX-DR30)

### Story 1.4: Opprette emne og se Mine emner

Som student,
vil jeg opprette emner og se dem på startsiden,
slik at jeg kan samle notatene fra hvert fag.

*Prioritet: kjerne. FR-3, FR-4, UX-DR7, UX-DR25.*

**Akseptansekriterier:**

**Gitt** en ny bruker uten emner
**Når** Mine emner åpnes
**Så** vises velkomstkortet med «Velkommen til FåreQuiz», én setning om hva appen gjør og den store knappen «Opprett ditt første emne»

**Gitt** Nytt emne
**Når** brukeren sender et navn
**Så** lagres emnet med brukeren som eier fra skjemaets konstruktør, og brukeren sendes til Emnesiden med «Ingen notater ennå» (AD-1). Knappen «+ Last opp notat» legges til i story 2.3, «Gi emnet nytt navn» i 1.5 og «Slett emne» i 1.6
**Og** tomt navn gir feilmelding ved feltet
**Og** et navn brukeren alt har, uten å skille store og små bokstaver, gir feilmelding ved feltet, mens en annen bruker kan ha samme navn

**Gitt** en bruker med emner
**Når** Mine emner åpnes
**Så** listes brukerens egne emner alfabetisk som listerader der hele raden er én lenke, med plass til dekningsgrad (fylles i Epic 5)
**Og** menyen viser *Mine emner* med alle emnene som lenker, og *+ Nytt emne*

**Gitt** to brukere
**Når** bruker A åpner `/emner/<id>/` for et emne som tilhører B
**Så** får A «Fant ikke siden», og alle emnevisninger bruker `hent_egen` eller `egne` (AD-8)

### Story 1.5: Gi emne nytt navn

Som student,
vil jeg gi et emne nytt navn,
slik at jeg kan rette skrivefeil eller endre hvordan jeg organiserer fagene.

*Prioritet: bør. FR-5.*

**Akseptansekriterier:**

**Gitt** Emnesiden
**Når** brukeren velger «Gi emnet nytt navn»
**Så** vises samme skjema som Nytt emne, ferdig utfylt med dagens navn, og Tilbake går til emnet

**Gitt** skjemaet
**Når** brukeren sender et nytt gyldig navn
**Så** lagres navnet, brukeren sendes til Emnesiden, og notater, quizer og historikk i emnet er uendret
**Og** tomt navn og navn brukeren alt har på et annet emne, gir samme feilmeldinger som i story 1.4, mens samme navn med andre store og små bokstaver på samme emne godtas

**Gitt** et emne som tilhører en annen bruker
**Når** noen sender POST mot nytt navn for det
**Så** får hen «Fant ikke siden», og navnet endres ikke

### Story 1.6: Slette emne

Som student,
vil jeg slette et emne etter å ha bekreftet det,
slik at jeg kan rydde bort fag jeg er ferdig med, med alle filene.

*Prioritet: bør. FR-6, AD-14, UX-DR24.*

**Akseptansekriterier:**

**Gitt** Emnesiden
**Når** brukeren velger «Slett emne»
**Så** vises en egen bekreftelsesside, ikke en popup, med «Slette «<navn>»? Dette sletter N notater og alle quizene …» og antall notater
**Og** «Avbryt» er like lett å nå som den røde knappen «Ja, slett emnet»

**Gitt** bekreftelsessiden
**Når** brukeren trykker «Ja, slett emnet»
**Så** sletter `services.emner.slett_emne` emnet med notater, quizer, økter, svar, feilbankrader og jobber i én `transaction.atomic`, og filene på disk slettes i `transaction.on_commit`
**Og** en fil som alt mangler på disk, gir ingen feil
**Og** brukeren sendes til Mine emner, og andre emner og dataene deres er uendret

**Gitt** en test med et emne som har et notat med fil, laget direkte i testoppsettet, fordi opplasting først kommer i story 2.3
**Når** emnet slettes
**Så** finnes verken radene eller filen etterpå, og hvis transaksjonen ruller tilbake, ligger filen igjen

**Gitt** et emne som tilhører en annen bruker
**Når** noen sender POST mot sletting av det
**Så** får hen «Fant ikke siden», og ingenting slettes
**Og** ingen andre funksjoner enn `slett_emne` sletter `Notat`, `Quiz`, `Okt` eller `Feilbankrad`

## Epic 2: Fra notat til quiz

Studenten godtar vilkårene, laster opp et notat, velger nivå og antall, og får en KI-laget quiz med fremdrift, låst knapp og «Prøv igjen». Alt virker i testmodus uten API-nøkkel. Story 2.1 og 2.2 rører bare `ki` og kan bygges parallelt med resten av Epic 1.

### Story 2.1: Lese filen og sjekke quizutkastet

Som utvikler i gruppa,
vil jeg at `ki` kan lese en notatfil og sjekke et svar fra modellen mot formatet,
slik at alle quizer som lagres, har riktig form uansett om de kommer fra modellen eller fra mock-svar.

*Prioritet: kjerne. FR-9, FR-12, FR-13, AD-10, AD-11. Ingen databasetilgang. Eier testdokumentene, som story 2.2 og 6.4 bygger på (lagt til 20.11).*

**Akseptansekriterier:**

**Gitt** mappen `testdokumenter/`
**Når** storyen er ferdig
**Så** ligger de fem testdokumentene der: en tekst-PDF på ca. 10 sider, en lysbilde-PDF, en skannet PDF, en DOCX og en TXT, og minst ett av dem er på et annet språk enn norsk (FR-9, FR-12)
**Og** `testdokumenter/KILDER.md` oppgir kilde og lisens for hvert dokument, slik at ingen av dem bryter opphavsretten
**Og** testene for `les_fil` bruker disse filene

**Gitt** en PDF, en DOCX og en TXT
**Når** `ki.les_fil(sti)` kalles
**Så** returneres `Innhold(sha256, type, data)`, der PDF-en er hele filen og DOCX og TXT er uttrukket tekst
**Og** TXT leses som UTF-8 med cp1252 som reserve, og `sha256` er hashen av filens bytes
**Og** en fil som mangler, gir `KIFeil("api_feil")`, og en DOCX eller TXT uten tekst gir `KIFeil("for_lite_innhold")`

**Gitt** et rått svar fra modellen eller mock-filen
**Når** `ki.sjekk(raatt, antall)` kalles
**Så** returneres `QuizUtkast` med `sprak`, `modell`, `prompt_versjon`, `forhandslagret` og `sporsmal`, der hvert spørsmål har `tekst`, `begrunnelse` og tre `alternativer` med `tekst` og `er_riktig`
**Og** `KIFeil("format")` heves ved feil antall spørsmål, et annet antall alternativer enn tre, et annet antall riktige enn ett, to like alternativer, to like spørsmål, manglende felt eller ugyldig JSON

**Gitt** `ki`
**Når** koden sjekkes
**Så** importerer den ingenting fra `studier` eller `kontoer`, og `KIFeil(kode)` bruker bare kodene i AD-10
**Og** enhetstester dekker hver formatfeil i FR-13 hver for seg

### Story 2.2: Generere med modellen eller mock-svar

Som sensor uten API-nøkkel,
vil jeg at genereringen gir en quiz fra lagrede mock-svar,
slik at jeg kan kjøre hele appen lokalt uten gruppas nøkkel.

*Prioritet: kjerne. FR-9, FR-12, FR-27, FR-29, NFR-3, NFR-5, NFR-7, AD-11, AD-12.*

**Akseptansekriterier:**

**Gitt** at testmodus er av og det finnes en API-nøkkel
**Når** `ki.generer(innhold, vanskelighetsgrad, antall, timeout)` kalles
**Så** kalles modellen i `KI_MODELL` (standard `claude-sonnet-5-5`) med PDF-en som dokument eller teksten, structured outputs (`output_config.format`) med skjemaet fra AD-11 og `effort` satt eksplisitt
**Og** svaret er `RaattSvar(tekst, forhandslagret=False, modell, prompt_versjon=PROMPT_VERSJON)`
**Og** ugyldig nøkkel gir `KIFeil("api_nokkel")`, for stor fil eller for mange sider gir `KIFeil("for_stor")`, timeout gir `KIFeil("timeout")`, og andre API- og nettfeil gir `KIFeil("api_feil")`

**Gitt** at testmodus er på
**Når** `ki.generer` kalles
**Så** gjøres ingen nettverkskall, `innhold.sha256` slås opp i `ki/mock/manifest.json`, og de første N spørsmålene returneres fra `ki/mock/<dokument>/<vanskelighetsgrad>.json` med `modell` og `prompt_versjon` fra filens metadata
**Og** en ukjent fil gir standarddokumentet med `forhandslagret=True`
**Og** en test med nettverket blokkert bekrefter at testmodus aldri kaller API-et (NFR-3)

**Gitt** de fem testdokumentene i `testdokumenter/` fra story 2.1
**Når** en med API-nøkkel kjører `python manage.py lag_mocksvar`
**Så** kjøres hvert dokument mot ekte modell med 30 spørsmål per nivå, svarene sjekkes med `ki.sjekk`, og mock-filene og manifestet skrives og committes
**Og** alle fem dokumentene gir en gyldig quiz, også lysbilde-PDF-en og den skannede PDF-en (FR-9)
**Og** testene bruker de committede mock-filene, ikke API-et

**Gitt** malene
**Når** en quiz vises
**Så** gir `ki.visningsnavn(modell)` et lesbart navn som «Claude Sonnet 5.5», og `PROMPT_VERSJON` er definert ett sted i `ki`

### Story 2.3: Godta vilkår og laste opp notat

Som student,
vil jeg laste opp forelesningsnotatet mitt under et emne,
slik at appen kan lage quizer fra det.

*Prioritet: kjerne. FR-7, FR-8, AD-1, AD-14, UX-DR16.*

**Akseptansekriterier:**

**Gitt** Emnesiden
**Når** brukeren trykker «+ Last opp notat»
**Så** vises Last opp notat med vanlig filvelger uten dra-og-slipp, valg av nivå (middels valgt), antall (10, 5–30), KI-merknaden om at innholdet sendes til en ekstern KI-tjeneste (Anthropic) og knappen «Lag quiz»
**Og** Tilbake går til emnet

**Gitt** en bruker som ikke har godtatt vilkårene
**Når** siden vises
**Så** vises vilkårsboksen med «Jeg godtar vilkårene» og «Les vilkårene», som folder ut teksten om ansvar for personopplysninger, at innholdet sendes til Anthropic, og at quizene lages av KI og kan inneholde feil
**Og** uten kryss gir sending feilmelding ved boksen, og ingenting lastes opp
**Og** med kryss lagrer `last_opp` tidspunktet i `Bruker.vilkar_godtatt`, og boksen vises ikke igjen

**Gitt** en fil på over 5 MB eller i et annet format enn PDF, DOCX og TXT (for eksempel MP4, PPTX eller et bilde)
**Når** brukeren sender skjemaet
**Så** avvises filen på serveren med «Bare PDF, DOCX og TXT på maks 5 MB kan lastes opp.» ved filfeltet med `role="alert"`, og valgene står igjen
**Og** nettleseren sjekker format og størrelse før opplasting når det går

**Gitt** en gyldig fil
**Når** brukeren sender skjemaet
**Så** lagrer `services.notater.last_opp` filen som `notater/<eier-id>/<uuid4><endelse>` og et `Notat` med `originalnavn`, `filtype` og `storrelse` i emnet (AD-14)
**Og** brukeren sendes til Notatsiden, som viser notatets navn og «Ingen quizer ennå», og notatet står i listen på Emnesiden, sortert alfabetisk. Dette er midlertidig: story 2.4 bytter det ut med ventepanelet og genereringen
**Og** filen kan ikke lastes ned via noen URL (AD-8)

**Gitt** et emne som tilhører en annen bruker
**Når** noen sender en opplasting til det
**Så** får hen «Fant ikke siden», og ingenting lagres

### Story 2.4: Lage quiz med fremdrift

Som student,
vil jeg trykke «Lag quiz» og se hvilket steg genereringen er på,
slik at jeg vet at noe skjer og ikke lager to quizer ved et uhell.

*Prioritet: kjerne (fremdrift og låst knapp: bør). FR-11 til FR-14, AD-9, AD-19, UX-DR17.*

**Akseptansekriterier:**

**Gitt** Last opp notat med gyldig fil og valg
**Når** brukeren trykker «Lag quiz»
**Så** lagres notatet, en `Genereringsjobb` opprettes med valgt nivå og antall, og skjemaet byttes ut med ventepanelet «Lager quiz, håper du er klar!» og en låst knapp
**Og** antall utenfor 5–30 gir feilmelding ved feltet

**Gitt** en jobb som er i gang
**Når** siden spør `/jobber/<id>/steg/` med HTMX-POST (`hx-post`, fordi kallet endrer jobben)
**Så** tas jobben med `filter(pk, status=S, i_gang=False).update(i_gang=True)`, ett steg kjøres, og fragmentet viser «Steg 1 av 3: Leser filen» → «Steg 2 av 3: Lager spørsmål» → «Steg 3 av 3: Sjekker quizen» med `role="status"` og `aria-live="polite"`
**Og** endres 0 rader, returneres bare gjeldende fragment, som spør igjen
**Og** ingen `ki`-kall skjer mens en databasetransaksjon er åpen, og filinnholdet lagres aldri på jobben eller i sesjonen (AD-19)

**Gitt** at `sjekk` finner formatfeil i runde 1
**Når** steget `sjekker` kjører
**Så** går jobben tilbake til `lager` med `runde=2`, og feiler formatet igjen, blir jobben `feilet` med `feilkode="format"`, og ingen quiz lagres (FR-13)

**Gitt** et gyldig utkast
**Når** steget `sjekker` er ferdig
**Så** lagres `Quiz` med `jobb`, `vanskelighetsgrad`, `sprak`, `modell`, `prompt_versjon` og `forhandslagret`, og hvert `Sporsmal` med `begrunnelse` og tre `Alternativ`, nøyaktig ett med `er_riktig` (AD-7, AD-11)
**Og** brukeren sendes til Notatsiden, der quizen står med nivå, antall, dato og KI-merket «Laget av KI (<modell>) · kan inneholde feil» (NFR-9). Story 3.1 endrer dette til å åpne quizen på spørsmål 1
**Og** en quiz har nøyaktig det valgte antallet spørsmål, også når den kommer fra mock-svar

**Gitt** en aktiv jobb for notatet
**Når** brukeren laster siden på nytt, åpner en ny fane eller trykker «Lag quiz» igjen
**Så** opprettes ingen ny jobb, og ventepanelet for den aktive jobben vises (`aktiv_jobb(notat)`, FR-14)
**Og** to samtidige kall på samme steg gir ett KI-kall og én quiz (`Quiz.jobb` er `OneToOneField`)

**Gitt** `services.generering.generer_synkront(notat, vanskelighetsgrad, antall)`
**Når** den kalles fra en test eller kommando
**Så** kjøres de samme stegfunksjonene etter hverandre uten HTMX og returnerer quizen (brukes av seed i Epic 6)

### Story 2.5: Feil, timeout og «Prøv igjen»

Som student,
vil jeg få en melding som sier hva som gikk galt og kunne prøve igjen uten ny opplasting,
slik at en feil hos KI-tjenesten ikke stopper meg.

*Prioritet: bør. FR-13, FR-15, AD-9, AD-10, UX-DR18, TF-4.*

**Akseptansekriterier:**

**Gitt** en jobb som har stått i over 120 sekunder uten å bli ferdig
**Når** den leses av `aktiv_jobb` eller stegendepunktet
**Så** settes den til `feilet` med `feilkode="timeout"`, og ventepanelet byttes ut med «Det tok for lang tid å lage quizen. Filen er lagret, så du trenger ikke laste den opp på nytt.» og knappen «Prøv igjen»

**Gitt** en feilet jobb med `feilkode` `format`, `for_lite_innhold`, `for_stor`, `api_nokkel` eller `api_feil`
**Når** feilfragmentet vises
**Så** vises teksten for koden fra `farequiz/feilmeldinger.py` med `role="alert"`, for eksempel «Vi klarte ikke å lage en gyldig quiz. Prøv igjen, eller velg færre spørsmål.» for `format`
**Og** teksten sier hva brukeren kan gjøre, ingen quiz lagres, og «Lag quiz» er låst opp
**Og** jobben logges til konsollen med jobb-ID og feilkode, aldri med filinnhold

**Gitt** en feilet jobb
**Når** brukeren trykker «Prøv igjen»
**Så** opprettes en ny jobb med den lagrede filen og samme nivå og antall, uten ny opplasting, og ventepanelet vises igjen

**Gitt** at notatet eller jobben er slettet mens genereringen pågår
**Når** siden spør stegendepunktet
**Så** returneres et sluttfragment med lenke til Mine emner, ikke 404, og ingen quiz lagres

**Gitt** testene
**Når** de kjøres
**Så** dekker de hver feilkode med en `ki`-stub, og minst én test bruker en kort TXT og én test en ugyldig nøkkel (TF-4)

### Story 2.6: Flere quizer per notat

Som student,
vil jeg lage nye quizer fra et notat jeg alt har lastet opp,
slik at jeg kan øve på flere nivåer uten å laste opp filen igjen.

*Prioritet: bør. FR-11, FR-16, NFR-9, UX-DR13, UX-DR15, UX-DR26 (ukjent fil).*

**Akseptansekriterier:**

**Gitt** Notatsiden
**Når** den vises
**Så** står alle notatets quizer med nyeste øverst, hver med nivå, antall spørsmål, dato og KI-merket med modellnavnet fra quizen, ikke fra gjeldende innstilling
**Og** under står «Lag ny quiz» med valg av nivå (middels valgt) og antall (10, 5–30)

**Gitt** «Lag ny quiz»
**Når** brukeren velger nivå og antall og trykker «Lag quiz»
**Så** kjøres samme genereringskjede som i story 2.4 med den lagrede filen, og den nye quizen legges til ved siden av de gamle
**Og** samme valg som en eksisterende quiz er lov, og spørsmål kan gå igjen på tvers av quizer

**Gitt** en quiz laget i testmodus fra en fil som ikke er et testdokument
**Når** den vises på Notatsiden
**Så** står merknaden «Testmodus: denne quizen er laget fra et forhåndslagret testdokument, ikke fra filen din.» (`Quiz.forhandslagret`, FR-27)

**Gitt** Notatsiden
**Når** brukeren leter etter en måte å slette en enkelt quiz på
**Så** finnes det ingen, og Tilbake går til emnet (FR-16)

**Gitt** en quiz eller et notat som tilhører en annen bruker
**Når** noen åpner `/notater/<id>/` eller starter «Lag ny quiz» for det
**Så** får hen «Fant ikke siden»

## Epic 3: Ta quiz, se resultat og fyll feilbanken

Studenten tar quizen med svar som lagres underveis, kan fortsette der hen slapp, leverer, ser poengsummen uten fasit, og feilsvarene havner i feilbanken. En levert quiz kan tas på nytt. Etter denne epicen er kjerneløpet notat → quiz → feilbank → lært ferdig.

### Story 3.1: Starte og svare på en quiz

Som student,
vil jeg ta quizen ett spørsmål om gangen og kunne gå frem og tilbake,
slik at jeg kan tenke meg om og endre svar før jeg leverer.

*Prioritet: kjerne. FR-17, FR-18 (lagring underveis), AD-6, AD-7, AD-13, AD-16, AD-17, AD-20, UX-DR10 til UX-DR12, NFR-1, NFR-9.*

**Akseptansekriterier:**

**Gitt** en quiz på Notatsiden
**Når** brukeren trykker «Ta quizen» (POST)
**Så** oppretter `start_eller_fortsett_okt` en `Okt` med `type=forsok`, `status=pabegynt`, `notat` og `quiz`, eller henter den påbegynte økten for quizen hvis den finnes, og brukeren sendes til første ubesvarte spørsmål
**Og** `Okt.innhold` lagrer quizens spørsmål i quizens rekkefølge med alternativene stokket, og listen endres aldri etterpå (AD-16)
**Og** når siste steg i genereringen (story 2.4) har lagret quizen, kaller stegviewet `start_eller_fortsett_okt` for den nye quizen og svarer med `HX-Redirect` til `/okter/<id>/sporsmal/1/` i stedet for å sende brukeren til Notatsiden. Det samme skjer for en annen fane som spør etter at jobben er ferdig, og den får den samme økten. Stegendepunktet er en POST, så ingen GET endrer data. Dette avklarer antakelse 1 i EXPERIENCE.md

**Gitt** `/okter/<id>/sporsmal/<nr>/`
**Når** siden vises
**Så** står «Spørsmål N av M» med en 8 px fremdriftsstolpe og KI-merket med modellen fra quizen, spørsmålet som `<legend>` og tre radioknapper i `<label>` på minst 56 px i rekkefølgen fra `Okt.innhold`
**Og** et svar som alt er lagret, er valgt
**Og** spørsmål og alternativer har `lang="{{ quiz.sprak }}"` når språket ikke er norsk, og `<title>` er «Spørsmål N av M – <notat> – FåreQuiz»
**Og** Tilbake går til notatet

**Gitt** et spørsmål
**Når** brukeren trykker Neste eller Forrige i et vanlig POST-skjema, med eller uten valgt svar
**Så** lagrer `services.okter.lagre_svar` svaret med `update_or_create` på (`okt`, `sporsmal`) og oppdaterer `sist_endret`, og brukeren sendes til neste eller forrige spørsmål
**Og** det virker uten JavaScript. HTMX kan legges på, men treffer samme endepunkt, og en mislykket lagring viser «Svaret ble ikke lagret. Sjekk nettet og prøv igjen.» ved knappen, mens brukeren blir på samme spørsmål (AD-13)
**Og** på siste spørsmål er Neste byttet ut med Lever

**Gitt** `lagre_svar`
**Når** økten er levert, spørsmålet ikke står i `okt.innhold`, eller alternativet hører til et annet spørsmål
**Så** avvises svaret, og ingenting lagres. Et forsøk på å svare i en levert økt sender brukeren til resultatsiden (AD-17)

**Gitt** malen for Quiz
**Når** den vises
**Så** sendes verken `er_riktig` eller `begrunnelse` til malen, og en test sjekker at HTML-en ikke skiller ut det riktige alternativet med klasse, dataattributt eller rekkefølge (AD-20)

**Gitt** en økt som tilhører en annen bruker
**Når** noen åpner eller sender svar til `/okter/<id>/sporsmal/<nr>/`
**Så** får hen «Fant ikke siden», også når `alternativ`-ID-en i POST tilhører en annen bruker (AD-8)
**Og** quizsiden kan brukes med tastatur alene, med piltaster i radiogruppen, og ved 360 px uten vannrett rulling (NFR-1)

### Story 3.2: Regelen for feilbanken

Som student,
vil jeg at spørsmål jeg svarer feil på, havner i feilbanken og blir der til jeg har svart riktig to ganger på rad,
slik at jeg øver på det jeg faktisk ikke kan.

*Prioritet: kjerne. FR-21, FR-23 (regelen), AD-2, AD-3, AD-5. Bare tjenestelag og tester.*

**Akseptansekriterier:**

**Gitt** et spørsmål uten `Feilbankrad`
**Når** `services.feilbank.registrer_svar(sporsmal, riktig=False)` kalles
**Så** opprettes raden med `get_or_create` og telleren 0, og funksjonen returnerer `lagt_i`
**Og** med `riktig=True` skjer ingenting, og den returnerer `ingen`

**Gitt** et spørsmål i feilbanken (`laert_tidspunkt IS NULL`)
**Når** `registrer_svar` kalles med riktig svar
**Så** øker telleren med 1 og funksjonen returnerer `opp`, og ved 2 settes `laert_tidspunkt` og funksjonen returnerer `laert`
**Og** feil svar nullstiller telleren og returnerer `nullstilt`

**Gitt** et lært spørsmål
**Når** `registrer_svar` kalles med feil svar
**Så** åpnes den samme raden igjen med `laert_tidspunkt=None` og telleren 0, og funksjonen returnerer `nullstilt`
**Og** det finnes aldri mer enn én `Feilbankrad` per spørsmål, og ingen rad slettes (AD-3)

**Gitt** to quizer om samme notat med et spørsmål med lik tekst
**Når** spørsmålet i quiz 1 besvares feil
**Så** påvirkes ikke spørsmålet i quiz 2 (AD-5, TF-3)

**Gitt** kodebasen
**Når** den sjekkes
**Så** er `registrer_svar` eneste sted som oppretter eller endrer `Feilbankrad`, og tester dekker alle fem hendelsene og sekvensen feil → riktig → feil → riktig → riktig

### Story 3.3: Levere og se resultatet

Som student,
vil jeg levere quizen og se poengsummen og hvilke svar som var feil,
slik at jeg vet hvor jeg står uten at fasiten gjør det for lett.

*Prioritet: kjerne. FR-17, FR-19, FR-21, AD-2, AD-18, AD-20, UX-DR19, UX-DR20.*

**Akseptansekriterier:**

**Gitt** en påbegynt økt der alle spørsmålene er besvart
**Når** brukeren trykker Lever
**Så** kjører `services.okter.lever_okt` i én `transaction.atomic`: først `filter(pk, status="pabegynt").update(status="levert", levert_tidspunkt=now())`, deretter `registrer_svar` for hvert spørsmål i `okt.innhold`, lagring av `Svar.hendelse`, `poengsum` og `antall`
**Og** brukeren sendes til `/okter/<id>/resultat/`

**Gitt** en påbegynt økt med ubesvarte spørsmål
**Når** brukeren trykker Lever
**Så** leveres ingenting, og «Du har ikke svart på alle spørsmålene. Disse mangler: spørsmål 4, spørsmål 7.» vises ved Lever med `role="alert"` og lenker til spørsmålene

**Gitt** en økt som alt er levert
**Når** Lever sendes igjen fra dobbeltklikk eller en annen fane
**Så** endrer `lever_okt` ingenting mer, feilbanken teller ikke dobbelt, og brukeren sendes til resultatsiden (AD-18)

**Gitt** resultatsiden
**Når** den vises
**Så** står poengkortet med «7 av 10» i 56 px og «riktige svar» med `role="status"`, og én resultatrad per spørsmål med «✓ Riktig» eller «✗ Feil» og spørsmålsnummer
**Og** fasiten vises ikke for feil svar, og fasit og begrunnelse vises bare for spørsmål der `fasit_synlig(sporsmal)` er sann (AD-20)
**Og** hendelsene leses fra `Svar.hendelse`, ikke regnet ut på nytt, og teksten er «N spørsmål er lagt i feilbanken. Øv på dem til du kan dem.» når N > 0
**Og** Tilbake går til notatet

**Gitt** et levert forsøk
**Når** brukeren ser på feilbanken og påbegynte forsøk
**Så** ligger hvert feilbesvarte spørsmål i notatets feilbank høyst én gang, mens et påbegynt forsøk aldri har påvirket feilbanken (FR-18, FR-21)

**Gitt** en økt som tilhører en annen bruker
**Når** noen sender Lever eller åpner resultatsiden for den
**Så** får hen «Fant ikke siden»

### Story 3.4: Ta en quiz på nytt

Som student,
vil jeg ta en quiz jeg har levert, på nytt,
slik at jeg kan se om jeg har blitt bedre og jobbe meg ut av feilbanken.

*Prioritet: kjerne (flyttet fra bør 20.11: eneste vei til «lært» i kjernen hvis Epic 4 kuttes). FR-20, FR-23 (nye forsøk teller), AD-6.*

**Akseptansekriterier:**

**Gitt** en quiz med minst ett levert forsøk og ingen påbegynte
**Når** brukeren trykker «Ta på nytt» på Notatsiden eller resultatsiden
**Så** opprettes et nytt forsøk med alternativene stokket på nytt, og de gamle forsøkene er uendret

**Gitt** et spørsmål i feilbanken
**Når** det besvares riktig i to leverte forsøk på rad på den opprinnelige quizen
**Så** blir det lært, og resultatsiden viser fasiten for det (FR-23)

**Gitt** en quiz med et påbegynt forsøk
**Når** brukeren starter quizen igjen
**Så** fortsetter hen det påbegynte forsøket, og det finnes aldri mer enn ett påbegynt forsøk per quiz (betinget `UniqueConstraint`, FR-18)

### Story 3.5: Fortsette der jeg slapp

Som student,
vil jeg se påbegynte quizer og fortsette fra spørsmålet jeg kom til, også på en annen enhet,
slik at jeg kan øve i små pauser.

*Prioritet: bør (fra annen enhet: kan kuttes, men følger med fordi svarene ligger på serveren). FR-18, AD-6, AD-16, UX-DR9, UX-DR14.*

**Akseptansekriterier:**

**Gitt** et påbegynt forsøk med 5 av 10 besvart
**Når** Notatsiden vises
**Så** har quizen den gule merkelappen «Påbegynt 5/10», og knappen heter «Fortsett» i stedet for «Ta på nytt»

**Gitt** påbegynte økter
**Når** Mine emner vises
**Så** står boksen «Fortsett der du slapp» nederst med én rad per påbegynt økt, nyeste først etter `sist_endret`, med tekst som «Webutvikling › HTML · Middels · 5 av 10 besvart»
**Og** hver rad lenker til første ubesvarte spørsmål, og menyen får *Fortsett der du slapp*
**Og** uten påbegynte økter vises ikke boksen

**Gitt** at brukeren lukker fanen etter å ha svart på halvparten
**Når** hen logger inn fra en annen nettleser og trykker på raden
**Så** åpnes første ubesvarte spørsmål med de tidligere svarene lagret, og Tilbake går til notatet

**Gitt** et påbegynt forsøk
**Når** feilbanken og historikken sjekkes
**Så** har forsøket ikke påvirket feilbanken, og det står ikke i historikken

## Epic 4: Øv på feil til det sitter

Studenten øver på feilbanken i oransje øvemodus, ser «Lært! ✓» med fasit og begrunnelse, og kan melde et spørsmål som feil. Epicen bruker de samme `Okt`-tjenestene som Epic 3, med `type=oving`.

### Story 4.1: Øve på feilbanken

Som student,
vil jeg øve på spørsmålene i feilbanken med alternativene i ny rekkefølge,
slik at jeg husker svaret og ikke bare plasseringen.

*Prioritet: bør (ny stokking for hver økt: kan kuttes). FR-22, AD-6, AD-16, AD-20, UX-DR5, UX-DR14, UX-DR21, UX-DR23 (feilbank-raden).*

**Akseptansekriterier:**

**Gitt** et notat med N spørsmål i feilbanken
**Når** Notatsiden vises
**Så** står feilbank-raden «N spørsmål å øve på» med den oransje knappen «Øv på feil»
**Og** med tom feilbank og ingen påbegynt øvingsøkt er knappen låst og viser «Ingen feil å øve på»
**Og** med en påbegynt øvingsøkt heter knappen «Fortsett» og virker selv om feilbanken er blitt tom (AD-16)

**Gitt** «Øv på feil» (POST)
**Når** brukeren trykker på knappen på Notatsiden eller resultatsiden
**Så** oppretter `start_eller_fortsett_okt` en `Okt` med `type=oving`, `notat` satt og `quiz` tom, eller henter den påbegynte øvingsøkten for notatet
**Og** `Okt.innhold` inneholder spørsmålene med åpen `Feilbankrad` når økten opprettes, sortert på når raden ble opprettet, med alternativene stokket på nytt, og listen endres ikke når feilbanken endres senere
**Og** resultatsiden fra story 3.3 får knappen «Øv på feil» når feilbanken ikke er tom

**Gitt** en øvingsøkt
**Når** et spørsmål vises
**Så** brukes samme side og samme skjemaer som i story 3.1, med den oransje merkelappen «Øv på feil», og practice-fargene erstatter primary-fargene i knapper, valgt svar, fremdrift og fokusring
**Og** KI-merket for spørsmålets quiz står over spørsmålet, og verken `er_riktig` eller `begrunnelse` sendes til malen (AD-20)
**Og** Tilbake går til notatet, og påbegynte øvingsøkter står i «Fortsett der du slapp» (story 3.5)

**Gitt** en øvingsøkt
**Når** historikken vises
**Så** står ikke økten der, verken påbegynt eller levert (FR-22)

**Gitt** en øvingsøkt eller et notat som tilhører en annen bruker
**Når** noen starter eller åpner den
**Så** får hen «Fant ikke siden»

### Story 4.2: Levere øvingen og se hva som er lært

Som student,
vil jeg se «Lært! ✓» med fasiten og begrunnelsen når jeg har svart riktig to ganger på rad,
slik at jeg forstår hvorfor svaret er riktig og ser at feilbanken krymper.

*Prioritet: kjerne (visning av fasit når spørsmålet er lært). FR-22, FR-23, AD-2, AD-18, AD-20, UX-DR22, TF-2.*

**Akseptansekriterier:**

**Gitt** en øvingsøkt der alle spørsmålene er besvart
**Når** brukeren trykker Lever
**Så** leveres den med samme `lever_okt` som et forsøk, og `registrer_svar` kjøres for hvert spørsmål, slik at svar i øving og i forsøk teller likt (FR-23)
**Og** ubesvarte spørsmål gir samme melding med lenker som i story 3.3

**Gitt** Øv-resultat
**Når** det vises
**Så** står poengsummen med `role="status"`, og øverst én lært-boks per spørsmål med `hendelse=laert`, med «Lært! ✓», spørsmålet, «Fasit: …» og begrunnelsen
**Og** så følger resultatradene med «✓ Riktig» eller «✗ Feil», og telleren for spørsmål som ennå ikke er lært, for eksempel «1 av 2 riktige på rad»
**Og** fasiten vises ikke for spørsmål som ikke er lært (AD-20)

**Gitt** at feilbanken er tom etter levering
**Når** Øv-resultat vises
**Så** står «Feilbanken er tom. Godt jobba!» og «Tilbake til <notat>»
**Og** lært-boksen er det eneste stedet med en liten feiring, uten lyd og uten animasjon som varer

**Gitt** et lært spørsmål
**Når** det senere besvares feil i et forsøk
**Så** kommer det tilbake i feilbanken med telleren nullstilt, og fasiten er ikke lenger synlig

### Story 4.3: Melde et spørsmål som feil

Som student,
vil jeg melde et spørsmål jeg mener er feil eller uklart,
slik at jeg ikke blir sittende fast med et spørsmål der KI-en har laget feil fasit.

*Prioritet: kan kuttes. FR-31, TF-1. Forutsetter at gruppa først har lagt til regelen i arkitekturen (AD-3, AD-4 og AD-16) og FR-31 i PRD-en.*

**Akseptansekriterier:**

**Gitt** arkitekturen og PRD-en
**Når** storyen startes
**Så** er AD-3, AD-4 og AD-16 oppdatert med at et meldt spørsmål ikke er i feilbanken, ikke telles i dekningsgraden og ikke kommer med i nye økter, og FR-31 står i PRD-en

**Gitt** en resultatrad med «✗ Feil» på Resultat eller Øv-resultat
**Når** brukeren trykker «Meld som feil eller uklart» (POST) og bekrefter på en egen side
**Så** setter en tjeneste `Sporsmal.meldt_tidspunkt` (feltet finnes fra story 1.1, så ingen ny migrering trengs), og raden viser «Meldt som feil»
**Og** fasiten vises fortsatt ikke

**Gitt** et meldt spørsmål
**Når** feilbanken telles eller en ny økt opprettes
**Så** er spørsmålet ikke i feilbanken, og det kommer ikke med i `Okt.innhold` for nye forsøk eller øvingsøkter. Én hjelper, for eksempel `Sporsmal.objects.ikke_meldt()`, brukes alle steder
**Og** i en påbegynt økt der spørsmålet alt står, gir `registrer_svar` `ingen` ved levering
**Og** `Feilbankrad` slettes ikke

**Gitt** et spørsmål i en annen brukers quiz
**Når** noen sender meldingen for det
**Så** får hen «Fant ikke siden», og ingenting endres

## Epic 5: Se progresjonen

Studenten ser dekningsgraden per notat med fordeling per nivå, dekningsgraden per emne, og historikken med alle forsøk. Epicen kan bygges parallelt med Epic 4.

### Story 5.1: Dekningsgrad per notat

Som student,
vil jeg se hvor stor del av stoffet i et notat jeg kan, fordelt på nivå,
slik at jeg vet om jeg må øve mer, særlig på de vanskelige spørsmålene.

*Prioritet: bør. FR-24, AD-4, AD-5, UX-DR8, UX-DR23 (dekningskortet), TF-6.*

**Akseptansekriterier:**

**Gitt** `services.dekningsgrad`
**Når** dekningsgraden for et notat regnes ut
**Så** er et spørsmål dekket når det har minst ett riktig `Svar` i en levert `Okt` (forsøk eller øving) og ingen åpen `Feilbankrad`
**Og** for hvert nivå er andelen dekkede spørsmål av alle spørsmålene på det nivået i notatets quizer, og dekningsgraden er 0,2 × lett + 0,3 × middels + 0,5 × vanskelig som et tall mellom 0 og 1 uten avrunding
**Og** et nivå uten quiz teller som 0, og spørsmål som bare er besvart i påbegynte økter, er ikke dekket
**Og** verdien lagres aldri i databasen, og `services.dekningsgrad` er eneste implementasjon (AD-4)
**Og** hvis story 4.3 er bygget, telles meldte spørsmål ikke med, og den samme hjelperen brukes

**Gitt** testene
**Når** de kjøres
**Så** gir lett 100 %, middels 50 % og vanskelig uten quiz nøyaktig 35 % (FR-24)
**Og** en ny quiz på et nivå gjør at dekningsgraden går ned, og uten quiz på vanskelig blir den aldri over 50 % (TF-6)
**Og** et spørsmål som blir lagt i feilbanken etter å ha vært dekket, er ikke lenger dekket

**Gitt** Notatsiden
**Når** den vises
**Så** står dekningskortet øverst med «Dekningsgrad for <notat>», tallet avrundet til hele prosent i malen og stolpen med prosenttallet ved siden av
**Og** under står tre nivåbokser «Lett · 20 %», «Middels · 30 %» og «Vanskelig · 50 %» med resultatet for hvert nivå, eller «Ingen quiz» for nivå uten quiz
**Og** en kort hjelpetekst forklarer at dekningsgraden kan gå ned når en ny quiz lages, og at quiz på vanskelig trengs for å komme over 50 % **[ordlyd ikke bestemt]**

**Gitt** et nytt levert forsøk eller en levert øvingsøkt
**Når** Notatsiden vises igjen
**Så** er dekningsgraden oppdatert uten at noe er lagret

### Story 5.2: Dekningsgrad per emne

Som student,
vil jeg se dekningsgraden for hvert emne og hvert notat i emnet,
slik at jeg ser hva som gjenstår før eksamen.

*Prioritet: kan kuttes. FR-25, AD-4, UX-DR7, UX-DR8.*

**Akseptansekriterier:**

**Gitt** et emne med notater
**Når** dekningsgraden for emnet regnes ut i `services.dekningsgrad`
**Så** er den snittet av dekningsgraden til notatene som har minst én quiz, uavhengig av hvor lange notatene er
**Og** to notater med 80 % og 40 % gir 60 %, og et tredje notat uten quiz endrer ikke snittet (tester)
**Og** et emne uten notater, eller der ingen notater har quiz, har ingen dekningsgrad

**Gitt** Emnesiden
**Når** den vises
**Så** står dekningskortet med «Dekningsgrad for <emne>», eller «Ingen dekningsgrad», og hver notatrad har stolpe og prosenttall
**Og** et notat uten quiz viser «Ingen quiz» i stedet for stolpen

**Gitt** Mine emner
**Når** den vises
**Så** har hver emnerad stolpe og prosenttall, eller «Ingen dekningsgrad»
**Og** siden lastes uten én databasespørring per spørsmål, slik at den er rask også for testbrukeren

### Story 5.3: Historikk per notat

Som student,
vil jeg se alle forsøkene mine på et notat med dato, quiz og poengsum,
slik at jeg ser om jeg blir bedre.

*Prioritet: bør. FR-26, AD-6, UX-DR23 (historikktabellen), NFR-1.*

**Akseptansekriterier:**

**Gitt** et notat med leverte forsøk
**Når** Notatsiden vises
**Så** står historikktabellen nederst med kolonnene Dato, Quiz og Poengsum, én rad per forsøk med `type=forsok` og `status=levert`, sortert med nyeste `levert_tidspunkt` øverst
**Og** datoen vises i `Europe/Oslo`, quizen med nivå og antall, og poengsummen som «7 av 10»
**Og** hver rad lenker til resultatsiden for forsøket

**Gitt** påbegynte forsøk og øvingsøkter
**Når** historikken vises
**Så** står de ikke i tabellen (FR-18, FR-22)

**Gitt** et notat uten leverte forsøk
**Når** Notatsiden vises
**Så** står «Ingen forsøk ennå» i stedet for tabellen

**Gitt** en skjerm på 360 px
**Når** historikken vises
**Så** er det ingen vannrett rulling, og tabellen har `<th scope="col">` for skjermleser (NFR-1, NFR-8)

## Epic 6: Klar for sensor

Sensor kloner repoet, følger README-en, logger inn som testbrukeren med ferdige data og kjører hele kjerneflyten uten nøkkel. Epicen har også sluttkontroll av tilgang, universell utforming og KI-kvalitet, og brukertesten.

### Story 6.1: Testbruker med eksempeldata

Som sensor,
vil jeg logge inn som en testbruker som alt har emner, quizer, forsøk og en feilbank,
slik at jeg ser dekningsgrad, historikk og «Fortsett der du slapp» med en gang.

*Prioritet: kjerne. FR-28, AD-21.*

**Akseptansekriterier:**

**Gitt** en tom database etter `migrate`
**Når** `python manage.py seed_testdata` kjøres
**Så** kjører kommandoen i `ki.tving_testmodus()`, gjør ingen nettverkskall og lager testbrukeren med e-posten og passordet som står i README-en
**Og** testbrukeren har emnet «Webutvikling» med minst tre notater fra `testdokumenter/`, quizer på minst to nivåer, leverte forsøk, en feilbank med minst ett spørsmål som er lært og ett som ikke er det, og ett påbegynt forsøk

**Gitt** seed-kommandoen
**Når** koden sjekkes
**Så** bruker den bare tjenestene `last_opp`, `generering.generer_synkront`, `lagre_svar` og `lever_okt` med faste svar, og skriver aldri rett til modellene (AD-1)

**Gitt** at testbrukeren alt finnes
**Når** `seed_testdata` kjøres igjen
**Så** slettes emnene hens med `slett_emne`, dataene lages på nytt, og resultatet er det samme som første gang

**Gitt** testbrukeren
**Når** sensor logger inn
**Så** viser Mine emner emnet med dekningsgrad og «Fortsett der du slapp», og Notatsiden viser fordeling per nivå, quizer med KI-merke, feilbank og historikk
**Og** en test kjører `seed_testdata` to ganger og sjekker antallet av hver ting

### Story 6.2: README og test med ny klone

Som sensor,
vil jeg kunne installere og kjøre appen med README-en alene,
slik at jeg kan vurdere hele appen uten hjelp fra gruppa og uten API-nøkkel.

*Prioritet: kjerne. FR-29, FR-30, AD-22, SM-1.*

**Akseptansekriterier:**

**Gitt** README-en
**Når** den leses
**Så** beskriver den kort hva appen gjør, hva som trengs (Python 3.14 og uv, eller pip), og nøyaktig stegene `uv sync` (eller `pip install -r requirements.txt`), `python manage.py migrate`, `python manage.py seed_testdata` og `python manage.py runserver`
**Og** den oppgir testbrukerens e-post og passord, at testmodus er på uten `.env`, og hva testmodus-stripen betyr
**Og** den forklarer hvordan sensor kopierer `.env.example` til `.env`, legger inn sin egen Anthropic-nøkkel og slår av testmodus for å teste med ekte modell, og at `KI_MODELL` kan byttes
**Og** den forklarer hvordan `ALLOWED_HOSTS` utvides for å teste fra mobil på samme nett, og at dette ikke er hosting

**Gitt** en ny klone på en maskin som ikke har vært brukt i prosjektet, uten `.env` og uten nøkkel
**Når** en i gruppa som ikke skrev README-en, følger den ordrett på Windows og på macOS eller Linux
**Så** kan hen logge inn som testbrukeren, laste opp et testdokument, ta quizen, levere, øve på feil og se dekningsgraden endre seg
**Og** avvik mellom README og virkelighet rettes i README-en eller koden, og testen dokumenteres i sesjonsloggen

**Gitt** CI
**Når** en pull request kjøres
**Så** kjører CI også `migrate` og `seed_testdata` på en tom database, slik at en ødelagt seed stopper merge

### Story 6.3: Sluttkontroll av tilgang og universell utforming

Som sensor og som student med nedsatt funksjonsevne,
vil jeg at ingen kan se andres data, og at hele appen virker med tastatur og skjermleser,
slik at appen er trygg og tilgjengelig for alle.

*Prioritet: kjerne. FR-3, NFR-1, NFR-2, NFR-8, NFR-9, SM-5, SM-7, SM-8.*

**Akseptansekriterier:**

**Gitt** alle URL-er med ID i `urls.py`
**Når** tilgangstesten kjører
**Så** prøver den hver URL med GET og POST som en annen bruker og får 404 hver gang, og testen feiler hvis en ny URL med ID ikke er med (SM-5)
**Og** alle sider unntatt Logg inn og Registrer sender en utlogget bruker til Logg inn

**Gitt** alle sider i appen, med testbrukerens data og i hver tilstand fra EXPERIENCE.md (tom, påbegynt, feil, ventepanel, resultat, øving)
**Når** axe kjøres mot dem
**Så** finnes ingen brudd på WCAG 2.2 A eller AA, og resultatet dokumenteres med dato og verktøyversjon (SM-7)

**Gitt** kjerneflyten: registrere, logge inn, opprette emne, laste opp, lage quiz, svare, levere og øve på feil
**Når** en i gruppa gjør den med bare tastatur og deretter med skjermleser (NVDA eller VoiceOver)
**Så** er fokus alltid synlig og skjules aldri, ventepanelets steg og poengsummen leses opp som statusmeldinger, og feilmeldinger leses opp
**Og** sidene virker ved 320 px bredde og 200 % tekst uten vannrett rulling (NFR-1)
**Og** funn rettes eller føres som åpne punkter med begrunnelse

**Gitt** alle sider som viser en quiz
**Når** de sjekkes
**Så** har Notatsiden, Quiz og Øv på feil KI-merket med modellnavnet fra quizen, også i testmodus (SM-8)

### Story 6.4: KI-kvalitet og genereringstid

Som faglærer og sensor,
vil jeg se dokumentert at quizene fra modellen er gode nok og lages innen tidsgrensen,
slik at jeg kan stole på at appen hjelper studenten å lære.

*Prioritet: kjerne. FR-9, FR-12, FR-15, NFR-7, SM-2, SM-4, PRD kap. 9 spørsmål 1 og 3.*

**Akseptansekriterier:**

**Gitt** de fem testdokumentene og en API-nøkkel
**Når** gruppa kjører dem mot ekte modell på alle tre nivåer
**Så** har alle quizene nøyaktig det valgte antallet spørsmål, tre ulike alternativer, ett riktig svar og ingen like spørsmål (SM-4)
**Og** spørsmålene er på samme språk som notatet, og `Quiz.sprak` stemmer med språket (FR-12, NFR-6). Minst ett testdokument er på et annet språk enn norsk (story 2.1)
**Og** gruppa vurderer hvert spørsmål manuelt, og minst 90 % er relevante, har riktig fasit og er ikke tvetydige (SM-2)
**Og** resultatet dokumenteres med modell, dato, `PROMPT_VERSJON` og eksempler på dårlige spørsmål

**Gitt** en generering av 30 spørsmål fra tekst-PDF-en
**Når** tiden måles flere ganger
**Så** dokumenteres typisk og lengste tid, og `effort` settes slik at genereringen holder seg godt under 120 sekunder. Går det ikke, foreslår gruppa en endring i PRD-en
**Og** valget mellom hel PDF og uttrukket tekst, og mellom Sonnet og Haiku, dokumenteres med begrunnelse

**Gitt** at prompt, skjema eller `effort` endres
**Når** endringen merges
**Så** er `PROMPT_VERSJON` økt, og mock-svarene er laget på nytt med `lag_mocksvar` hvis skjemaet er endret

### Story 6.5: Brukertest med medstudenter

Som gruppe,
vil vi la 3–5 medstudenter teste appen,
slik at vi finner problemene vi selv er blinde for før leveringen.

*Prioritet: bør. SM-6, NFR-1, FR-18.*

**Akseptansekriterier:**

**Gitt** appen kjørt lokalt med testmodus eller ekte modell
**Når** 3–5 medstudenter får oppgaver fra UJ-1 til UJ-3 uten hjelp
**Så** noterer gruppa hvor de stopper, hva de misforstår og hva de sier
**Og** minst én av dem tar et påbegynt forsøk videre på mobil (FR-18, NFR-1)

**Gitt** funnene
**Når** de er samlet
**Så** er de dokumentert med alvorlighet, og hvert funn er enten rettet eller ført som åpent punkt med begrunnelse
