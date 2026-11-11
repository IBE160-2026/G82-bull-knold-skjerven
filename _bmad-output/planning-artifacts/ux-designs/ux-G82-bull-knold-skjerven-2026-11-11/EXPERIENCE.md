---
name: FåreQuiz
status: final
created: 2026-11-11
updated: 2026-11-11
sources:
  - ../../prds/prd-G82-bull-knold-skjerven-2026-11-11/prd.md
  - ../../prds/prd-G82-bull-knold-skjerven-2026-11-11/addendum.md
---

# FåreQuiz: hvordan appen virker

## Foundation

FåreQuiz er en responsiv webapp med ett grensesnitt. Studenten laster opp notater på PC og øver på mobilen (PRD §2.3). Sidene er Django-maler med Tailwind CSS og litt HTMX der siden må oppdateres uten ny innlasting: fremdriften under generering og lagring av svar. Alle sider skal også virke uten JavaScript, bortsett fra stegene i fremdriften.

Utseendet står i [DESIGN.md](DESIGN.md). Begrepene følger ordlisten i PRD-en (§3) nøyaktig, og FR-, NFR- og UJ-numrene viser til PRD-en.

## Information Architecture

| # | Skjermbilde | Nås fra | Formål | Krav |
|---|---|---|---|---|
| S1 | Logg inn | Åpne appen uten å være innlogget | E-post og passord | FR-2 |
| S2 | Registrer | Lenke på S1 | Ny konto | FR-1 |
| S3 | **Emner** (startside) | Innlogging, logoen «FåreQuiz» | Alle emner med dekningsgrad, «Nytt emne» | FR-4, FR-25 |
| S4 | Emne | Kort på S3 | Notatene i emnet med dekningsgrad, «Last opp notat», «Gi nytt navn», «Slett emne» | FR-5, FR-6, FR-24, FR-25 |
| S5 | Godta vilkår | «Last opp notat» første gang | Vilkårene og knappen «Godta og fortsett» | FR-7, NFR-9 |
| S6 | Last opp notat | «Last opp notat» på S4, eller etter S5 | Filvelger, formater og KI-varsel | FR-8 |
| S7 | **Notat** | Kort på S4, eller etter opplasting | Dekningsgrad per nivå, «Øv på feil», «Lag ny quiz», quizlisten og historikken | FR-11, FR-16, FR-22, FR-24, FR-26 |
| S8 | Generering | «Lag quiz» på S7 | Stegene i fremdriften, timeout og «Prøv igjen» | FR-12 til FR-15 |
| S9 | **Ta quiz** | Quizkort på S7, eller etter S8 | Ett spørsmål om gangen | FR-17, FR-18, NFR-9 |
| S10 | Se over og lever | Etter siste spørsmål på S9 | Oversikt over besvarte og ubesvarte spørsmål, «Lever» | FR-17 |
| S11 | Resultat | Lever på S10 | Poengsum, riktig og feil uten fasit, videre til «Øv på feil» | FR-19, FR-21 |
| S12 | Øv på feil | Knapp på S7 eller S11 | Samme flyt som S9–S11 med spørsmålene i feilbanken. Resultatet viser fasiten for spørsmål som er lært. | FR-22, FR-23 |
| S13 | Slett emne | «Slett emne» på S4 | Bekreftelsesside som viser hva som slettes | FR-6 |
| S14 | Ikke funnet | Ukjent eller annen brukers ID | «Fant ikke siden» med lenke til Emner | FR-3 |

**Navigasjon:** Toppfeltet viser «FåreQuiz» (lenke til S3) til venstre og «Logg ut» til høyre. Under toppfeltet står en brødsmulesti, for eksempel «Emner › Webutvikling › HTML-forelesning». Appen har ingen sidemeny og ingen hamburgermeny, fordi strukturen bare er tre nivåer dyp. Når testmodus er på, ligger testmodus-banneret mellom toppfeltet og brødsmulestien på alle sider.

**Bekreftelser og vilkår** vises som egne sider (S5, S13), ikke som popup-vinduer. Det er enklere å gjøre tilgjengelig og virker uten JavaScript.

**Sortering:** Emner sorteres alfabetisk. Notater, quizer og historikk sorteres med det nyeste først.

## Voice and Tone

