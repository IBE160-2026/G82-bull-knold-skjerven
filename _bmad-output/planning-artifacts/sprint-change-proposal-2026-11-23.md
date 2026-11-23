---
type: sprint-change-proposal
date: 2026-11-23
status: approved
trigger: 'Gruppemøte 23.11: Martins design blir felles UX'
scope: moderate
affects:
  - _bmad-output/planning-artifacts/epics-christian.md
  - _bmad-output/planning-artifacts/architecture/architecture-G82-bull-knold-skjerven-2026-11-15-christian/ARCHITECTURE-SPINE.md
  - _bmad-output/planning-artifacts/ux-designs/ux-G82-bull-knold-skjerven-2026-11-15-christian/
  - _bmad-output/implementation-artifacts/sprint-status.yaml
---

# Endringsforslag for sprinten: Martins design blir felles UX

## 1. Hva som har skjedd

I gruppemøtet 23.11 bestemte gruppa at Martins design blir felles UX: [DESIGN.md](ux-designs/ux-G82-bull-knold-skjerven-2026-11-11/DESIGN.md), [EXPERIENCE.md](ux-designs/ux-G82-bull-knold-skjerven-2026-11-11/EXPERIENCE.md) og prototypen, med skjermbildene S1–S16. Christians arkitektur og epics beholdes. Christians UX (15.11) blir liggende som arkiv.

Arkitekturen og epics er laget ut fra Christians UX. De må derfor peke på Martins design og beskrive de samme skjermbildene, tekstene og flytene. Ellers bygger story 1.3 og senere stories et annet grensesnitt enn det gruppa har valgt.

Type endring: ny beslutning fra gruppa (valg mellom to UX-versjoner), ikke en teknisk begrensning.

## 2. Konsekvenser

### Det som ikke endres

- **Stacken.** Martins DESIGN.md beskriver også «Tailwind CSS i Django-maler». Django, HTMX, Tailwind v4 og SQLite står.
- **Koden i story 1.1.** Den har ingen maler eller CSS. `Bruker.vilkar_godtatt` og `LoginRequiredMiddleware` finnes og brukes som før. Ingen tilbakerulling trengs.
- **PRD-en.** Martins design bygger på samme PRD (11.11). FR-7 («godta vilkårene før første opplasting») oppfylles strengere: vilkårene godtas ved første innlogging.
- **Domenereglene.** AD-1 til AD-7, AD-9 til AD-12 og AD-14 til AD-22 gjelder uendret.
- **Epic-strukturen.** Ingen epics legges til eller fjernes, og ingen stories legges til eller fjernes.

### Det som endres

| Hva | Hvorfor | Omfang |
|---|---|---|
| UX-DR1–UX-DR30 i epics | Beskriver Christians design (grønt tema, menypanel, Tilbake-knapp, «Mine emner», oransje øving, «Lært! ✓») | Skrives om. Nye UX-DR31–UX-DR35 for S10, S1b, S15, S16 og S1 |
| Story 1.2–1.6, 2.3–2.6, 3.1, 3.3, 3.5, 4.1–4.3, 5.1–5.3, 6.1, 6.3 | Viser til skjermbilder, tekster og flyt fra Christians UX | Akseptansekriteriene justeres |
| Vilkår | Flyttes fra opplastingen (2.3) til første innlogging (S1b, story 1.2) | Ny AD-23, FR-7 i Epic 1 |
| Opplasting og generering | Martin: S6 laster opp → S7 Notat → «Lag quiz» → S8 egen side. Christian: opplasting og «Lag quiz» i ett skjema | Story 2.3 og 2.4, URL `/jobber/<id>/` |
| Levering | Martin har egen side S10 «Se over og lever» | Story 3.1 og 3.3, GET på `/okter/<id>/lever/` |
| Arkitekturen | Kildestier, offentlig personvernside, vilkårsregel, JS for opplastingsfremdrift, nye URL-er | Fem små tillegg |
| Sprint-status | Fire storytitler endres | Nøklene får nye navn (alle står i `backlog`) |

## 3. Anbefalt fremgangsmåte

**Direkte justering (alternativ 1).** Endringene passer inn i de eksisterende epics og stories. Ingen kode må rulles tilbake (alternativ 2 er unødvendig), og omfanget av v1 er uendret (alternativ 3 er unødvendig).

- **Innsats:** middels. Det meste er tekst i epics. Arkitekturen trenger fem små tillegg.
- **Risiko:** lav. Endringen er gjort før story 1.2 er startet, og story 1.1 berøres ikke.
- **Tidslinje:** ingen forsinkelse, så lenge endringen er merget før story 1.3 startes.

## 4. Endringene i detalj

