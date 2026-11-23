---
title: 'Avstemming: arkitektur-spine mot PRD, addendum, faglærers tilbakemelding og UX'
reviewed: ../ARCHITECTURE-SPINE.md
created: '2026-11-15'
type: review
sources:
  - ../../../prds/prd-G82-bull-knold-skjerven-2026-11-11/prd.md
  - ../../../prds/prd-G82-bull-knold-skjerven-2026-11-11/addendum.md
  - ../../../prds/prd-G82-bull-knold-skjerven-2026-11-11/tilbakemelding-prd.md
  - ../../../ux-designs/ux-G82-bull-knold-skjerven-2026-11-15-christian/EXPERIENCE.md
  - ../../../ux-designs/ux-G82-bull-knold-skjerven-2026-11-15-christian/DESIGN.md
---

# Avstemming av arkitektur-spinen mot kildene

## Konklusjon

Spinen dekker kjerneløpet godt: lagdeling, feilbankregelen, dekningsgrad, eiersjekk, KI-adapter og testmodus er tydelige og stemmer med kildene. Hullene ligger hovedsakelig i `Okt`. UX og FR-18 krever mer av den enn spinen sier: en entydig eierkjede, posisjon og tidsstempler, et frosset spørsmålssett og levering som bare kan skje én gang. I tillegg har noen stille krav ikke landet: modellnavn i KI-merket i testmodus, notatets språk for `lang`, og hva seed-kommandoen må lage.

Gjennomgangen tar bare med funn som krever en arkitekturbeslutning, en regel eller en konvensjon. Rene UI-detaljer er utelatt med vilje.

**Alvorlighet:** **Høy** betyr at utviklere vil gjøre det ulikt eller bygge feil data hvis det ikke avklares før første migrering. **Middels** betyr et krav i kildene som ikke har noe hjem i spinen. **Lav** betyr en konvensjon eller presisering.

| ID | Alvorlighet | Tema | Forslag |
| --- | --- | --- | --- |
| F-01 | Høy | `Okt`: eierkjede, posisjon og tidsstempler («Fortsett der du slapp») | Endre AD-6 og AD-8, utvid URL-konvensjonen |
| F-02 | Høy | Spørsmålssettet i en øvingsøkt fryses ikke | Endre AD-7 |
| F-03 | Høy | Levering kan skje to ganger, fra to faner eller to enheter | Endre AD-2 |
| F-04 | Middels | KI-merket: modellnavn og prompt-versjon i testmodus og seed | Endre AD-11 og AD-12 |
| F-05 | Middels | Notatets språk for `lang` (WCAG 3.1.2, NFR-6) | Endre AD-11, ny konvensjon |
| F-06 | Middels | Resultatdata: «Lært! ✓» og «lagt i feilbanken» | Endre AD-2 |
| F-07 | Middels | Fasit som skjult informasjon er ingen invariant | Ny regel (AD-16 eller i AD-7) |
| F-08 | Middels | Seed: påbegynt forsøk, filer på disk, alltid mock | Endre AD-12, ny regel for seed |
| F-09 | Middels | Ingen vei til å lage mock-svarene, og SM-2 mangler verktøy | Ny konvensjon eller AD, beslutning om `begrunnelse` |
| F-10 | Middels | Mobil og annen enhet passer ikke med «bare lokal maskin» | Konvensjon og endret driftsdiagram |
| F-11 | Middels | Notat uten quiz trekker ned emnets dekningsgrad for alltid | Endre AD-4, meld til PRD |
| F-12 | Lav | «Lagring feiler» krever HTMX-feilhåndtering | Konvensjon i AD-13 |
| F-13 | Lav | Lange PDF-er og modellgrenser mot FR-8 «uansett sideantall» | Endre AD-10 eller Utsatt med mapping |
| F-14 | Lav | NFR-3 og ikke-mål: filer serveres aldri, ingen Files API | Regel i AD-14 eller AD-11 |
| F-15 | Lav | htmx må ligge lokalt, og CSRF for HTMX | Strukturfrø og konvensjon |
| F-16 | Lav | `DEBUG`, «Ikke funnet»-tilstanden og statiske filer | Konvensjon |
| F-17 | Lav | Konto: passordregler, e-post og innloggingsmelding | Presisering i AD-15 |
| F-18 | Lav | Tone og ordlyd har ikke noe hjem | Konvensjon |
| F-19 | Lav | Avrunding av dekningsgrad | Konvensjon |
| F-20 | Lav | Tilbake, brødsmuler og sidetittel trenger samme forelderdata | Konvensjon |
| F-21 | Lav | Genereringskjeden: tilstand mellom steg, transaksjoner, ny innlasting | Presisering i AD-9 |
| F-22 | Lav | Testkonvensjoner for SM-3, SM-4 og SM-5 | Konvensjon |
| F-23 | Lav | Mindre motsigelser og hull inne i spinen | Små rettelser |