Teksten i appen er på norsk bokmål og bruker «du». Den er kort og saklig, uten utropstegn og uten emojier. Riktig og feil sies rett ut.

| Gjør | Ikke gjør |
|---|---|
| «7 av 10 riktige» | «Supert! Du fikk 7 av 10! 🎉» |
| «3 spørsmål er lagt i feilbanken.» | «Oops, du bommet på noen!» |
| «Lært. Riktig svar var: …» | «Gratulerer, du har mestret spørsmålet!» |
| «Filen er over 5 MB. Velg en mindre fil.» | «Feil ved opplasting» |
| «Formatet støttes ikke. Bruk PDF, DOCX eller TXT.» | «Ugyldig fil» |
| «Genereringen tok for lang tid. Filen er lagret, så du kan prøve igjen.» | «Timeout (504)» |
| «Du har ikke svart på spørsmål 4 og 7.» | «Skjemaet er ufullstendig» |
| «Ingen notater ennå. Last opp det første.» | «Her var det tomt!» |
| «Laget av KI (Claude Sonnet 5.5). Spørsmålene kan inneholde feil.» | Å skjule modellnavnet eller kalle det «smart quiz» |

## Component Patterns

Her står hvordan komponentene oppfører seg. Utseendet står i DESIGN.md under Components.

| Komponent | Brukes på | Regler |
|---|---|---|
| Emnekort | S3 | Hele kortet er en lenke til S4. Viser emnenavn, antall notater og dekningsgrad i prosent med stolpe. Et emne uten notater viser «Ingen notater» i stedet for prosent (FR-25). |
| Notatkort | S4 | Lenke til S7. Viser filnavn, opplastingsdato, dekningsgrad og antall spørsmål i feilbanken. |
| Quizkort | S7 | Viser vanskelighetsgrad, antall spørsmål, dato og KI-merke. Har et påbegynt forsøk merket «Påbegynt – spørsmål 5 av 10», og knappen er «Fortsett». Ellers er knappen «Ta quiz» eller «Ta på nytt» (FR-18, FR-20). |
| Skjema for ny quiz | S7 | Vanskelighetsgrad er en gruppe med tre radioknapper (lett, middels, vanskelig). Middels er valgt på forhånd. Antall er et tallfelt (min 5, maks 30, standard 10) med forklarende tekst. Knappen er «Lag quiz» (FR-11). |
| Fremdrift | S8 | Tre steg i en liste: «Leser filen», «Lager spørsmål», «Sjekker quizen». Hvert steg er markert som ferdig, pågår eller venter med både ikon og tekst. Knappen er låst så lenge genereringen pågår (FR-14). |
| Spørsmålsvisning | S9, S12 | Teksten «Spørsmål 3 av 10» og en stolpe øverst, deretter spørsmålet og tre svaralternativer. Under står «Forrige» og «Neste». Svaret lagres når studenten trykker «Neste» eller «Forrige» (FR-18). Studenten kan gå videre uten å svare, og ubesvarte spørsmål vises på S10. |
| Oversikt før levering | S10 | Ett nummer per spørsmål, merket «Besvart» eller «Ikke besvart», og hvert nummer er en lenke til spørsmålet. «Lever» er låst til alle er besvart, og en tekst forteller hvilke som mangler (FR-17). |
| Resultatliste | S11, S12 | Poengsummen øverst. For hvert spørsmål vises spørsmålsteksten, svaret studenten valgte og merket Riktig eller Feil. Fasiten vises ikke (FR-19). I «Øv på feil» vises fasiten for spørsmål som akkurat ble lært (FR-23). |
| KI-merke | S7, S9, S10, S11, S12 | I lister står den korte teksten «Laget av KI». På quizsidene (S9–S12) står den fulle teksten med modellnavn og advarsel øverst. Merket er tekst og ikke bare et ikon, og det kan ikke lukkes (NFR-9). |
| Dekningsvisning | S3, S4, S7 | Stolpe med prosent som tekst. På S7 står totalen øverst og lett, middels og vanskelig under, med vektingen forklart: «Vanskelige spørsmål teller mest (50 %)» (FR-24). |
| Historikk | S7 | En tabell med dato, quiz (vanskelighetsgrad og antall) og poengsum, nyeste først. På mobil vises hver rad som et lite kort i stedet for en tabell (FR-26). |
| Filvelger | S6 | En vanlig `<input type="file">` med etikett, og ingen dra-og-slipp (WCAG 2.5.7). Godkjente formater og maks størrelse står over feltet. Filen sjekkes i nettleseren før opplasting og alltid på serveren (FR-8). |