### 4.1 UX-designkrav (epics, seksjonen «UX-designkrav (UX-DR)»)

**GAMMELT:** UX-DR1–UX-DR30 etter Christians DESIGN.md og EXPERIENCE.md.

**NYTT:** Hele seksjonen erstattes. Numrene beholdes for samme tema, slik at henvisningene i storyene fortsatt stemmer, og fem nye krav legges til:

- **UX-DR1 Tokens:** fargene, typografien, hjørnene og avstandene fra Martins DESIGN.md i Tailwind v4 `@theme`. Varm palett med `accent-strong` #5C3A21 som hovedfarge, `error` #A34420 (terrakotta) og `success` #3F624D (salvie). Typografi `page-title` 24, `section-title` 18, `question` 20, `body` 16, `meta` 14 og `score` 36 px. Hjørner 4/6/8/full. `content-max` 768 px, marg 16/24 px og `tap-min` 44 px. Størrelser i `rem`. Ingen mørk modus.
- **UX-DR2 Grunnmal:** mørkt toppfelt (`surface-inverse`) med logoen (fåret i ballongen) og «FåreQuiz», som lenker til S3, og «Logg ut» (POST) til høyre. «Logg ut» vises ikke på S1 og S2. «Hopp til innhold» er det første fokuserbare elementet. Sidens bakgrunn er `page-bg` med `kart.svg`. Én `<h1>`, `<main>` og `<title>` på formen «HTML-forelesning – Webutvikling – FåreQuiz». `scroll-padding-top` er lik høyden på toppfeltet.
- **UX-DR3 Brødsmulesti** i stedet for Tilbake-knapp: «Emner › Webutvikling › HTML-forelesning» under toppfeltet. Under `md` vises bare forrige nivå, for eksempel «‹ Webutvikling».
- **UX-DR4 Ingen meny:** Appen har ingen sidemeny og ingen hamburgermeny. Fotlinjen på alle sider har opphavsrettsteksten fra prototypen og en lenke til personvernerklæringen (S15).
- **UX-DR5 Knapper:** hovedknapp i `accent-strong` med krem tekst, høyst én per skjermbilde. Sekundærknapp i krem med brun kant («Forrige», «Avbryt», «Gi nytt navn»). Fareknapp i `error`, bare på S13. Låste knapper har `aria-disabled` og en synlig forklaring. Alle knapper er minst 44 px høye.
- **UX-DR6 Fokusring:** 2 px `accent-strong` med 2 px avstand, i toppfeltet `focus-inverse`. `outline: none` er forbudt.
- **UX-DR7 Kort:** emnekort, notatkort og quizkort der hele kortet er én lenke, med `card`-skygge og et løft på 2 px ved hover (av ved `prefers-reduced-motion`). Emner sorteres alfabetisk. Notater, quizer og historikk sorteres med det nyeste først.
- **UX-DR8 Dekningsvisning:** stolpen er en reiserute (stiplet spor, fyll i kaffebrun, fåret i ballongen på enden av fyllet med `aria-hidden`, og et flagg ved 100 %), og prosenten står alltid som tekst. På S7 står totalen øverst og lett, middels og vanskelig under, med teksten «Vanskelige spørsmål teller mest (50 %)». S4 har tallfliser for dekningsgrad og antall i feilbanken. Et emne uten notater viser «Ingen notater».
- **UX-DR9 Fortsett der du slapp:** boks øverst på S3 med de påbegynte øktene, nyeste først, for eksempel «Middels, 10 spørsmål», «Webutvikling · HTML-forelesning · spørsmål 5 av 10» og «Fortsett quizen». Vises ikke når det ikke finnes påbegynte økter.
- **UX-DR10 Spørsmål og svaralternativer:** spørsmålet står på et flashcard (maks 560 px, `question` 20 px) og er `<legend>` i en `<fieldset>`. Under står tre svaralternativer (`option-card`) som radioknapper med etikett, minst 44 px høye. Valgt alternativ har 2 px kant i `accent-strong`, `surface-muted` og fylt radioknapp. Ved hover blir bakgrunnen `card-hover`. Piltastene velger. `lang` settes fra quizen når språket ikke er norsk.
- **UX-DR11 Fremdrift:** teksten «Spørsmål 3 av 10» og en reiserute med fåret i ballongen (`aria-hidden`) og et flagg i enden.
- **UX-DR12 Forrige og Neste:** begge lagrer svaret og går videre, også uten valgt svar. Neste på siste spørsmål går til S10. Fokus flyttes til spørsmålet. Mislykket lagring gir «Svaret ble ikke lagret. Sjekk nettet og prøv igjen.» ved knappen.
- **UX-DR13 KI-merke:** «Laget av KI» i lister, og «Laget av KI (<modell>). Spørsmålene kan inneholde feil.» øverst på S9–S12, med modellen fra quizen. Merket kan ikke lukkes og vises også i testmodus.
- **UX-DR14 Quizkort:** et påbegynt forsøk vises som «Påbegynt – spørsmål 5 av 10» med knappen «Fortsett». Ellers er knappen «Ta quiz» eller «Ta på nytt».
- **UX-DR15 Skjema for ny quiz (S7):** `<fieldset>` med lett, middels og vanskelig, der middels er valgt. Tallfelt for antall med `min` 5, `max` 30, standard 10 og forklarende tekst. Knappen er «Lag quiz».
- **UX-DR16 Opplasting:**
  - **S5:** kort bekreftelse første gang brukeren laster opp: «Du har godtatt vilkårene. Det skjedde da du logget inn første gang …», lenke til S15, og knappene «Gå videre til opplasting» og «Avbryt».
  - **S6:** filvelger med etikett, der formatene og maks størrelse står over feltet (koblet med `aria-describedby`). KI-varsel, ingen dra-og-slipp, og knappen «Last opp».
  - **S6b:** filnavnet, fremdrift som reiserute, låst knapp og beskjed om å ikke lukke fanen.
  - **S6c:** «Opplastingen ble avbrutt. Filen er ikke lagret. Last opp på nytt.»
  - **Feil:** «Filen er over 5 MB. Velg en mindre fil.», «Formatet støttes ikke. Bruk PDF, DOCX eller TXT.» og «Velg en fil først.» står ved feltet, med `role="alert"`, og fokus flyttes dit.
  - **Etterpå:** Etter opplasting åpnes S7.
