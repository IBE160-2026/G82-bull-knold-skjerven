# Sluttkontroll 6.3: tilgang og universell utforming

Story 6.3, spec `spec-6-3-sluttkontroll-av-tilgang-og-universell-utforming.md`. Krav: SM-5, SM-7, SM-8, FR-2, FR-3, NFR-1, NFR-2, NFR-8, NFR-9.

## 1. Tilgang (SM-5, FR-2)

Testene står i `studier/tests/test_tilgang_urler.py` og kjøres med vanlig `uv run python manage.py test`.

- `UrlTilgangTest` leser alle URL-mønstrene fra `get_resolver()`. Et mønster med ID som mangler i `OPPSETT`, gir feil med navnet på mønsteret, for eksempel `studier:ny_side`. Det er prøvd ved å legge til et mønster midlertidig.
- Kari er innlogget og har godtatt vilkårene. Hun sender GET og POST med Olas ID-er til alle 13 mønstrene med ID. Metodene viewet tar imot, gir 404 med «Fant ikke siden» (S14). Hele databasen (alle rader i `kontoer` og `studier`, med tidsstempler) er lik før og etter hver forespørsel. POST-dataene er gyldige der det går, så et hull ville gitt en endring.
- `test_ola_far_ikke_404_for_egne_id_er` viser at oppsettet peker på objekter som finnes, så 404-en for Kari skyldes eieren og ikke en feil ID.
- `InnloggingTest`: utlogget gir Logg inn, Registrer og Personvern (S15) 200. Alle andre mønstre, også med gyldige ID-er, gir 302 til Logg inn med `next` lik stien.

**Avvik fra «404 hver gang» (beslutning 26.11):** en metode viewet ikke tar imot (for eksempel GET på `/notater/<id>/ov/` eller POST på `/emner/<id>/`), gir 405. Det skjer før ID-en slås opp, så svaret er det samme for en annens ID og for en ID som ikke finnes, og det avslører ikke at data finnes. Testen sjekker at statuskoden er den samme som for ID 999999.

**Merknad, ikke endret:** `/jobber/<id>/steg/` gir 200 med et sluttfragment når jobben ikke finnes (for eksempel slettet med notatet), og 404 når den finnes og er en annens (`hent_egen_eller_none`). Forskjellen viser at en jobb-ID finnes, men ingen data fra jobben. ID-ene er fortløpende tall, så det sier ikke mer enn ID-en selv. Tilgangsmodellen er derfor ikke endret (spec: «Ikke endre tilgangsmodellen med mindre testen avslører et hull»).

## 2. KI-merket (SM-8, NFR-9)

`studier/tests/test_ki_merke.py`: en quiz med `modell="claude-haiku-5-5"` viser «Laget av KI» og «Claude Haiku 5.5» på S7 (notatsiden), S9 (Ta quiz) og S12 (Øv på feil), i testmodus og med testmodus-banneret. På S9 og S12 står hele teksten «Laget av KI (Claude Haiku 5.5)».

## 3. axe (SM-7)

| | |
|---|---|
| Dato | 26.11.2026 |
| axe-core | 4.14.0 (fra `axe-playwright-python` 0.1.9, ingen nettverkskall) |
| Nettleser | Chromium 159.0.8154.6 (headless), Playwright for Python 1.65.2 |
| Tagger | `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa` |
| Test | `farequiz/tests_axe.py`, `uv run python manage.py test --tag nettleser` |
| Resultat | **0 brudd** i alle 44 tilstander, 39 på 1280 × 720 og 5 på 320 × 640 |

Testen kjører med `DEBUG=False`, så S14 er den ekte 404-siden. Tilstandene med data bruker `seed_testdata` (testbrukeren). Testen kjører også i et eget CI-steg, så et nytt brudd stopper merge. Mangler Playwright, axe-playwright-python eller Chromium, feiler testen i stedet for å hoppes over. Den skriver versjonene av axe-core og Chromium når den er ferdig.

### Tilstander som er dekket