## State Patterns

| Tilstand | Skjermbilde | Hva som vises |
|---|---|---|
| Ingen emner | S3 | «Ingen emner ennå. Opprett ditt første emne.» og skjemaet for nytt emne. |
| Ingen notater | S4 | «Ingen notater ennå. Last opp det første.» og knappen «Last opp notat». |
| Notat uten quiz | S7 | Dekningsgraden er 0 % med teksten «Lag en quiz for å komme i gang». Skjemaet for ny quiz står øverst. |
| Genereringen pågår | S8 | Fremdriftssteg og låst knapp. Fremdriften meldes til skjermleser, for eksempel «Lager spørsmål». |
| Timeout | S8 | Feilmelding og knappen «Prøv igjen», som bruker samme fil og samme valg (FR-15). |
| Feil format to ganger | S8 | «Klarte ikke å lage en gyldig quiz. Prøv igjen, eller velg færre spørsmål.» Ingen quiz lagres (FR-13). |
| Avvist fil | S6 | Feilmeldingen står ved filvelgeren, og fokus flyttes dit (FR-8). |
| Påbegynt forsøk | S7, S9 | Quizkortet viser «Påbegynt» og knappen «Fortsett». S9 åpnes på første ubesvarte spørsmål (FR-18). |
| Ikke alle besvart | S10 | «Lever» er låst, og en tekst sier hvilke spørsmål som mangler. |
| Tom feilbank | S7, S11 | «Øv på feil» er låst og viser «Ingen spørsmål i feilbanken» (FR-22). |
| Alt lært i en økt | S12 resultat | «Alle spørsmålene er lært. Feilbanken er tom.» og lenke tilbake til notatet. |
| Feil innlogging | S1 | «Feil e-post eller passord.» Teksten er den samme uansett hva som var feil (FR-2). |
| E-posten finnes alt | S2 | «Det finnes allerede en konto med denne e-posten.» (FR-1). |
| Annen brukers data | S14 | Siden «Fant ikke siden» med statuskode 404 (FR-3). |
| Testmodus | Alle | Testmodus-banneret vises. På S1 står i tillegg testbrukerens e-post og passord (FR-28). |

## Interaction Primitives

- Studenten klikker eller trykker for å gjøre noe. Alle handlinger er vanlige lenker, knapper eller skjemaer.
- **Quiz med tastatur:** Tab flytter til alternativgruppen. Piltastene velger alternativ, og et alternativ kan også velges med mellomrom. Enter eller Tab til «Neste» går videre. Det er ingen egne hurtigtaster, så det er ingenting å lære.
- **Lagring:** Et svar lagres når studenten går til et annet spørsmål. Det finnes ingen egen «Lagre»-knapp. Lukker studenten fanen, er alle svar fram til forrige spørsmål lagret, og det siste valget også hvis HTMX rakk å sende det.
- **Sletting** skjer bare via bekreftelsessiden S13, der studenten trykker «Slett emnet og alt innhold».
- **Forbudt:** dra-og-slipp som eneste måte å gjøre noe på, informasjon som bare vises når man holder musepekeren over, tidsgrenser i quizen, automatiske popup-vinduer, karuseller og animasjoner som ikke kan slås av.

## Accessibility Floor

Appen følger WCAG 2.2 nivå A og AA (NFR-8). Kontrastkravene står i DESIGN.md. Her står krav til oppførsel, først for alle sider og deretter per skjermbilde.

**Alle sider:**
- `<html lang="no">` og en unik `<title>` per side, for eksempel «HTML-forelesning – Webutvikling – FåreQuiz» (2.4.2, 3.1.1).
- En lenke «Hopp til innhold» er det første fokuserbare elementet (2.4.1).
- Overskriftene følger rekkefølgen h1 → h2 uten hopp. Det er én h1 per side.
- Fokusringen er alltid synlig. Toppfeltet ligger ikke over fokusert innhold, fordi `scroll-padding-top` er satt til høyden på toppfeltet (2.4.7, 2.4.11).
- Tab-rekkefølgen følger leserekkefølgen.
- Toppfeltet, brødsmulestien og testmodus-banneret ligger på samme sted på alle sider (3.2.3, 3.2.6).
- Siden virker ved 320px bredde og 200 % tekstforstørrelse uten vannrett rulling (1.4.4, 1.4.10).
- Respekterer `prefers-reduced-motion`. Appen har nesten ingen animasjon.