- **UX-DR17 Generering (S8):** egen side med de tre stegene «Leser filen», «Lager spørsmål» og «Sjekker quizen» i en liste. Hvert steg er markert som ferdig, pågår eller venter, med ikon og tekst, i en `aria-live="polite"`-region. Knappen er låst. Når quizen er laget, åpnes S9 på spørsmål 1.
- **UX-DR18 Feil ved generering:**
  - Timeout gir «Genereringen tok for lang tid. Filen er lagret, så du kan prøve igjen.»
  - Formatfeil to ganger gir «Klarte ikke å lage en gyldig quiz. Prøv igjen, eller velg færre spørsmål.»
  - Feil fra API-et gir «KI-tjenesten svarte ikke. Prøv igjen.»
  - Feilkodene `for_lite_innhold`, `for_stor` og `api_nokkel` får egne tekster i samme tone.
  - Alle feilene vises med `role="alert"`, og fokus flyttes til «Prøv igjen».
- **UX-DR19 Feilmeldinger:** står ved feltet og er koblet med `aria-describedby`, og fokus flyttes dit. På S1 og S2 står de over skjemaet.
- **UX-DR20 Resultat (S11):** «7 av 10 riktige» i `score` med `role="status"`. For hvert spørsmål vises spørsmålsteksten, svaret studenten valgte og ✓ «Riktig» eller ✕ «Feil» (ikonet har `aria-hidden`). Fasiten vises ikke. Teksten «3 spørsmål er lagt i feilbanken.» og knappen «Øv på feil».
- **UX-DR21 Øv på feil (S12):** samme flyt som S9–S11, også S10. Aksentfargen settes på seksjonen og er terrakotta, slik at fremdrift, prikker og knapper blir terrakotta, som i prototypen. Valgt alternativ vises fortsatt med form, ikke bare med farge.
- **UX-DR22 Resultat av øving:** for hvert spørsmål som ble lært i økten står «Lært. Riktig svar var: …» og begrunnelsen (TF-2). Spørsmål som ennå ikke er lært, viser lært-prikker og teksten «1 av 2 riktige på rad». Når alt er lært: «Alle spørsmålene er lært. Feilbanken er tom.» og en lenke tilbake til notatet. Ingen feiring og ingen utropstegn.
- **UX-DR23 Notat (S7):**
  - **Rekkefølge:** dekningsgrad (UX-DR8), «Øv på feil (N)» eller låst knapp med «Ingen spørsmål i feilbanken», quizkortene, «Lag ny quiz» og historikk.
  - **Historikk:** `<table>` med `<th scope>` fra `md` og oppover, og kort på mobil. Uten forsøk: «Ingen forsøk ennå. Ta en quiz for å se historikken.»
  - **Notat uten quiz:** 0 %, «Lag en quiz for å komme i gang» og skjemaet øverst.