---

## Funn

### F-01 – `Okt`: eierkjede, posisjon og tidsstempler

- **Alvorlighet:** Høy
- **Kilde:** EXPERIENCE.md: Information Architecture (Quiz og Øv på feil nås fra «Fortsett der du slapp»), Component Patterns (Fortsett-boks: «nyeste først», «Hver rad lenker rett til spørsmålet studenten kom til»; Forrige/Neste: «Det går an å gå videre uten å svare»; Feilmelding: «Lenker i meldingen hopper rett til … spørsmålet»), Key Flows UJ-3 («havner rett på spørsmål 6»). PRD FR-18 og FR-26 (dato). Spinen: AD-6 og AD-8.
- **Hva mangler eller motsier:**
  1. **To eierkjeder for samme modell.** Etter AD-6 peker `forsok` på `Quiz` og `oving` på `Notat`. Da har `Okt` to mulige veier til eieren (`quiz__notat__emne__eier` og `notat__emne__eier`), avhengig av `type`. AD-8 forutsetter én vei per modell i `tilgang.py`. Med to nullbare FK-er blir `egne(Okt, bruker)` et OR-filter som er lett å gjøre feil. Det er nettopp IDOR-hullet AD-8 skal hindre.
  2. **«per notat og bruker» i AD-6.** ER-diagrammet viser ingen `bruker` på `Okt`, og et notat har bare én eier. Enten er «og bruker» overflødig, eller så finnes det et felt spinen ikke nevner. Utviklere vil gjøre det ulikt.
  3. **Posisjon.** Fordi studenten kan hoppe over spørsmål, er «første ubesvarte» ikke det samme som «spørsmålet studenten kom til». UX krever en lagret posisjon. Spinen har ingen.
  4. **Tidsstempler.** Fortsett-boksen sorterer nyeste først, og historikken viser dato og sorterer nyeste øverst. `Okt` trenger `opprettet`/`endret` og `levert_tidspunkt`. Ingen av dem er nevnt.
  5. **Spørsmål i URL-en.** Feilmeldingen ved Lever lenker til «spørsmål 4», og Fortsett lenker til et bestemt spørsmål. URL-konvensjonen har bare `/okter/<id>/`.
  6. **Tverrgående spørring.** Fortsett-boksen og menyen viser påbegynte økter for alle emner. Det er en spørring som ingen tjeneste eier i dag.
- **Forslag:** Endre AD-6: `Okt` har alltid `notat` (FK, også for `forsok`) og `quiz` (nullbar, satt bare for `forsok`, og quizens notat må være det samme). Eierkjeden for `Okt` er da alltid `notat__emne__eier`. Constraintene blir «høyst én påbegynt `forsok` per `quiz`» og «høyst én påbegynt `oving` per `notat`», uten bruker. Legg til feltene `posisjon`, `opprettet`, `endret` og `levert_tidspunkt` (nullbar). Utvid URL-konvensjonen med `/okter/<id>/sporsmal/<nr>/`. `/okter/<id>/` sender videre til `posisjon` for en påbegynt økt og til resultatet for en levert. Legg spørringen `paabegynte_okter(bruker)` i `services/okter`.

### F-02 – Spørsmålssettet i en øvingsøkt fryses ikke

- **Alvorlighet:** Høy
- **Kilde:** PRD FR-22 (økten lagres underveis «på samme måte som i et forsøk»), FR-18 (fortsette senere), FR-21 og FR-23 (feilbanken endres ved levering av forsøk). EXPERIENCE.md: Quizfremdrift «Spørsmål N av M», UJ-3 «5 av 10 besvart». Spinen: AD-7.
- **Hva mangler:** AD-7 fryser bare rekkefølgen på alternativene. For en øvingsøkt er spørsmålene feilbanken «nå», og den endrer seg når et forsøk på en av notatets quizer leveres mens øvingsøkten står påbegynt. Fortsetter studenten øvingsøkten etterpå, kan M, nummereringen og «5 av 10 besvart» være annerledes, og lagrede svar kan høre til spørsmål som ikke lenger er med. Rekkefølgen på spørsmålene er heller ikke fastsatt for noen av typene.
- **Forslag:** Endre AD-7: Når en `Okt` opprettes, lagres en ordnet liste over spørsmål med alternativrekkefølgen for hvert av dem. Det kan være en egen tabell (`OktSporsmal`: `okt`, `sporsmal`, `nr`, `alternativ_rekkefolge`) eller ett JSON-felt. Det gjelder begge typer. Økten viser og leverer bare disse spørsmålene. Blir et spørsmål lært via et forsøk mens øvingsøkten står påbegynt, blir det likevel værende i økten, og AD-2 håndterer svaret som et svar på et spørsmål som ikke ligger i feilbanken.