**Per skjermbilde:**

| Skjermbilde | Krav som må sjekkes |
|---|---|
| S1 Logg inn, S2 Registrer | Feltene har `<label>` og `autocomplete="email"` / `current-password` / `new-password`. Innliming og passordbehandlere er tillatt, og det er ingen CAPTCHA (3.3.8). Feilmeldinger står over skjemaet, er koblet til feltet med `aria-describedby`, og fokus flyttes til dem (3.3.1). |
| S3 Emner, S4 Emne | Kortene er lenker med tydelig tekst, for eksempel «Webutvikling, 4 notater, dekningsgrad 62 %». Dekningsstolpen har `role="img"` med prosent i `aria-label`, eller er skjult for skjermleser når prosenten allerede står som tekst (1.1.1). |
| S5 Vilkår | Vilkårene er vanlig tekst på siden, ikke i en rulleboks. Teksten nevner KI-tjenesten (Anthropic), ansvaret for personopplysninger og at quizene kan inneholde feil (FR-7, NFR-9). |
| S6 Last opp | Filvelgeren har synlig etikett og hjelpetekst om formater og størrelse koblet med `aria-describedby`. Det er ingen dra-og-slipp (2.5.7). Feil meldes med `role="alert"` (4.1.3). |
| S7 Notat | Radioknappene for vanskelighetsgrad ligger i `<fieldset>` med `<legend>`. Tallfeltet har `min` og `max` og en feilmelding i tekst. Historikken er en ekte `<table>` med `<th scope>` på store skjermer. Låste knapper har `aria-disabled` og en forklaring. |
| S8 Generering | Fremdriften ligger i en `aria-live="polite"`-region, og hvert nytt steg leses opp. Timeout og feil leses opp med `role="alert"`, og fokus flyttes til «Prøv igjen» (4.1.3). |
| S9 Ta quiz, S12 Øv på feil | Alternativene er ekte radioknapper i `<fieldset>`, og `<legend>` er spørsmålsteksten. Hvert spørsmål har `lang` satt til notatets språk når det ikke er norsk (3.1.2). «Spørsmål 3 av 10» er tekst og ikke bare en stolpe. Fokus flyttes til spørsmålet når studenten trykker «Neste». Quizen har ingen tidsgrense (2.2.1). KI-merket står i teksten og leses opp før spørsmålet (NFR-9). |
| S10 Se over og lever | Ubesvarte spørsmål er lenker med teksten «Spørsmål 4 – ikke besvart». Låst «Lever» har en synlig forklaring. |
| S11 Resultat | Poengsummen leses opp som tekst, for eksempel «7 av 10 riktige». Riktig og feil vises med ikon, ordet «Riktig» eller «Feil» og farge, aldri bare farge (1.4.1). Ikonene har `aria-hidden`, fordi ordet står ved siden av. |
| S13 Slett emne | Siden sier nøyaktig hva som slettes, for eksempel «4 notater, 9 quizer og all historikk». «Avbryt» kommer før «Slett» i tab-rekkefølgen. |
| S14 Ikke funnet | Siden har en h1 «Fant ikke siden» og en lenke til Emner. Den sier ikke om dataene finnes (FR-3). |

**Test (SM-7):** axe DevTools eller Lighthouse kjøres på alle 14 skjermbildene. Deretter testes kjerneflyten UJ-1 manuelt, med bare tastatur og med skjermleser (NVDA på Windows eller VoiceOver på mobil).

## Responsive & Platform

| Bredde | Oppførsel |
|---|---|
| `< md` (under 768px) | Én kolonne med 16px marg. Knappene i quizen («Forrige», «Neste» og «Lever») er like brede som skjermen og står nederst i innholdet, ikke fast i bunnen. Historikken vises som kort. Brødsmulestien viser bare forrige nivå, for eksempel «‹ Webutvikling». |
| `≥ md` | Innholdet er sentrert med maks bredde 768px. Historikken vises som tabell. Quizknappene står på én linje. |