| Skjermbilde | Tilstander |
|---|---|
| S1 Logg inn | tom, feil innlogging, økt utløpt (`?next=`) |
| S1b Vilkår | bruker som ikke har godtatt vilkårene |
| S2 Registrer | tom, feil (for kort passord) |
| S3 Oversikt | ny bruker uten emner, testbrukeren (emnekort og «Fortsett der du slapp»), menyen åpen |
| S4 Emne | uten notater, med notater, tomt navn i «Gi nytt navn» |
| S5 Vilkår (kort) | første opplasting |
| S6 Last opp | tom, avvist fil i nettleseren (`.exe`), avvist fil på serveren (falsk PDF) |
| S6b | opplasting pågår (svaret holdes tilbake med `page.route`) |
| S6c | opplasting avbrutt (forespørselen avbrytes med `page.route`) |
| S7 Notat | uten quiz, med quizer, historikk og påbegynt forsøk |
| S8 Generering | pågår (steget holdes tilbake), timeout, feil format, ingen kontakt med serveren (500 fra steget) |
| S9 Ta quiz | spørsmål, spørsmål på engelsk (quiz fra `javascript-og-dom.txt`, `lang="en"`), «Svaret ble ikke lagret» |
| S10 Se over og lever | ikke alle besvart, «Lever» med manglende svar (alert) |
| S11 Resultat | levert forsøk med feil svar |
| Meld som feil | bekreftelsen |
| S12 Øv på feil | spørsmål, resultat |
| S13 Slett emne | bekreftelsen |
| S14 Fant ikke siden | innlogget, ukjent ID |
| S15 Personvern | utlogget, innlogget |
| S16 Nytt emne | tom, tomt navn. S16 er testet slik siden er, uten filer (UX-DR34 er utsatt). |
| 320 × 640 (mobil) | S1, S3 testbrukeren med menyen åpen, S7 med quizer, S9 spørsmål, S11 resultat. Her sjekkes også `target-size` (WCAG 2.5.8) i mobiloppsettet. Ingen brudd, så ingen maler eller CSS er endret. |

En egen test legger et bilde uten `alt` inn på S1 og viser at testen da feiler med regelen (`image-alt`), selectoren og URL-en.

### Unntak og begrensninger

- **Ingen regler er slått av** (`disableRules` brukes ikke).
- **Kartet bak siden tas bort mens axe kjører.** `.kart-bakgrunn` har kartet (`static/img/kart.svg`) som bakgrunnsbilde. Over et bakgrunnsbilde kan ikke axe regne ut kontrasten, og da ble `color-contrast` «incomplete» for nesten all tekst. Kartet er dekorativt, så testen legger inn `background-image: none` før axe kjører, og kontrasten måles mot sidefargen `#EFE6D8`. Linjene i kartet (`#DFD2BE`, 1,5 px) er sjekket for seg:

  | Tekstfarge | Mot linjene `#DFD2BE` | Mot sidefargen `#EFE6D8` |
  |---|---|---|
  | ink `#2B1D14` | 10,94:1 | 13,18:1 |
  | ink-secondary `#5E4636` | 5,86:1 | 7,06:1 |
  | accent-strong `#5C3A21` | 6,77:1 | 8,15:1 |
  | success `#3F624D` | 4,60:1 | 5,54:1 |
  | **error `#A34420`** | **4,14:1** | 4,99:1 |

  Feilteksten (`text-error`) er under 4,5:1 der en kartlinje går rett bak bokstavene. Det gjelder feilmeldinger som står rett på siden og ikke på et kort, for eksempel på S6, S9, S10 og S16, og lenken «Slett emne» på S4. Se åpent punkt 1.
- **Igjen som «incomplete»:** ikonene ✓, ✕ og … på S8, S11 og S12. De er `aria-hidden`, og teksten ved siden av («Riktig», «Feil», «(pågår)») har samme informasjon. axe kan ikke avgjøre kontrasten for ett tegn. De sjekkes i den manuelle kontrollen.
- axe finner ikke alt. Fokusrekkefølge, at fokus flyttes riktig, opplesing og reflow må sjekkes manuelt (se under).