### F-03 – Levering kan skje to ganger

- **Alvorlighet:** Høy
- **Kilde:** PRD FR-18 («også fra en annen enhet»), FR-23 (to riktige på rad), SM-3. Spinen: AD-2 og AD-13.
- **Hva mangler:** AD-2 krever én `transaction.atomic`, men sier ikke at levering bare kan skje én gang. Et dobbeltklikk på Lever, en fane som sender skjemaet på nytt, eller to enheter med samme påbegynte økt kan kalle `registrer_svar` to ganger for samme svar. Da blir et spørsmål lært etter ett riktig svar, og det bryter den viktigste regelen i læringssløyfen. Det er heller ikke bestemt hva som skjer når en gammel side lagrer et svar til en økt som allerede er levert.
- **Forslag:** Endre AD-2: `lever_okt` bytter status med en betinget oppdatering, `Okt.objects.filter(pk=…, status="pabegynt").update(status="levert", levert_tidspunkt=…)`, inne i transaksjonen. Gir den 0 rader, avbrytes leveringen uten at noe registreres, og brukeren sendes til resultatet. Lagring av svar til en levert økt avvises med en melding fra `feilmeldinger.py`. Det knytter også F-12 til en konkret serverfeil. Legg til en test som leverer samme økt to ganger.

### F-04 – KI-merket: modellnavn og prompt-versjon i testmodus og seed

- **Alvorlighet:** Middels
- **Kilde:** PRD NFR-7, NFR-9 («Merkingen gjelder også i testmodus, fordi mock-svarene kommer fra ekte genereringer», «sier hvilken modell som laget quizen»). EXPERIENCE.md: KI-merking («Modellnavnet hentes fra quizen (NFR-7), ikke fra gjeldende konfigurasjon»). DESIGN.md: `ai-label` «Laget av KI (Claude Sonnet 5.5) · kan inneholde feil». Spinen: AD-11 og AD-12.
- **Hva motsier:** AD-11 sier at `Quiz` lagrer `MODELL` «(fra `.env`)» og `PROMPT_VERSJON`. I testmodus er det feil: quizen er laget av den modellen og prompt-versjonen som laget mock-filen, ikke av det som står i `.env` nå. Da viser KI-merket feil modell, og NFR-7 brytes for alle quizer sensor lager. I tillegg viser merket et visningsnavn («Claude Sonnet 5.5»), mens `.env` har en modell-ID. Ingenting i spinen gjør om fra den ene til den andre.
- **Forslag:** Endre AD-11: `QuizUtkast` har feltene `modell` og `prompt_versjon`. Ved ekte generering er de lik `MODELL` og `PROMPT_VERSJON`. Endre AD-12: hver mock-fil har `modell`, `prompt_versjon` og `laget` som metadata, og `generer` i testmodus gir dem videre. `Quiz` lagrer alltid utkastets verdier. Legg til `ki.visningsnavn(modell_id)`, som slår opp i en liten tabell og bruker selve ID-en når navnet ikke finnes der. Malene bruker bare `quiz.modell`, aldri innstillingene.

### F-05 – Notatets språk for `lang` (WCAG 3.1.2, NFR-6)

- **Alvorlighet:** Middels
- **Kilde:** PRD NFR-8 («Spørsmålene merkes med notatets språk når det ikke er norsk (3.1.1, 3.1.2)»), NFR-6, FR-12 («på samme språk som notatet»). EXPERIENCE.md: Accessibility Floor, Språk («Spørsmål og alternativer får `lang` fra notatets språk når det ikke er norsk»). Spinen: AD-11 og konvensjonen Tid (`LANGUAGE_CODE="nb"`).
- **Hva mangler:** For å sette `lang` må appen vite hvilket språk quizen er på. Det er data, men ingen modell har et språkfelt, og JSON-skjemaet i `ki` er utsatt («Prompttekst og JSON-skjema i detalj»). Bestemmes ikke dette før mock-svarene lages, mangler det i alle mock-filene. Det er et AA-krav og en del av SM-7.
- **Forslag:** Endre AD-11: JSON-skjemaet har feltet `sprak` (BCP 47, for eksempel `en`, `nb`). `sjekk` krever at det finnes, `QuizUtkast` og `Quiz` lagrer det, og mock-filene har det. Ny konvensjon: maler setter `lang="{{ quiz.sprak }}"` på spørsmålsboksen og alternativene når språket ikke er `nb`, `nn` eller `no`. Velg samtidig én verdi for sidens `lang`. PRD og UX sier `lang="no"`, men `LANGUAGE_CODE="nb"` gir `nb` hvis malen bruker `{{ LANGUAGE_CODE }}`. Begge er gyldige, men konvensjonen bør si hvilken som gjelder.