- **UX-DR24 Slett emne (S13):** egen side som sier nøyaktig hva som slettes, for eksempel «4 notater, 9 quizer og all historikk». «Avbryt» kommer før fareknappen «Slett emnet og alt innhold» i tab-rekkefølgen.
- **UX-DR25 Tomtilstander:** S3 viser «Ingen emner ennå. Opprett ditt første emne.» og kortet «Nytt emne». S4 viser «Ingen notater ennå. Last opp det første.» og knappen «Last opp notat».
- **UX-DR26 Testmodus:** banneret «Testmodus: quizene bruker mock-svar, ingen KI kalles» ligger mellom toppfeltet og brødsmulestien på alle sider. S1 viser testbrukerens e-post og passord. En quiz fra en fil som ikke er et testdokument, får merknaden «Testmodus: denne quizen er laget fra et forhåndslagret testdokument, ikke fra filen din.»
- **UX-DR27 Ikke funnet (S14):** h1 «Fant ikke siden», lenke til Emner og status 404. Siden sier ikke om dataene finnes hos andre.
- **UX-DR28 Innlogging og registrering (S1, S2):**
  - **Skjemaene:** synlige etiketter, `autocomplete="email"` og `current-password`/`new-password`. Innliming er tillatt, og det er ingen CAPTCHA.
  - **Meldinger:** «Feil e-post eller passord.», «Det finnes allerede en konto med denne e-posten.» og «Passordet må ha minst 8 tegn.»
  - **Utløpt økt:** «Du er logget ut. Logg inn igjen for å fortsette.» Etter innlogging åpnes siden brukeren var på (`next`).
- **UX-DR29 Responsivt:**
  - **Under `md`:** én kolonne med 16 px marg. Quizknappene er like brede som skjermen og står nederst i innholdet, ikke fast. Historikken vises som kort.
  - **Fra `md`:** innholdet er sentrert med maks 768 px og 24 px marg, historikken er en tabell, og quizknappene står på én linje.
  - **Alltid:** ingen vannrett rulling ved 320 px og 200 % tekst.
- **UX-DR30 Tone:** etter Martins EXPERIENCE.md. Norsk bokmål, du-form, kort og saklig, uten utropstegn og uten emojier. Tekstene i «Gjør»-tabellen brukes ordrett.
- **UX-DR31 (ny) Se over og lever (S10):** ett nummer per spørsmål merket «Besvart» eller «Ikke besvart», der hvert nummer er en lenke («Spørsmål 4 – ikke besvart»). «Lever» har `aria-disabled` til alle er besvart, og teksten sier hvilke som mangler: «Du har ikke svart på spørsmål 4 og 7.»
- **UX-DR32 (ny) Personvern ved første innlogging (S1b):** dialog med `aria-modal` og fokusfelle, som Esc ikke lukker. Teksten har de fire punktene fra prototypen: behandling av notater hos Anthropic, ikke del personopplysninger, KI-generert innhold kan ha feil, og vilkår og loggføring. Den har også en lenke til S15. «Jeg har forstått og godtar» lagrer tidspunktet. Brukeren kommer ikke videre før dette er gjort.
- **UX-DR33 (ny) Personvernerklæring (S15):** offentlig side med teksten fra prototypen: hva som lagres, hvorfor, hvem det deles med, hvor lenge, rettigheter og opphavsrett. Siden nås fra S1, S1b og fotlinjen.
- **UX-DR34 (ny) Nytt emne (S16):** egen side fra kortet «Nytt emne» på S3, med emnenavn, valgfrie notater (samme filvelger som S6) og «Opprett emne». Tomt eller brukt navn gir «Navnet kan ikke være tomt.» eller «Du har allerede et emne med dette navnet.» ved feltet.
- **UX-DR35 (ny) Forside (S1):**
  - **Hero:** overskrift, en kort intro, «Registrer deg» og tre dekorative flashcards med `aria-hidden`.
  - **Under hero:** tre informasjonskort (last opp, ta quizen, øv på feilene) og innloggingsskjemaet.
  - **Bilder:** logoen og fanebildet er `favicon.svg`, og bakgrunnen er `kart.svg`, begge fra prototypen.

### 4.2 Stories (epics)

Bare det som endres, er tatt med. Ellers står storyene som før.

**Frontmatter og «Oversikt»**
- GAMMELT: `inputDocuments` viser til `ux-…-2026-11-15-christian/DESIGN.md` og `EXPERIENCE.md`, og teksten sier «UX-designet (Christians versjon, 15.11)».
- NYTT: viser til `ux-G82-bull-knold-skjerven-2026-11-11/DESIGN.md` og `EXPERIENCE.md`, og teksten sier «UX-designet (Martins design, valgt som felles UX 23.11)». Nytt avsnitt: «Endret 23.11: tilpasset Martins design, se sprint-change-proposal-2026-11-23.md.»