### Åpne punkter

1. **Kontrast for feiltekst over kartlinjene (WCAG 1.4.3).** `--color-error` `#A34420` gir 4,14:1 mot kartlinjene. Forslag: endre tokenet til `#963D1C`, som gir 4,73:1 mot linjene, 5,70:1 mot sidefargen og 6,59:1 mot `surface`. Det er en endring i DESIGN.md, `static/css/input.css` og `app.css` (bygg med `sh scripts/bygg-css.sh`), så gruppa bestemmer. Alternativet er en bakgrunn (`bg-surface`) på feilmeldingene som står rett på siden. Ikke rettet i 6.3, fordi axe ikke melder det og spec-en bare retter brudd axe finner.

## 4. Manuell kontroll (NFR-1, NFR-2, NFR-8)

Gjøres av en i gruppa, i testmodus med testbrukeren (`sensor@farequiz.no` / `sensor123`) etter `seed_testdata`. Kjerneflyten er UJ-1: logg inn → S3 → emnet → last opp et testdokument → lag quiz (S8) → ta quizen (S9) → se over og lever (S10) → resultat (S11) → Øv på feil (S12). Funn rettes eller føres som åpne punkter med begrunnelse i `.logs/<bruker>/issues.md`.

| | |
|---|---|
| Utført av | |
| Dato | |
| Nettleser og skjermleser (versjon) | |
| Enhet og operativsystem | |

| # | Sjekk | OK / funn | Merknad |
|---|---|---|---|
| 1 | Hele kjerneflyten kan gjøres med bare tastatur (Tab, Shift+Tab, Enter, mellomrom, piltaster i radiogruppen), uten mus | | |
| 2 | Hele kjerneflyten med NVDA (Windows) eller VoiceOver (macOS eller iOS) | | |
| 3 | Synlig fokus på alle lenker, knapper, felt og menyen, også i toppfeltet (mørk bakgrunn) | | |
| 4 | «Hopp til innhold» vises ved første Tab og flytter fokus til innholdet | | |
| 5 | S8: hvert steg («Leser filen», «Lager spørsmål», «Sjekker quizen») leses opp som statusmelding, uten at de samme stegene leses på nytt | | |
| 6 | S8: timeout og feil leses opp, og «Prøv igjen» kan nås med tastatur | | |
| 7 | S6b: fremdriften leses opp i steg på 10 %, og S6c leses opp og får fokus | | |
| 8 | S11 og S12: poengsummen leses opp som status | | |
| 9 | S1b: fokus starter i vilkårene, holder seg der til de er godtatt, og Esc lukker ikke | | |
| 10 | Feilmeldinger leses opp og får fokus: S1 feil innlogging, S2 feil, S6 avvist fil og ingen fil, S16 og S4 tomt navn, S9 svaret ble ikke lagret, S10 manglende svar | | |
| 11 | S9 og S12: KI-merket leses før spørsmålet, spørsmålet er `legend`, og fokus flyttes til spørsmålet etter «Neste» | | |
| 12 | S9: lag først en quiz på `javascript-og-dom.txt` (seed lager ingen quiz på den). Spørsmålene er på engelsk og skal leses med engelsk uttale (`lang`) | | |
| 13 | 320 px bredde: ingen vannrett rulling på S1–S16 | | |
| 14 | 200 % tekststørrelse (bare tekst, ikke zoom av hele siden): ingen vannrett rulling og ingen tekst som blir borte | | |
| 15 | Ikonene ✓, ✕ og … på S8, S11 og S12 har tekst ved siden av, og kontrasten er god nok (se «incomplete» over) | | |
| 16 | Feiltekst over kartlinjene (åpent punkt 1): vurder om den er lesbar, eller om tokenet bør endres | | |

### Funn fra den manuelle kontrollen

| # | Skjermbilde | Funn | Alvorlighet | Rettet / åpent punkt |
|---|---|---|---|---|
| | | | | |