### F-06 – Resultatdata: «Lært! ✓» og «lagt i feilbanken»

- **Alvorlighet:** Middels
- **Kilde:** EXPERIENCE.md: IA (Øv-resultat: «Lært! ✓» med fasit og «telleren for resten»), Lært-boks («hvert spørsmål som ble lært i økten»), Voice and Tone («3 spørsmål er lagt i feilbanken»), State Patterns («Alle feil lært»). DESIGN.md: Brand & Style (den eneste feiringen er når et spørsmål blir lært). PRD FR-23 («Det tas da ut av feilbanken, og fasiten vises»). Spinen: AD-2 og AD-6.
- **Hva mangler:** Resultatsiden må vite hva som skjedde ved akkurat denne leveringen: hvilke spørsmål som ble lært, hvilke som ble lagt til, hvilke som fikk telleren nullstilt, og hva telleren står på for resten. `registrer_svar` returnerer ingenting etter AD-2, og et `laert_tidspunkt` blir overskrevet hvis raden åpnes igjen. Spinen sier heller ikke om resultatet skal kunne vises på nytt (ny innlasting, en lenke fra historikken) eller bare rett etter levering. Det er også en liten motsigelse mellom kildene: etter FR-23 kan et spørsmål bli lært via et nytt forsøk, og da skal fasiten vises, mens UX har Lært-boksen bare på Øv-resultat.
- **Forslag:** Endre AD-2: `registrer_svar` returnerer et utfall (`ny_i_feilbank`, `nullstilt`, `teller_okt`, `laert`, `ingen_endring`), og leveringen lagrer det på `Svar` (feltet `utfall`). Da kan resultatet vises på nytt uten å regne baklengs. Bestem at Resultat og Øv-resultat bruker samme tjeneste og mal (det følger av AD-6), så Lært-boksen også vises når et forsøk gjør et spørsmål lært. Si fra til UX om dette.

### F-07 – Fasit som skjult informasjon er ingen invariant

- **Alvorlighet:** Middels
- **Kilde:** PRD FR-19 («Fasiten vises ikke for spørsmål som er besvart feil»), FR-23 («Fasiten vises ikke før spørsmålet er lært»). Tilbakemelding 4.1 og 4.5. EXPERIENCE.md: Resultatrad og Lært-boks. Spinen: AD-7.
- **Hva mangler:** At fasiten er skjult, er en kjerneregel i produktet, men spinen sier bare hvor fasiten er lagret (`Alternativ.er_riktig`), ikke hvem som får lese den. Et HTMX-fragment, et `data-`-attributt, en rekkefølge som avslører svaret eller en resultatmal som viser «riktig svar var …» er lette feil å gjøre, og de bryter FR-19 og FR-23 uten at noen test merker det.
- **Forslag:** Ny regel (AD-16, eller et tillegg til AD-7): `er_riktig` sendes aldri til malene for Quiz, Øv på feil eller Resultat. Fasit vises bare gjennom én tjenestefunksjon, for eksempel `fasit_hvis_laert(sporsmal)`, som brukes av Lært-boksen. Rettingen skjer i tjenestelaget. Legg til en test som sjekker at quizsiden ikke inneholder noe som skiller det riktige alternativet fra de andre.

### F-08 – Seed: påbegynt forsøk, filer på disk og alltid mock

- **Alvorlighet:** Middels
- **Kilde:** PRD FR-28 («et emne med notater, quizer, leverte forsøk og en feilbank»), UJ-5. EXPERIENCE.md: UJ-5 trinn 2 («Mine emner viser et emne med dekningsgrad, og nederst «Fortsett der du slapp»»). Addendum: «Testbruker og eksempeldata lages med en seed-kommando», og SQLite-filen og opplastede filer ligger i `.gitignore`. Spinen: AD-1, AD-12 og Strukturfrø.
- **Hva mangler:**
  1. UX krever et påbegynt forsøk i eksempeldataene. FR-28 nevner det ikke, og spinen sier ingenting om hva seed lager.
  2. `media/` ligger i `.gitignore`. Seed-notatene må derfor få ekte filer kopiert fra `testdokumenter/`, ellers feiler «Lag ny quiz» og «Prøv igjen» på dem.
  3. Etter AD-12 er `ki.er_testmodus()` eneste kilde. Kjører sensor seed etter å ha lagt inn en ekte nøkkel og slått av testmodus, vil seed via tjenestene kalle det ekte API-et. Det bryter NFR-3, koster penger og gir eksempeldata som ikke kan gjentas.
  4. Det står ikke hva som skjer om seed kjøres to ganger.