Minste bredde som støttes er 320px (WCAG 1.4.10), og PRD-ens 360px (NFR-1) er dermed dekket. Det finnes ingen egen mobilapp.

## Inspiration & Anti-patterns

Gruppa har ikke nevnt forbilder. Det som er valgt bort, følger av ordene «effektiv, enkel, seriøs»:

- **Valgt bort: streaker, merker, konfetti og lyder.** FåreQuiz er et verktøy, ikke et spill (PRD SM-C1, SM-C3).
- **Valgt bort: tidsgrense per spørsmål.** Den gir stress, er et WCAG-problem (2.2.1) og passer ikke med at Tore skal kunne bli avbrutt.
- **Valgt bort: alle spørsmål på én side.** Gruppa valgte ett spørsmål om gangen, fordi det passer bedre på mobil.

## Key Flows

### Flow 1: Første quiz (Tore, 2. år, på PC kvelden etter forelesningen). Realiserer UJ-1.

1. Tore registrerer seg på S2 og kommer til S3: «Ingen emner ennå».
2. Han oppretter «Webutvikling», åpner emnet (S4) og trykker «Last opp notat».
3. Det er første opplasting, så S5 viser vilkårene. Han trykker «Godta og fortsett».
4. På S6 velger han `html-forelesning.pdf` (2 MB) og laster opp. Han kommer til S7.
5. Han lar middels og 10 spørsmål stå og trykker «Lag quiz». S8 viser stegene «Leser filen ✓ → Lager spørsmål … → Sjekker quizen».
6. S9 åpnes på «Spørsmål 1 av 10». Han svarer og trykker «Neste» ti ganger. S10 viser at alle er besvart, og han trykker «Lever».
7. **Høydepunkt:** S11 viser «7 av 10 riktige» og «3 spørsmål er lagt i feilbanken». Tilbake på S7 er dekningsgraden 21 % (middels 70 % × 30 %), og «Øv på feil (3)» er klar.

**Feil:** Han velger først `forelesning.mp4`. S6 viser «Formatet støttes ikke. Bruk PDF, DOCX eller TXT.» ved filvelgeren (UJ-4).

### Flow 2: Avbrutt og fortsatt på mobilen (Tore, mellom to forelesninger og senere på bussen). Realiserer UJ-3.

1. Tore starter en vanskelig quiz med 20 spørsmål på PC og svarer på 10.
2. Han må gå og lukker fanen.
3. På bussen åpner han FåreQuiz på mobilen og går til S3, så S4 og så S7. Quizkortet viser «Påbegynt – spørsmål 11 av 20» og «Fortsett».
4. **Høydepunkt:** S9 åpnes på spørsmål 11. De ti første svarene er der, og han kan bla tilbake og se dem.
5. Han svarer på resten, leverer og ser resultatet på S11.

### Flow 3: Øv på feil til spørsmålene er lært (Tore, kvelden før eksamen, på mobilen). Realiserer UJ-2.

1. På S3 ser Tore at «Webutvikling» har 48 %. Han åpner notatet med flest spørsmål i feilbanken.
2. Han trykker «Øv på feil (5)». S12 viser de fem spørsmålene med alternativene i ny rekkefølge og uten fasit.
3. Han leverer: 4 riktige. To av spørsmålene hadde han også fått riktig forrige gang.
4. **Høydepunkt:** Resultatet viser «2 spørsmål er lært», og nå vises fasiten for akkurat de to. Feilbanken har 3 igjen, og dekningsgraden for notatet går opp.

### Flow 4: Sensor i testmodus. Realiserer UJ-5.

1. Sensor følger README-en og åpner appen. Testmodus-banneret vises, og S1 viser testbrukerens e-post og passord.
2. Sensor logger inn og ser på S3 et ferdig emne med dekningsgrad.
3. Sensor laster opp et testdokument og lager en quiz. S8 viser de samme stegene, og quizen er merket «Laget av KI».
4. **Høydepunkt:** Sensor tar quizen, øver på feil og ser dekningsgraden endre seg. Alt skjer uten API-nøkkel.