**Kravdekning og epic-liste**
- FR-7: «Epic 2 – Godta vilkår én gang» → «Epic 1 – Godta vilkårene ved første innlogging (story 1.2). Epic 2 sjekker dem ved opplasting (story 2.3).»
- Epic 1: FR dekket + FR-7. Tailwind-tokens og grunnmalen etter Martins design kommer i story 1.3.
- Epic 2: «Studenten godtar vilkårene, laster opp …» → «Studenten laster opp et notat, velger nivå og antall på notatsiden …». FR-7 fjernes fra FR-listen.
- Epic 4: «i oransje øvemodus, ser «Lært! ✓» med fasit og begrunnelse» → «i øvemodus med terrakotta-aksent, ser «Lært. Riktig svar var: …» med begrunnelse».

**Story 1.2 → «Registrere konto, logge inn og godta vilkårene»** (FR-1, FR-2, FR-7, NFR-2, NFR-3, UX-DR28, UX-DR32, UX-DR33, UX-DR35, AD-23)
- Nytt kriterium: Logg inn er en del av forsiden S1 med hero og informasjonskort. Registrer er S2.
- Nytt kriterium: en innlogget bruker uten `vilkar_godtatt` sendes til personvern-dialogen (S1b) fra alle sider. «Jeg har forstått og godtar» kaller `services.vilkar.godta_vilkar`, lagrer tidspunktet og sender brukeren videre. Dialogen vises ikke igjen. Uten JavaScript virker den som en vanlig side.
- Nytt kriterium: personvernerklæringen (S15) er offentlig. `@login_not_required` gjelder bare Logg inn, Registrer og Personvernerklæring.
- Nytt kriterium: når økten er utløpt, står «Du er logget ut. Logg inn igjen for å fortsette.», og etter innlogging åpnes siden brukeren var på.
- GAMMELT: «startsiden `/`, som foreløpig er en enkel side som story 1.4 gjør til Mine emner». NYTT: «… som story 1.4 gjør til Oversikt».
- Meldingene etter UX-DR28.

**Story 1.3 → «Toppfelt, brødsmuler og felles sidemal»** (UX-DR1–UX-DR6, UX-DR26, UX-DR27, UX-DR29, UX-DR30)
- GAMMELT: topplinje med Tilbake, logo og «☰ Meny», `<details>`-meny, Tilbake-knapp, 760 px, og logoen skjules under 400 px.
- NYTT: mørkt toppfelt med logo og «Logg ut», «Hopp til innhold», brødsmulesti, testmodus-banner med Martins tekst, fotlinje med lenke til S15, kartbakgrunn, `favicon.svg` og `kart.svg` i `static/img/`, og 768 px. Ingen meny og ingen Tilbake-knapp.
- Kriteriene for knapper og fokus følger UX-DR5 og UX-DR6 (2 px fokusring, `focus-inverse` i toppfeltet).
- «Fant ikke siden» lenker til Emner (S3).

**Story 1.4 → «Opprette emne og se Oversikt»** (FR-3, FR-4, UX-DR7, UX-DR9, UX-DR25, UX-DR34)
- GAMMELT: Mine emner som en liste, velkomstkort, og menyen viser emnene.
- NYTT: S3 Oversikt med kortet «Nytt emne» først og emnekortene alfabetisk, med miniatyr, antall notater og plass til dekningsgrad (Epic 5). Tomtilstand etter UX-DR25.
- «Nytt emne» er egen side (S16) med bare emnenavn foreløpig. Feltet for valgfrie notater legges til i story 2.3.
- Etter opprettelse åpnes S4 med «Ingen notater ennå. Last opp det første.»
- Feilmeldingene etter UX-DR34.

**Story 1.5 Gi emne nytt navn** (FR-5)
- GAMMELT: «samme skjema som Nytt emne … og Tilbake går til emnet».
- NYTT: knappen «Gi nytt navn» på S4 åpner et skjema på emnesiden med dagens navn og knappen «Lagre navn». Samme feilmeldinger som i 1.4.

**Story 1.6 Slette emne** (UX-DR24)
- GAMMELT: «Slette «<navn>»? …», knappen «Ja, slett emnet», og etterpå åpnes Mine emner.
- NYTT: siden sier nøyaktig hva som slettes («4 notater, 9 quizer og all historikk»). «Avbryt» kommer før fareknappen «Slett emnet og alt innhold». Etterpå åpnes S3.