- **Forslag:** Ny regel under AD-12 eller AD-1: `seed_testdata` lager quizer fra mock-svarene direkte (en egen funksjon i `ki`, for eksempel `mock_utkast(dokument, nivaa, antall)`), uansett modus. Seed kopierer testdokumentene inn i `media/` via den samme tjenesten som brukes ved opplasting, og lager minst ett levert forsøk med feil, én feilbank og ett påbegynt forsøk. Kjøres seed på nytt, slettes testbrukerens emner via `slett_emne` før alt lages igjen.

### F-09 – Ingen vei til å lage mock-svarene, og SM-2 mangler verktøy

- **Alvorlighet:** Middels
- **Kilde:** Addendum: «Mock-svarene lages ved å kjøre testdokumentene mot ekte modell én gang». PRD FR-27 (30 spørsmål per testdokument og nivå), SM-2 («dokumenteres med modell, dato og prompt-versjon»), SM-4. Tilbakemelding 4.1 («Vurder også en kort begrunnelse per fasit som vises når spørsmålet er lært»). Spinen: AD-11, AD-12 og Utsatt (prompt og JSON-skjema).
- **Hva mangler:** Testmodus, seed og alle testene står og faller med `ki/mock/<dokument>/<nivå>.json`, men spinen sier ikke hvordan filene lages, hvilket format de har (se F-04 og F-05) eller hvor resultatet av SM-2 havner. Hver gang `PROMPT_VERSJON` endres eller et felt legges til, må alle 15 filene lages på nytt mot den ekte modellen. Derfor må skjemaet være bestemt før filene lages første gang. Det gjelder også en eventuell `begrunnelse` per fasit fra tilbakemelding 4.1. Den er billig å ha med nå og dyr å legge til senere.
- **Forslag:** Ny konvensjon eller AD: kommandoen `lag_mocksvar` (den bruker `ki` og skriver bare filer, så AD-11 brytes ikke) kjører hvert testdokument på hvert nivå med 30 spørsmål mot den ekte modellen, kjører `sjekk(…, 30)` og skriver JSON med metadata (`modell`, `prompt_versjon`, `laget`, `sprak`, kildefilens SHA-256). Den kan også skrive en CSV til den manuelle vurderingen i SM-2. Gruppa bør bestemme før første kjøring om `begrunnelse` skal være med i skjemaet. Hvis ikke, kan det stå under Utsatt med beskjed om at mock-filene da må lages på nytt. Tilbakemelding 4.1 er ellers riktig plassert under Utsatt, men faglærer ba om at den ble avklart *før* arkitekturen. Det bør stå at den er sendt videre til gruppa.

### F-10 – Mobil og annen enhet passer ikke med «bare lokal maskin»

- **Alvorlighet:** Middels
- **Kilde:** PRD FR-18 («også fra en annen enhet»), UJ-2 og UJ-3 (mobil), NFR-1, SM-6 («Minst én av dem har tatt et påbegynt forsøk videre på mobil»), NFR-4. Spinen: driftsdiagrammet (bare nettleser på lokal maskin), Utsatt (hosting) og konvensjonen Konfigurasjon.
- **Hva motsier:** Etter driftsdiagrammet og konfigurasjonen kan appen bare nås fra maskinen den kjører på. For å oppfylle SM-6 og FR-18 må en mobil på samme nett nå `runserver`. Det krever `runserver 0.0.0.0:8000` og at maskinens IP står i `ALLOWED_HOSTS`, og ingen av delene finnes i spinen. Uten dette kan ikke brukertesten gjennomføres slik PRD-en beskriver den.
- **Forslag:** Konvensjon: `ALLOWED_HOSTS` leses fra `.env`, med `localhost,127.0.0.1` som standard. README beskriver hvordan appen kjøres på lokalnettet for en brukertest. Legg til «mobil på samme nett» i driftsdiagrammet. Si samtidig at dette bare er for testing og ikke er hosting, så NFR-4 og Utsatt fortsatt holder.

### F-11 – Notat uten quiz trekker ned emnets dekningsgrad for alltid

- **Alvorlighet:** Middels
- **Kilde:** PRD FR-15 (filen lagres før genereringen, «Prøv igjen»), FR-6 og FR-10 (et notat kan ikke slettes alene), FR-24 («Et nivå uten quiz teller som 0 %»), FR-25 (snittet av notatenes dekningsgrad). Tilbakemelding 4.3 (innhold som ikke kan bli en quiz). Spinen: AD-4 og AD-10 (`for_lite_innhold`).
- **Hva mangler:** Notatet opprettes før genereringen (det må det for at «Prøv igjen» skal virke). Feiler genereringen for godt, for eksempel med `for_lite_innhold` eller en fil som ikke kan leses, blir det stående et notat med 0 % dekningsgrad. Det kan ikke slettes uten å slette hele emnet, og det trekker emnets snitt ned for alltid. AD-4 sier ikke om et notat uten quiz er med i emnets snitt.
- **Forslag:** Endre AD-4 så det sier det eksplisitt. Anbefalt: et notat uten noen quiz er ikke med i emnets snitt, og et emne der ingen notater har quiz, viser «Ingen dekningsgrad» (samme visning som et emne uten notater). Legg det til som testtilfelle, og meld det til PRD-en som en presisering av FR-25.

### F-12 – «Lagring feiler» krever HTMX-feilhåndtering

- **Alvorlighet:** Lav
- **Kilde:** EXPERIENCE.md: State Patterns «Lagring feiler» («Svaret ble ikke lagret. Sjekk nettet og prøv igjen.» ved knappen, studenten blir på samme spørsmål) **[ASSUMPTION]**, og Åpne punkter 4. Spinen: AD-13.
- **Hva motsier:** Etter AD-13 er Neste, Forrige og Lever vanlige POST-skjemaer, og HTMX er bare en forbedring. Uten JavaScript betyr en nettfeil at nettleseren viser sin egen feilside. Appen kan da ikke vise meldingen, og studenten blir ikke stående på samme spørsmål. Tilstanden kan bare lages med HTMX og feilhåndtering i nettleseren. Feil på serveren (levert økt, se F-03) er en annen sak og må gi samme side med melding.
- **Forslag:** Konvensjon under AD-13: quiznavigasjonen bruker HTMX mot de samme endepunktene, og en felles lytter på `htmx:sendError` og `htmx:responseError` viser meldingen i et felt med `role="alert"` ved knappen uten å bytte spørsmål. Uten JavaScript gjelder nettleserens egen feilside, og det godtas. Feil på serveren gir vanlig respons med melding fra `feilmeldinger.py`.

### F-13 – Lange PDF-er og modellgrenser mot FR-8 «uansett sideantall»

- **Alvorlighet:** Lav
- **Kilde:** PRD FR-8 («uansett sideantall»), FR-9 (PDF sendes hel). Tilbakemelding 4.3 («en veldig lang PDF (modellen har trolig en sidegrense, sjekk den)»). Spinen: AD-10 og AD-11.
- **Hva mangler:** API-et har grenser for sider og størrelse på en forespørsel med PDF. AD-10 har ingen feilkode for «filen er for stor for modellen», så feilen havner i `api_feil` med en generell melding. Faglærer nevnte akkurat denne saken.
- **Forslag:** Legg til feilkoden `for_stor` i AD-10, som `ki` bruker når API-et avviser dokumentet på grunn av størrelse eller sideantall. Meldingen foreslår å dele opp filen. Ellers kan det stå under Utsatt at slike feil gir `api_feil`, slik at valget er tatt med vilje.

### F-14 – NFR-3 og ikke-mål: filer serveres aldri, ingen Files API

- **Alvorlighet:** Lav
- **Kilde:** PRD NFR-3 («Filer og data lagres bare lokalt»), kap. 6 («Ingenting kan lastes ned fra appen»), FR-3. Spinen: AD-8, AD-11, AD-14 og Strukturfrø (`media/`).
- **Hva mangler:** Det er vanlig i Django å legge til `static(settings.MEDIA_URL, …)` i `urls.py`. Gjør noen det, kan filene i `media/` hentes uten å gå gjennom AD-8, og ikke-målet om at ingenting kan lastes ned, brytes. Spinen sier heller ikke at PDF skal sendes direkte i forespørselen og ikke via Anthropics Files API, som lagrer filen hos Anthropic.
- **Forslag:** Legg til i AD-14 eller AD-11: «`media/` har ingen URL. Filene leses bare av `ki.les_fil`. PDF sendes som base64 i forespørselen, ikke via Files API.»

### F-15 – htmx må ligge lokalt, og CSRF for HTMX

- **Alvorlighet:** Lav
- **Kilde:** PRD NFR-4 (ingen eksterne tjenester utenom KI-modellen), SM-1. DESIGN.md: Typography («virker uten nett»). PRD NFR-2. Spinen: Stack (htmx 2.x) og Strukturfrø.
- **Hva mangler:** Det står ikke hvor htmx lastes fra. Lastes det fra en CDN, er det en ekstern tjeneste. I tillegg trenger HTMX-POST-er et CSRF-token, ellers avviser Django dem.
- **Forslag:** Legg `static/js/htmx.min.js` (fast versjon, committet) inn i Strukturfrø. Konvensjon: basemalen setter `hx-headers` med CSRF-tokenet. Ingen CDN.