**Story 2.3 → «Laste opp notat»** (FR-7 kontroll, FR-8, AD-1, AD-14, AD-23, UX-DR16, UX-DR34)
- GAMMELT: én side med filvelger, nivå, antall, vilkårsboks og «Lag quiz».
- NYTT: «Last opp notat» på S4 åpner S5 (kort bekreftelse) første gang, ellers S6 direkte. S6 har filvelger, KI-varsel og «Last opp». S6b viser fremdrift med JavaScript, og uten JavaScript sendes skjemaet på vanlig måte. S6c gjelder avbrutt opplasting. Etter opplasting åpnes S7.
- Nytt kriterium: `last_opp` avviser opplasting når `vilkar_godtatt` er tom (FR-7 håndheves i tjenesten).
- Nytt kriterium: S16 får det valgfrie feltet for notater, som bruker `last_opp` for hver fil.
- Feilmeldingene etter UX-DR16 (tre tekster i stedet for én samlet).
- Midlertidig-merknaden om ventepanelet fjernes. Skjemaet for ny quiz på S7 kommer i 2.4.

**Story 2.4 Lage quiz med fremdrift** (FR-11–FR-14, AD-9, AD-19, UX-DR15, UX-DR17)
- GAMMELT: «Gitt Last opp notat med gyldig fil og valg … skjemaet byttes ut med ventepanelet «Lager quiz, håper du er klar!»».
- NYTT: «Gitt Notatsiden med skjemaet for ny quiz (UX-DR15). Når brukeren trykker «Lag quiz», opprettes en `Genereringsjobb`, og brukeren sendes til S8 `/jobber/<id>/`, som kjører stegkjeden.» Stegene vises som en liste med ikon og tekst (UX-DR17), uten den faste overskriften.
- «Last siden på nytt»-kriteriet gjelder S8. En ny «Lag quiz» mens en jobb er aktiv, sender brukeren til S8 for den aktive jobben.

**Story 2.5 Feil, timeout og «Prøv igjen»** (UX-DR18)
- Tekstene byttes til Martins tekster (UX-DR18). Fokus flyttes til «Prøv igjen».
- Sluttfragmentet lenker til Emner (S3).

**Story 2.6 Flere quizer per notat** (UX-DR13–UX-DR15)
- KI-merket i listen er «Laget av KI». Skjemaet for ny quiz står etter quizkortene, eller øverst når notatet ikke har noen quiz.
- «Tilbake går til emnet» → «brødsmulestien viser emnet».

**Story 3.1 Starte og svare på en quiz** (UX-DR10–UX-DR13)
- GAMMELT: 8 px stolpe, alternativer på minst 56 px, «Tilbake går til notatet», og «på siste spørsmål er Neste byttet ut med Lever».
- NYTT: flashcard, reiserute og alternativer på minst 44 px. Brødsmulestien viser notatet. Neste på siste spørsmål lagrer og går til S10. Fokus flyttes til spørsmålet. `<title>` følger formen «Spørsmål N av M – <notat> – FåreQuiz».

**Story 3.3 Levere og se resultatet** (FR-17, FR-19, FR-21, AD-18, AD-20, UX-DR20, UX-DR31)
- NYTT første kriterium: `/okter/<id>/lever/` med GET viser S10 (UX-DR31). Med POST leveres økten med `lever_okt`. Lever er låst til alle spørsmål er besvart, og serveren avviser fortsatt ubesvarte (AD-18).
- GAMMELT: «Du har ikke svart på alle spørsmålene. Disse mangler: spørsmål 4, spørsmål 7.» ved Lever. NYTT: «Du har ikke svart på spørsmål 4 og 7.» på S10, med lenker.
- GAMMELT: poengkortet «7 av 10» i 56 px, rader med spørsmålsnummer, og «N spørsmål er lagt i feilbanken. Øv på dem til du kan dem.» NYTT: «7 av 10 riktige» i `score`. Hver rad har spørsmålsteksten, svaret studenten valgte og ✓ «Riktig» eller ✕ «Feil». Teksten er «N spørsmål er lagt i feilbanken.»

**Story 3.5 Fortsette der jeg slapp** (UX-DR9, UX-DR14)
- GAMMELT: gul merkelapp «Påbegynt 5/10», boksen nederst på Mine emner og menyen får *Fortsett der du slapp*.
- NYTT: quizkortet viser «Påbegynt – spørsmål 5 av 10» og «Fortsett». Boksen «Fortsett der du slapp» står øverst på S3. Ingen meny.

**Story 4.1 Øve på feilbanken** (UX-DR21, UX-DR23)
- GAMMELT: den oransje knappen «Øv på feil», «Ingen feil å øve på» og practice-fargene erstatter primary.
- NYTT: knappen «Øv på feil (N)» på S7, eller den låste knappen «Ingen spørsmål i feilbanken». S12 har terrakotta-aksent på seksjonen (UX-DR21). Påbegynte øvingsøkter står i boksen på S3.