### F-16 – `DEBUG`, «Ikke funnet»-tilstanden og statiske filer

- **Alvorlighet:** Lav
- **Kilde:** EXPERIENCE.md: State Patterns «Ikke funnet» («Fant ikke siden» og lenke til Mine emner). PRD FR-3. Spinen: konvensjonen Konfigurasjon (`DEBUG`).
- **Hva mangler:** Djangos egen 404-mal brukes bare når `DEBUG=False`. Med `DEBUG=True` får sensor Djangos gule feilside i stedet for tilstanden UX beskriver. Med `DEBUG=False` serverer `runserver` ikke statiske filer, og da mangler `app.css` og htmx. Spinen tar ikke stilling.
- **Forslag:** Bestem standardverdien i `.env.example`. Ett alternativ er `DEBUG=False`, med `runserver --insecure` i README eller WhiteNoise som ny avhengighet. Et annet er å godta `DEBUG=True` lokalt og skrive at 404-siden da bare testes med `DEBUG=False`.

### F-17 – Konto: passordregler, e-post og innloggingsmelding

- **Alvorlighet:** Lav
- **Kilde:** PRD FR-1 («Passordet må ha minst 8 tegn», duplikat-e-post), FR-2 (samme melding). EXPERIENCE.md: State Patterns «Feil innlogging» («Feil e-post eller passord.»). Spinen: AD-15.
- **Hva mangler:** Djangos standard `AUTH_PASSWORD_VALIDATORS` avviser også vanlige passord, passord med bare tall og passord som ligner e-posten. Det er strengere enn FR-1, som bare krever 8 tegn. Spinen sier ikke om e-post skal være unik uten hensyn til store og små bokstaver. `AbstractUser` med e-post som `USERNAME_FIELD` krever `username = None` og en egen manager. Det er en kjent felle som hører hjemme i den samme beslutningen.
- **Forslag:** Presiser i AD-15: bare `MinimumLengthValidator(8)`, e-post lagres med små bokstaver og sjekkes uten hensyn til store og små bokstaver, `username = None` og egen manager, og innloggingsskjemaet bruker meldingen fra `feilmeldinger.py`.

### F-18 – Tone og ordlyd har ikke noe hjem

- **Alvorlighet:** Lav
- **Kilde:** EXPERIENCE.md: Voice and Tone (du-form, «som en medstudent»), State Patterns (ordlyd for timeout og formatfeil). Spinen: konvensjonen Feilmeldinger.
- **Hva mangler:** Spinen samler feilmeldinger i `feilmeldinger.py`, men sier ikke hvor ordlyden kommer fra. Tekst som kommer fra Django selv (skjemavalidering, innlogging) har en annen tone.
- **Forslag:** Utvid konvensjonen: «Tekst til brukeren følger EXPERIENCE.md (Voice and Tone og State Patterns). Djangos egne meldinger byttes ut der brukeren ser dem.»

### F-19 – Avrunding av dekningsgrad

- **Alvorlighet:** Lav
- **Kilde:** PRD FR-24 (35 %) og FR-25 (snittet av notatene). EXPERIENCE.md: UJ-2 («48 % for hele emnet»). Spinen: AD-4 og konvensjonen Tester.
- **Hva mangler:** Det står ikke om emnets snitt regnes av avrundede eller uavrundede verdier, eller hvordan tallet avrundes når det vises. To utviklere og testene kan få ulike svar.
- **Forslag:** Konvensjon: dekningsgrad regnes som et tall mellom 0 og 1 uten avrunding, også i emnets snitt, og avrundes til hele prosent bare i malen.

### F-20 – Tilbake, brødsmuler og sidetittel trenger samme forelderdata

- **Alvorlighet:** Lav
- **Kilde:** EXPERIENCE.md: Navigasjon («Tilbake går alltid ett nivå opp i hierarkiet», Quiz, Resultat og Øv på feil går til notatet, brødsmuler), Tilbake-knapp (`aria-label` «Tilbake til HTML»), Accessibility Floor 2.4.2 (sidetittel).
- **Hva mangler:** Tilbake-knappen, brødsmulene og `<title>` bygger alle på kjeden emne › notat. For økter avhenger det av at `Okt` kan finne notatet sitt (F-01). Uten en konvensjon lager hver view sin egen versjon.
- **Forslag:** Konvensjon: hver view gir malen `smuler` (en liste med tittel og URL). Tilbake er det nest siste elementet, og `<title>` bygges av den samme listen.

### F-21 – Genereringskjeden: tilstand mellom steg, transaksjoner og ny innlasting

- **Alvorlighet:** Lav
- **Kilde:** PRD FR-14 (knappen låst til genereringen er ferdig eller har feilet), FR-15. EXPERIENCE.md: Ventepanel, «Lag quiz»-knapp. Spinen: AD-9.
- **Hva mangler:**
  1. `Genereringsjobb` lagrer `raatt_svar` mellom «lager» og «sjekker», men ingenting mellom «leser» og «lager». Det står ikke om «lager» leser filen på nytt.
  2. Med SQLite kan en transaksjon som står åpen under et KI-kall på opptil 120 s låse databasen for andre forespørsler, for eksempel lagring av svar i en annen fane.
  3. Laster brukeren inn siden på nytt mens en jobb er aktiv, må siden vise ventepanelet og fortsette kjeden. Ellers er knappen ikke låst, slik FR-14 krever (serveren avviser riktignok en ny jobb).
- **Forslag:** Presiser i AD-9: «leser» sjekker bare at filen kan leses, og «lager» leser den på nytt. Ingen databasetransaksjon er åpen under et KI-kall. Notatsiden og opplastingssiden viser ventepanelet og fortsetter kjeden når notatet har en aktiv jobb.

### F-22 – Testkonvensjoner for SM-3, SM-4 og SM-5

- **Alvorlighet:** Lav
- **Kilde:** PRD SM-3 (alle konsekvenser i FR-17 til FR-25), SM-4 (format på quizer fra testdokumentene), SM-5 («Det testes for alle sider»). Spinen: konvensjonen Tester.
- **Hva mangler:** Konvensjonen nevner bare regneeksemplene fra FR-24 og FR-25.
- **Forslag:** Utvid konvensjonen: (a) hver konsekvens i FR-17 til FR-25 har en test i tjenestelaget, (b) en test går gjennom alle mock-filene med `sjekk(…, 30)`, og (c) en felles tilgangstest går gjennom alle URL-mønstre med ID-er fra en annen bruker og forventer 404. Da fanger den også nye views.

### F-23 – Mindre motsigelser og hull inne i spinen

- **Alvorlighet:** Lav
- **Kilde:** Spinen selv, sammenholdt med PRD FR-9, kap. 9 spørsmål 1 og tilbakemelding kap. 5.
- **Funn:**
  1. AD-11 fastslår «PDF sendes hel som dokument», mens Utsatt sier at valget mellom PDF og tekst avgjøres i testfasen. Faglærer påpekte den samme motsigelsen i PRD-en. Skriv i AD-11 at valget er foreløpig og bare kan endres inne i `ki`.
  2. Tabellen Kapabilitet → arkitektur mangler rader for NFR-1, NFR-2, NFR-3, NFR-4 og NFR-6, selv om `binds` lister dem.
  3. Stack oppgir `anthropic ≥ 0.38`, men AD-11 bruker `output_config.format` (structured outputs). Den versjonen er trolig for gammel til det. Sjekk laveste versjon som støtter det, og sett den.
  4. Filene lagres som `<uuid>.<endelse>`, mens UX viser notatet med navn («HTML») og sorterer notater alfabetisk. `Notat` må ha et navn eller lagre det opprinnelige filnavnet. Det er ikke nevnt i spinen.

---

## Bekreftet dekket

Disse punktene fra kildene har landet i spinen og trenger ingen endring:

- Faglærer 4.2 (spørsmålsidentitet) er løst av AD-5 og AD-3.
- Faglærer 4.3 (API-feil og innhold som ikke kan bli en quiz) er i hovedsak løst av AD-10. Se F-13 for lange PDF-er.
- Faglærer kap. 5 (forsøk mot øvingsøkt) er løst av AD-6 med `type`.
- Testmodus-stripen og merknaden om forhåndslagret innhold (EXPERIENCE State Patterns, FR-27) er dekket av AD-12 (context processor og `forhandslagret`).
- Vilkår én gang med tidspunkt (FR-7) er dekket av AD-15.
- Generering med steg, 120 s, «Prøv igjen» og `role="status"` (FR-14, FR-15, NFR-8 4.1.3) er dekket av AD-9.
- UX åpent punkt 5 (CSS-rammeverk) er løst med Tailwind og ferdigbygd CSS som committes. Det støtter også SM-1.
- NFR-3 (aldri sende innhold i testmodus, testene kjører alltid i testmodus) er dekket av AD-12.
- NFR-5 og NFR-7 (én KI-modul, lagre modell og prompt) er dekket av AD-11. Se F-04 for testmodus.