**Story 4.2 Levere øvingen og se hva som er lært** (UX-DR22)
- GAMMELT: brukerhistorien sier «Lært! ✓», og kriteriene har «Fasit: …», «Feilbanken er tom. Godt jobba!» og «det eneste stedet med en liten feiring».
- NYTT: brukerhistorien sier «vil jeg se riktig svar og begrunnelsen når jeg har svart riktig to ganger på rad». Kriteriene har «Lært. Riktig svar var: …» med begrunnelse, lært-prikker med «1 av 2 riktige på rad», og «Alle spørsmålene er lært. Feilbanken er tom.» med lenke til notatet. Ingen feiring.
- Øvingen bruker også S10 før levering.

**Story 4.3 Melde et spørsmål som feil**
- Ingen endring utover at resultatraden er Martins (✕ «Feil»).

**Story 5.1 Dekningsgrad per notat** (UX-DR8)
- GAMMELT: dekningskortet med «Dekningsgrad for <notat>» og nivåboksene «Lett · 20 %» osv.
- NYTT: totalen øverst med en reiserute-stolpe og lett, middels og vanskelig under, med teksten «Vanskelige spørsmål teller mest (50 %)». Hjelpeteksten om at dekningsgraden kan gå ned, er fortsatt **[ordlyd ikke bestemt]**.

**Story 5.2 Dekningsgrad per emne** (UX-DR7, UX-DR8)
- S4 har tallfliser for dekningsgrad og antall i feilbanken. Notatkortene viser filnavn, dato, dekningsgrad og antall i feilbanken.
- S3: emnekortene har stolpe og prosent, «Ingen notater» for emne uten notater, og «Ingen dekningsgrad» når ingen notater har quiz.
- «Mine emner» → «Oversikt (S3)».

**Story 5.3 Historikk per notat**
- På mobil vises hver rad som et kort (UX-DR29). Uten forsøk: «Ingen forsøk ennå. Ta en quiz for å se historikken.»

**Story 6.1 Testbruker** og **6.3 Sluttkontroll**
- «Mine emner» → «Oversikt (S3)».
- 6.3 kjører axe på alle skjermbildene S1–S16 med S1b, S6b og S6c, i hver tilstand fra Martins EXPERIENCE.md.

### 4.3 Arkitektur (ARCHITECTURE-SPINE.md)

- **A1 Kilder:** `sources` viser til `ux-G82-bull-knold-skjerven-2026-11-11/EXPERIENCE.md` og `DESIGN.md`. Innledningen sier «… på grunnlag av PRD-en og Christians UX-versjon (15.11). Endret 23.11: UX-kilden er Martins design, som gruppa valgte som felles UX.»
- **A2 AD-8, innlogging:** «Bare innlogging og registrering har `@login_not_required`» → «Bare innlogging, registrering og personvernerklæringen (S15) har `@login_not_required`.»
- **A3 Ny AD-23 – Vilkår godtas ved første innlogging** (binder FR-7, NFR-3 og NFR-9):
  - En mellomvare etter `LoginRequiredMiddleware` sender en innlogget bruker med tom `vilkar_godtatt` til `/vilkar/` (S1b). Unntatt er `/vilkar/`, `/personvern/`, utlogging og statiske filer.
  - POST kaller `studier.services.vilkar.godta_vilkar(bruker)` og sender brukeren til `next`.
  - `services.notater.last_opp` avviser opplasting når `vilkar_godtatt` er tom.
  - Siden virker uten JavaScript, og JavaScript gir bare fokusfellen i dialogen.
  - Hindrer at vilkårene sjekkes forskjellig på ulike sider.
- **A4 AD-13, JavaScript:** «Bare genereringskjeden (AD-9) krever JavaScript» → «Bare genereringskjeden (AD-9) krever JavaScript. Opplastingsfremdriften (S6b) og fokusfellen i S1b er forbedringer. Uten JavaScript sendes skjemaene på vanlig måte.»
- **A5 Konvensjoner:**
  - **URL-er:** nye URL-er er `/` (S3 Oversikt), `/emner/ny/` (S16), `/emner/<id>/last-opp/` (S5/S6), `/emner/<id>/slett/` (S13), `/jobber/<id>/` (S8), `/vilkar/` (S1b) og `/personvern/` (S15). `/okter/<id>/lever/` med GET viser S10, og med POST leveres økten.
  - **CSS og JS:** tokens fra Martins DESIGN.md. `favicon.svg` og `kart.svg` fra prototypen ligger i `static/img/`.
  - **Strukturfrøet og tabellen «Kapabilitet → arkitektur»:** `services/` får `vilkar`, og raden «Vilkår og opplasting (FR-7, FR-8)» viser til `services/vilkar`, `services/notater` og AD-23.

### 4.4 Christians UX-mappe (arkiv)

- `status: final` → `status: arkivert` i frontmatter for `DESIGN.md` og `EXPERIENCE.md`.
- Ny fil `ARKIV.md` i mappen: «Arkivert 23.11.2026. Gruppa valgte Martins design (ux-G82-bull-knold-skjerven-2026-11-11) som felles UX. Denne versjonen ligger igjen som dokumentasjon av alternativet og skal ikke brukes som kilde for nye stories.»

### 4.5 Sprint-status

| Gammel nøkkel | Ny nøkkel |
|---|---|
| `1-2-registrere-konto-og-logge-inn-og-ut` | `1-2-registrere-konto-logge-inn-og-godta-vilkarene` |
| `1-3-topplinje-meny-og-felles-sidemal` | `1-3-toppfelt-brodsmuler-og-felles-sidemal` |
| `1-4-opprette-emne-og-se-mine-emner` | `1-4-opprette-emne-og-se-oversikt` |
| `2-3-godta-vilkar-og-laste-opp-notat` | `2-3-laste-opp-notat` |

Alle står i `backlog`, så ingen storyfiler må flyttes.

## 5. Gjennomføring

- **Omfang:** moderat. Backloggen omorganiseres (epics og sprint-status), og arkitekturen får små tillegg. Ingen ny planlegging av PRD eller arkitektur trengs.
- **Hvem:** Utvikleragenten gjør endringene på branchen `tilpass-til-martins-design`. Christian går gjennom endringene i arkitekturen og epics i PR-en, siden det er hans dokumenter. Martin bekrefter at UX-DR-ene gjengir designet hans riktig.
- **Rekkefølge:** PR #2 (story 1.1) merges først. Deretter merges denne PR-en, før story 1.2 og 1.3 startes.
- **Ferdig når:**
  - epics og arkitekturen ikke lenger viser til Christians UX-mappe som kilde
  - hver skjermbilde-ID S1–S16 (med S1b, S6b og S6c) er dekket av minst én story
  - sprint-status har de nye nøklene
  - CI er grønn

## 6. Spørsmål til gruppa (avgjort 23.11)

Gruppa godtok forslagene 23.11:

1. **«Øv på feil»-kortet på S3 i prototypen** er ikke med i v1. Feilbanken er per notat (PRD og AD-16), og en øvingsøkt gjelder ett notat. Kortet er fjernet fra prototypen, valget står under «Valgt bort» i EXPERIENCE.md, og story 1.4 og UX-DR25 sier det.
2. **«Første gang» for S5** betyr «brukeren har ingen notater ennå». Det trengs ikke noe nytt felt. Står i EXPERIENCE.md, UX-DR16 og story 2.3.
3. **Testseksjonen i EXPERIENCE.md** viser nå til alle skjermbildene: S1–S16, S1b, S6b og S6c.

## 7. Tillegg 23.11: Tilbake og Meny i toppfeltet

Etter forslaget ble to commits fra `forslag-design-martin` (17:27) tatt inn. De legger til «‹ Tilbake» og en «Meny»-rullgardin i toppfeltet og reverserer «ingen sidemeny». Magnus valgte å ta dem inn med to justeringer:

- **Menyen** har Oversikt, Nytt emne og Personvernerklæring, men ikke «Øv på feil», fordi feilbanken hører til hvert notat (kap. 6, punkt 1).
- **Tilbake** er en vanlig lenke til forelderen med `aria-label` som sier hvor (ikke `history.back()`), slik at den virker uten JavaScript (AD-13).
- Tilbake, Meny og Logg ut vises bare etter innlogging.

UX-DR2, UX-DR3 og UX-DR4 og story 1.3 er oppdatert. EXPERIENCE.md sier det samme, og «Øv på feil» er fjernet fra menyen i prototypen.

## Sjekkliste

| Del | Status |
|---|---|
| 1 Årsak og kontekst | [x] Gruppebeslutning 23.11, uten feil i implementasjonen |
| 2 Epics | [x] Ingen epics legges til eller fjernes. Fire storytitler endres. Rekkefølgen er uendret |
| 3.1 PRD | [N/A] Ingen konflikt. FR-7 oppfylles strengere |
| 3.2 Arkitektur | [x] A1–A5 gjennomført |
| 3.3 UX | [x] Christians mappe er arkivert, og de tre spørsmålene er avgjort (kap. 6) |
| 3.4 Andre artefakter | [x] CI og koden i story 1.1 er uendret |
| 4 Vei videre | [x] Direkte justering |
| 5 Forslag | [x] Dette dokumentet |
| 6.3 Godkjenning | [x] Godkjent av Magnus i gruppemøtet 23.11 |
| 6.4 Sprint-status | [x] Fire nøkler har fått nye navn |
