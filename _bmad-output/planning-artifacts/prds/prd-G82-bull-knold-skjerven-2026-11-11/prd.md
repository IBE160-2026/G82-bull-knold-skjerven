---
title: "PRD: Foredragsnotater → Quiz"
status: final
created: 2026-11-11
updated: 2026-11-11
---

# PRD: Foredragsnotater → Quiz

## 0. Om dokumentet

PRD-en beskriver hva gruppe G82 skal bygge i v1 av semesteroppgaven i IBE160, og hvordan vi vet at det virker. Den bygger på [product brief v2](../../briefs/brief-G82-bull-knold-skjerven-2026-09-16/brief.md) og faglærers [tilbakemelding](../../briefs/brief-G82-bull-knold-skjerven-2026-09-16/tilbakemelding-product-brief.md), og på beslutningene gruppa tok i møtet 11. november 2026. Den leses av sensor og faglærer, og den er grunnlaget for arkitektur, epics og stories.

Ordene i ordlisten (kap. 3) brukes med nøyaktig samme betydning i hele dokumentet. Kravene (FR) er nummerert fortløpende og gruppert per funksjon. Antakelsene gruppa har bekreftet, er samlet i kap. 10. Teknologivalg står i [addendum.md](addendum.md), ikke i kravene.

## 1. Visjon

Studenten laster opp forelesningsnotatene sine under egne emner og får en quiz laget av KI. Quizen tas i appen og gir poeng. Spørsmål studenten svarer feil på, havner i en feilbank og kommer tilbake til de er lært. En vektet dekningsgrad viser hvor godt studenten kan stoffet i hvert notat og hvert emne.

Å lese notatene på nytt gir gjenkjenning, ikke forståelse. Aktiv gjenkalling virker bedre, men gode quizspørsmål tar tid å lage selv. Studenten vet heller ikke hva hen faktisk ikke kan. Appen tar seg av begge deler: den lager spørsmålene, og den følger opp feilene.

Appen er ikke teknisk unik. Verdien ligger i en stram læringssløyfe: notat → quiz → feilbank → lært. Målet for semesteret er en solid, testet og dokumentert app som sensor kan kjøre lokalt selv.

## 2. Målgruppe

### 2.1 Jobber studenten vil få gjort

- Finne ut hva hen faktisk kan fra en forelesning, ikke bare hva hen kjenner igjen.
- Øve på stoffet uten å bruke tid på å lage spørsmål selv.
- Se progresjon per notat og per emne, så hen vet hva som gjenstår før eksamen.
- Øve på de samme feilene til de sitter.
- Øve på mobilen i små pauser og fortsette der hen slapp.

### 2.2 Ikke målgruppe i v1

- Forelesere som vil lage quizer til studentene sine. Appen har ingen deling eller roller.
- Studenter som vil konkurrere med andre. Appen har ingen sammenligning mellom brukere.

### 2.3 Brukerreiser

Appen er laget for studenter generelt, men designes og testes med medstudenter. Grensesnittet er på norsk, og quizen lages på notatets språk.

**UJ-1. Tore tester seg selv på en forelesning for første gang.**
Tore går 2. år på bachelor og har hørt at det er lurt å teste seg selv før eksamen. Han registrerer seg med e-post og passord og oppretter emnet «Webutvikling». Han laster opp PDF-en fra forelesningen om HTML. Første gang han laster opp, godtar han vilkårene. Han velger middels vanskelighetsgrad og 10 spørsmål og trykker «Lag quiz». Han ser hvilket steg genereringen er på, og knappen er låst så lenge den pågår. Han svarer på alle spørsmålene, leverer og får 7 av 10. Han ser hvilke spørsmål som var feil, men ikke hva som var riktig svar. De tre feilsvarene ligger nå i feilbanken. *(Realiserer FR-1, FR-4, FR-7, FR-8, FR-11 til FR-14, FR-17, FR-19, FR-21.)*

**UJ-2. Tore lager quizer for resten av forelesningene og følger progresjonen.**
Tore likte det og laster opp notatene fra forelesningene om CSS, JavaScript og UX-design under samme emne. For hvert notat lager han quizer på flere vanskelighetsgrader. På emnesiden ser han dekningsgraden for hvert notat og for hele emnet. Han ser også historikken med alle forsøk, dato og poengsum. Kvelden før eksamen åpner han «Øv på feil» på mobilen og jobber seg gjennom feilbanken. Når han har svart riktig på et spørsmål to ganger på rad, er det lært, og nå får han se fasiten. *(Realiserer FR-16, FR-22 til FR-26.)*

**UJ-3. Tore blir avbrutt midt i en quiz.**
Tore har svart på halvparten av spørsmålene da han må gå. Han lukker fanen. Senere åpner han appen på mobilen og ser at quizen står som påbegynt. Han fortsetter fra spørsmålet han kom til, med de første svarene lagret, og leverer. *(Realiserer FR-18.)*
**Feiltilfelle:** Hvis genereringen får timeout, ser Tore «Prøv igjen». Filen er allerede lagret, så han slipper å laste den opp på nytt. *(FR-15.)*

**UJ-4. Tore laster opp en fil appen ikke kan lese.**
Tore prøver å laste opp et opptak av forelesningen som MP4. Appen avviser filen med en melding om at bare PDF, DOCX og TXT på maks 5 MB støttes. *(Realiserer FR-8.)*

**UJ-5. Sensor kjører appen uten API-nøkkel.**
Sensor kloner repoet og følger README-en. Testmodus er på som standard. Sensor logger inn som testbrukeren, der det allerede finnes et emne med notater, quizer og historikk. Sensor laster opp et av testdokumentene og får en quiz fra mock-svarene. Sensor tar quizen, øver på feil og ser at dekningsgraden endrer seg. Hele flyten fungerer uten nøkkel. Vil sensor teste med ekte modell, legger hen inn sin egen Anthropic-nøkkel i `.env` og slår av testmodus. *(Realiserer FR-27 til FR-30.)*

## 3. Ordliste

- **Bruker:** En person med konto (e-post og passord). Ser bare sine egne data. I visjonen og brukerreisene kalles brukeren *studenten*.
- **Emne:** En samling notater som brukeren har opprettet og navngitt, for eksempel «Webutvikling». En bruker har mange emner.
- **Notat:** En opplastet fil og alt som hører til den. Hører til ett emne. Har mange quizer og én feilbank.
- **Fil:** Originalfilen til et notat (PDF, DOCX eller TXT, maks 5 MB). Lagres slik at nye quizer kan lages uten ny opplasting.
- **Vilkår:** Teksten brukeren må godta før første opplasting.
- **Generering:** Kallet til KI-modellen som lager en quiz fra filen.
- **Quiz:** Et sett spørsmål laget fra ett notat med én vanskelighetsgrad og et valgt antall spørsmål (5–30). Et notat kan ha mange quizer.
- **Vanskelighetsgrad:** Lett, middels eller vanskelig. Gjelder hele quizen og alle spørsmålene i den.
- **Spørsmål:** Hører til én quiz. Har tre ulike alternativer, og nøyaktig ett av dem er riktig.
- **Fasit:** Det riktige alternativet for et spørsmål.
- **Forsøk:** Én gjennomføring av en quiz. Er enten *påbegynt* (svar lagres, ikke levert) eller *levert* (har poengsum). En quiz kan ha mange forsøk.
- **Poengsum:** Antall riktige svar av antall spørsmål i et levert forsøk.
- **Feilbank:** Spørsmålene i et notat som brukeren har svart feil på og ennå ikke har lært. Én feilbank per notat.
- **Øv på feil:** En økt med spørsmålene i feilbanken, med alternativene i ny rekkefølge og uten fasit.
- **Lært:** Et spørsmål er lært når det er besvart riktig to ganger på rad etter at det kom i feilbanken. Det tas da ut av feilbanken.
- **Dekket:** Et spørsmål er dekket når det er besvart riktig og ikke ligger i feilbanken.
- **Dekningsgrad:** Andelen dekkede spørsmål, vektet etter vanskelighetsgrad (se FR-24). Finnes for notat og emne.
- **Historikk:** Liste over alle leverte forsøk for et notat, med dato og poengsum.
- **Testmodus:** Driftsmodus der genereringen bruker mock-svar i stedet for å kalle KI-modellen.
- **Mock-svar:** Lagrede svar fra ekte genereringer på testdokumentene.
- **Testdokument:** En av de faste filene som brukes til testing og i testmodus. Settet består minst av en vanlig tekst-PDF på ca. 10 sider, en lysbilde-PDF, en skannet PDF, en DOCX og en TXT.
- **Testbruker:** En ferdig konto med eksempeldata som sensor kan logge inn med i testmodus.

## 4. Funksjoner og krav

### 4.1 Konto og innlogging

**Beskrivelse:** Brukeren registrerer seg med e-post og passord og logger inn. Alle data er knyttet til brukeren, og ingen kan se eller endre en annen brukers data. V1 har ikke glemt passord, endring av passord eller sletting av konto.

#### FR-1: Registrere konto
En besøkende kan registrere seg med e-post og passord. Realiserer UJ-1.
- En e-post som allerede er registrert, gir en feilmelding, og det lages ingen ny konto.
- En ugyldig e-postadresse gir en feilmelding.
- Passordet må ha minst 8 tegn.

#### FR-2: Logge inn og ut
En bruker kan logge inn med e-post og passord og logge ut.
- Feil passord eller ukjent e-post avvises med samme melding, slik at det ikke avsløres om e-posten finnes.
- Etter utlogging gir sider som krever innlogging, en omdirigering til innloggingssiden.

#### FR-3: Bare egne data
En bruker kan bare se og endre sine egne emner, notater, quizer, forsøk og feilbanker.
- Endrer en bruker en ID i URL-en til en annen brukers data, får hen «ikke funnet», ikke dataene.
- Dette gjelder alle sider og alle handlinger som endrer data.

### 4.2 Emner

**Beskrivelse:** Brukeren organiserer notatene sine i emner hen lager selv.

#### FR-4: Opprette emne
En bruker kan opprette et emne med et navn. Realiserer UJ-1.
- Navnet kan ikke være tomt.
- To emner hos samme bruker kan ikke ha samme navn.

#### FR-5: Gi emne nytt navn
En bruker kan gi et emne nytt navn.
- Notater, quizer og historikk i emnet påvirkes ikke.

#### FR-6: Slette emne
En bruker kan slette et emne etter å ha bekreftet det.
- Alle notater i emnet slettes, med filene, quizene, forsøkene, feilbankene og historikken deres.
- Andre emner og dekningsgraden deres påvirkes ikke.
- Sletting av emner er den eneste måten å slette data på i v1. Enkeltnotater og enkeltquizer kan ikke slettes alene.

### 4.3 Opplasting og vilkår

**Beskrivelse:** Brukeren laster opp en fil under et emne, og filen blir et notat. Før første opplasting må brukeren godta vilkårene. Siden minner om at innholdet sendes til en ekstern KI-tjeneste.

#### FR-7: Godta vilkår én gang
En bruker må godta vilkårene før første opplasting. Realiserer UJ-1.
- Vilkårene vises bare ved første opplasting. Har brukeren godtatt dem, vises de ikke igjen.
- Uten godkjenning kan brukeren ikke laste opp.
- Vilkårene sier at brukeren er ansvarlig for personopplysninger i notatene, og at innholdet sendes til en ekstern KI-tjeneste (Anthropic).
- Vilkårene sier at quizene lages av KI og kan inneholde feil (NFR-9).
- Tidspunktet for godkjenningen lagres på brukeren.

#### FR-8: Laste opp fil
En bruker kan laste opp en fil i formatet PDF, DOCX eller TXT, på maks 5 MB og uansett sideantall, under et emne. Realiserer UJ-1 og UJ-4.
- En fil over 5 MB avvises med en melding som oppgir grensen.
- En fil i et annet format, for eksempel MP4, PPTX eller et bilde, avvises med en melding som oppgir formatene som støttes.
- Filen lagres, slik at nye quizer kan lages uten ny opplasting.
- Opplastingssiden viser en kort melding om at innholdet sendes til en ekstern KI-tjeneste.

#### FR-9: Lese innholdet i filen
Appen sender innholdet i filen til KI-modellen.
- En PDF sendes hel, slik at lysbilder og skannede sider kan brukes.
- Fra DOCX og TXT hentes teksten ut og sendes.
- Alle de fem testdokumentene gir en quiz, også lysbilde-PDF-en og den skannede PDF-en.

#### FR-10: (Fjernet 11.11.2026)
Gruppa bestemte at et notat ikke kan slettes alene i v1. Notater slettes bare sammen med emnet (FR-6). ID-en beholdes, slik at de andre kravnumrene ikke endres.

### 4.4 Lage quiz

**Beskrivelse:** For et notat velger brukeren vanskelighetsgrad og antall spørsmål, og appen lager en quiz med KI. Genereringen skjer mens brukeren venter, uten bakgrunnsjobb. Brukeren ser hvilket steg genereringen er på.

#### FR-11: Velge vanskelighetsgrad og antall
En bruker kan velge vanskelighetsgrad (lett, middels eller vanskelig) og antall spørsmål (5–30) før genereringen. Realiserer UJ-1.
- Antall utenfor 5–30 kan ikke velges.
- Standardvalg er middels og 10 spørsmål.

#### FR-12: Generere quiz
Appen lager en quiz med det valgte antallet spørsmål på valgt vanskelighetsgrad. Realiserer UJ-1.
- En PDF på 10 sider gir nøyaktig det valgte antallet spørsmål.
- Hvert spørsmål har tre ulike alternativer og nøyaktig ett riktig svar.
- Ingen to spørsmål i samme quiz er like.
- Spørsmålene er på samme språk som notatet.

#### FR-13: Sjekke formatet og generere på nytt én gang
Appen sjekker at svaret fra KI-modellen følger formatet i FR-12.
- Feil format er feil antall spørsmål, et annet antall alternativer enn tre, et annet antall riktige svar enn ett, to like alternativer eller to like spørsmål.
- Ved feil format genereres quizen på nytt én gang. Er formatet fortsatt feil, får brukeren en feilmelding og ingen quiz lagres.

#### FR-14: Vise fremdrift og låse knappen
Brukeren ser hvilket steg genereringen er på, og kan ikke starte en ny generering for samme notat før den er ferdig. Realiserer UJ-1.
- Knappen «Lag quiz» er låst fra den trykkes til genereringen er ferdig eller har feilet.
- Stegene er «Leser filen», «Lager spørsmål» og «Sjekker quizen».

#### FR-15: Timeout og «Prøv igjen»
Tar genereringen for lang tid, avbrytes den, og brukeren får knappen «Prøv igjen». Realiserer UJ-3.
- «Prøv igjen» bruker den lagrede filen og samme valg, uten ny opplasting.
- Grensen er 120 sekunder.

#### FR-16: Flere quizer per notat
En bruker kan lage flere quizer for samme notat, med samme eller ulike valg. Realiserer UJ-2.
- Hver quiz vises for seg på notatsiden med vanskelighetsgrad, antall spørsmål og dato.
- Spørsmål kan gå igjen på tvers av quizer om samme notat.
- En quiz kan ikke slettes alene. Den slettes bare sammen med emnet (FR-6).

### 4.5 Ta quiz

**Beskrivelse:** Brukeren tar quizen i appen. Svarene lagres underveis, så et forsøk kan fortsettes senere. Ved levering får brukeren poengsum og ser hvilke svar som var riktige og gale, men ikke fasiten.

#### FR-17: Svare og levere
En bruker kan svare på spørsmålene i en quiz og levere. Realiserer UJ-1.
- Brukeren kan ikke levere før alle spørsmålene er besvart. Appen viser hvilke som mangler.
- Brukeren kan endre et svar før levering.

#### FR-18: Fortsette et påbegynt forsøk
Svarene i et forsøk lagres underveis, og brukeren kan fortsette et påbegynt forsøk senere, også fra en annen enhet. Realiserer UJ-3.
- Lukker brukeren fanen etter å ha svart på halvparten, er de svarene der når hen åpner forsøket igjen.
- Påbegynte forsøk vises som «påbegynt» på notatsiden.
- Et påbegynt forsøk påvirker ikke feilbanken, dekningsgraden eller historikken.
- En quiz har høyst ett påbegynt forsøk om gangen. Starter brukeren quizen på nytt, fortsetter hen det påbegynte forsøket.

#### FR-19: Se resultat uten fasit
Etter levering ser brukeren poengsummen og om hvert svar var riktig eller galt. Realiserer UJ-1.
- Fasiten vises ikke for spørsmål som er besvart feil.
- Forsøket lagres i historikken med dato og poengsum.

#### FR-20: Ta en quiz på nytt
En bruker kan ta en quiz hen har levert, på nytt. Det gir et nytt forsøk.
- Alle leverte forsøk vises i historikken.

### 4.6 Feilbank og «Øv på feil»

**Beskrivelse:** Hvert notat har en feilbank. Spørsmål som besvares feil, havner der og blir værende til de er lært.

#### FR-21: Feilsvar havner i feilbanken
Når et forsøk leveres, legges hvert spørsmål som er besvart feil, i notatets feilbank. Realiserer UJ-1.
- Et spørsmål ligger høyst én gang i feilbanken.
- Svarer brukeren feil på et spørsmål som allerede ligger i feilbanken, nullstilles telleren for riktige svar på rad.

#### FR-22: Øv på feil
En bruker kan starte «Øv på feil» for et notat. Da får hen spørsmålene i feilbanken med alternativene i ny rekkefølge og uten fasit. Realiserer UJ-2.
- Alternativene stokkes på nytt for hver økt.
- Er feilbanken tom, er knappen låst og viser at det ikke er noe å øve på.
- Brukeren svarer på alle spørsmålene i økten og leverer. Svarene lagres underveis på samme måte som i et forsøk (FR-18).
- Økten vises ikke i historikken.

#### FR-23: Lært etter to riktige på rad
Et spørsmål er lært når det er besvart riktig to ganger på rad etter at det kom i feilbanken. Det tas da ut av feilbanken, og fasiten vises. Realiserer UJ-2.
- Et nytt feilsvar nullstiller telleren.
- Fasiten vises ikke før spørsmålet er lært.
- Svar i «Øv på feil» og i nye forsøk på den opprinnelige quizen teller begge.

### 4.7 Progresjon

**Beskrivelse:** Brukeren ser hvor godt hen kan stoffet, per notat og per emne. Dekningsgraden belønner at brukeren mestrer de vanskelige spørsmålene.

#### FR-24: Dekningsgrad per notat
Appen viser dekningsgraden for hvert notat. Realiserer UJ-2.
- For hver vanskelighetsgrad regnes andelen dekkede spørsmål av alle spørsmålene på det nivået i notatets quizer.
- Dekningsgraden er 20 % × lett + 30 % × middels + 50 % × vanskelig.
- Et nivå uten quiz teller som 0 %.
- Lett 100 %, middels 50 % og vanskelig uten quiz gir 35 %.
- Spørsmål som ennå ikke er besvart i et levert forsøk, er ikke dekket.

#### FR-25: Dekningsgrad per emne
Appen viser dekningsgraden for hvert emne som snittet av notatenes dekningsgrad, uavhengig av hvor lange notatene er. Realiserer UJ-2.
- To notater med 80 % og 40 % gir 60 % for emnet.
- Et emne uten notater viser ingen dekningsgrad.

#### FR-26: Historikk
Appen viser historikken for hvert notat, med alle leverte forsøk, dato, quiz og poengsum. Realiserer UJ-2.
- Det nyeste forsøket står øverst.

### 4.8 Testmodus og kjørbarhet

**Beskrivelse:** Sensor skal kunne kjøre hele kjerneflyten lokalt etter README-en, uten gruppas API-nøkkel, slik faglærer har bedt om. Alle data lagres lokalt i en database på maskinen.

#### FR-27: Testmodus med mock-svar
I testmodus bruker genereringen mock-svar i stedet for å kalle KI-modellen. Realiserer UJ-5.
- Mock-svarene er lagret fra ekte genereringer på testdokumentene.
- Valgt vanskelighetsgrad og antall respekteres. For hvert testdokument og hver vanskelighetsgrad er det lagret 30 spørsmål, og appen bruker de første N.
- Lastes det opp en annen fil enn et testdokument, brukes mock-svarene for et standard testdokument, og appen viser at innholdet er forhåndslagret.
- Testmodus er på når flagget for testmodus i `.env` er på, eller når det ikke finnes noen API-nøkkel.

#### FR-28: Testbruker med eksempeldata
Appen har en testbruker som sensor kan logge inn med i testmodus. Realiserer UJ-5.
- E-post og passord står i README-en.
- Testbrukeren har allerede et emne med notater, quizer, leverte forsøk og en feilbank, slik at dekningsgrad og historikk vises med en gang.

#### FR-29: Konfigurasjon i `.env`
API-nøkkel, modellnavn og testmodus settes i `.env`. Repoet har `.env.example`.
- Standardmodellen er Claude Sonnet 5.5. Den kan byttes til en annen Anthropic-modell ved å endre modellnavnet.
- `.env` med ekte nøkkel ligger ikke i repoet.

#### FR-30: README for lokal kjøring
README-en beskriver hvordan appen installeres og kjøres lokalt, hvordan sensor logger inn som testbrukeren, og hvordan sensor eventuelt legger inn sin egen nøkkel for å teste med ekte modell.
- Med en ny klone og README-en kjører hele kjerneflyten i testmodus uten API-nøkkel.

## 5. Tverrgående krav og regelverk

### 5.1 Tverrgående krav (NFR)

- **NFR-1 Mobil:** Quiz, «Øv på feil», feilbank og historikk kan brukes på en skjerm som er 360 px bred, uten vannrett rulling.
- **NFR-2 Sikkerhet:** Passord lagres bare som hash. Alle sider unntatt innlogging og registrering krever innlogging. Tilgang sjekkes på eier for hver forespørsel (se FR-3).
- **NFR-3 Personvern:** Filer og data lagres bare lokalt i appens database og filområde. Innhold sendes bare til KI-tjenesten ved generering, og aldri i testmodus.
- **NFR-4 Lokal kjøring:** Appen krever ingen betalte kontoer, ingen eksterne tjenester utenom KI-modellen og ingen database-server.
- **NFR-5 KI-kall samlet:** Alle kall til KI-modellen går gjennom én modul, slik at modell, prompt og testmodus styres ett sted.
- **NFR-6 Språk:** Grensesnittet er på norsk. Quizen lages på notatets språk.
- **NFR-7 Sporbar KI-kvalitet:** Hver quiz lagrer hvilken modell og prompt-versjon som laget den.

### 5.2 Universell utforming (WCAG 2.2)

**NFR-8:** Alle sider oppfyller WCAG 2.2 på nivå A og AA. Det er den nyeste versjonen av standarden. Konkret betyr det blant annet:
- Hele kjerneflyten kan gjøres med bare tastatur: registrere, logge inn, laste opp, lage quiz, svare, levere og øve på feil.
- Fokus er alltid synlig og skjules ikke av andre elementer (2.4.7, 2.4.11).
- Klikkflater er minst 24 × 24 px (2.5.8). Svaralternativene er radioknapper med etikett, ikke bare farge.
- Tekst har kontrast på minst 4,5:1, og store tekster og grensesnittelementer minst 3:1 (1.4.3, 1.4.11).
- Riktig og galt vises med tekst eller ikon i tillegg til farge (1.4.1).
- Innloggingen godtar innliming og passordbehandlere og krever ingen kognitiv test (3.3.8).
- Feilmeldinger, for eksempel ved avvist fil eller manglende svar, vises som tekst ved feltet og leses opp av skjermleser (3.3.1, 4.1.3).
- Fremdriften under generering og resultatet etter levering meldes til skjermleser som statusmeldinger (4.1.3).
- Sidene har `lang="no"`. Spørsmålene merkes med notatets språk når det ikke er norsk (3.1.1, 3.1.2).
- Siden fungerer med 200 % tekstforstørrelse og ved 320 px bredde uten vannrett rulling (1.4.4, 1.4.10).
- Ingen funksjon krever dra-og-slipp. Opplasting kan alltid gjøres med en vanlig filvelger (2.5.7).

**Slik følger BMAD dette opp:** UX-spesifikasjonen (`bmad-ux`) beskriver hvordan hvert skjermbilde oppfyller NFR-8. Hver story med grensesnitt har akseptansekriterier for universell utforming, og kodegjennomgangen sjekker dem før storyen er ferdig.

### 5.3 EU AI Act

Gruppa vurderer appen som et KI-system med *begrenset risiko* (nivå 3 av 4). Det betyr at den har krav om åpenhet. Appen er ikke et høyrisikosystem for utdanning, fordi den ikke vurderer læringsutbytte med KI. KI lager bare spørsmålene. Retting, poengsum, feilbank og dekningsgrad er faste regler i koden.

**NFR-9 Merking av KI-innhold:** Brukeren får tydelig beskjed om at quizene er laget av KI.
- Hver quiz er merket «Laget av KI» der den vises, på notatsiden, mens den tas og i «Øv på feil».
- Merkingen gjelder også i testmodus, fordi mock-svarene kommer fra ekte genereringer.
- Merkingen sier hvilken modell som laget quizen (NFR-7), og at spørsmålene kan inneholde feil.
- Vilkårene opplyser om det samme (FR-7).

## 6. Ikke-mål

- Appen er ikke en chatbot og svarer ikke på spørsmål om stoffet.
- Appen lager ikke sammendrag, begrepslister eller noe annet enn quizer i v1.
- Appen hostes ikke offentlig i v1. Den kjøres lokalt.
- Appen deler ikke data mellom brukere og har ingen roller.
- Ingenting kan lastes ned fra appen.

## 7. Omfang

### 7.1 Med i v1

Alt i kap. 4: konto, emner, opplasting med vilkår, quizgenerering med formatsjekk, quiz med lagring underveis, feilbank og «Øv på feil», dekningsgrad og historikk, testmodus og README. I tillegg kommer kravene i kap. 5, blant annet universell utforming etter WCAG 2.2 og merking av KI-innhold etter AI Act.

### 7.2 Ikke med i v1 (videre arbeid)

- **Sammendrag og begrepsliste:** Flyttet ut av v1 av gruppa 11.11.
- **Valg av detaljnivå:** Følger sammendraget.
- **Temaer innen et emne:** Notater og quizer kan grupperes i temaer. For eksempel kan HTML, CSS og JavaScript i emnet webutvikling samles i temaet «programmeringsspråk».
- **Videre læring:**
  - KI-genererte oppfølgingsquizer om temaene studenten bommet på
  - flagg der studenten markerer et tema som vanskelig
  - samlet øving per emne
  - intervall-repetisjon
- **Kvalitetskontroll:** En egen KI-modell som kontrollerer spørsmålene automatisk.
- **Bakgrunnsjobb:** Genereringen fortsetter når fanen lukkes.
- **Hosting:** Med bruksgrense (f.eks. 10 genereringer per døgn) og utgiftstak.
- **Konto:** Glemt passord, endring av passord og sletting av konto.
- **Flere formater:** PPTX, bilder og ZIP-opplasting. Studenten eksporterer til PDF.
- **Annet:**
  - Feide/SSO
  - andre KI-leverandører enn Anthropic
  - samlet score på tvers av emner
  - sletting av et enkelt notat eller en enkelt quiz

## 8. Suksessmål

**Hovedmål**
- **SM-1 Kjørbarhet:** Med en ny klone og README-en kjører hele kjerneflyten i testmodus uten API-nøkkel. Validerer FR-27 til FR-30.
- **SM-2 KI-kvalitet:** Testdokumentene kjøres med ekte modell. Gruppa vurderer hvert spørsmål manuelt, og minst 90 % av spørsmålene skal være relevante, ha riktig fasit og ikke være tvetydige. Resultatet dokumenteres med modell, dato og prompt-versjon. Validerer FR-9, FR-12 og NFR-7.
- **SM-3 Læringssløyfen virker:** Alle konsekvensene i FR-17 til FR-25 har automatiske tester som passerer. Det gjelder blant annet feilbank, to riktige på rad, nullstilling og regneeksempelet på 35 %.

**Delmål**
- **SM-4 Format:** Alle quizer fra testdokumentene har nøyaktig det valgte antallet spørsmål, tre ulike alternativer, ett riktig svar og ingen like spørsmål. Validerer FR-12 og FR-13.
- **SM-5 Tilgang:** Ingen bruker får tilgang til andres data ved å endre ID-er i URL-en. Det testes for alle sider. Validerer FR-3.
- **SM-6 Brukertest:** 3–5 medstudenter har testet appen, og funnene er dokumentert. Minst én av dem har tatt et påbegynt forsøk videre på mobil. Validerer FR-18 og NFR-1.
- **SM-7 Universell utforming:** Et automatisk verktøy (f.eks. axe) finner ingen brudd på WCAG 2.2 A/AA på noen side. En manuell test viser at hele kjerneflyten kan gjøres med bare tastatur og med skjermleser. Validerer NFR-8.
- **SM-8 KI-merking:** Alle sider som viser en quiz, har merkingen «Laget av KI». Validerer NFR-9.

**Motmål (skal ikke optimaliseres)**
- **SM-C1 Høy poengsum:** Lette spørsmål gir høye poengsummer uten læring. Dekningsgraden er vektet mot de vanskelige spørsmålene for å motvirke dette. Motvekt til SM-3.
- **SM-C2 Rask generering:** Raskere generering med svakere modell eller kortere prompt skal ikke gå på bekostning av SM-2.
- **SM-C3 Antall funksjoner:** Flere halvferdige funksjoner er ikke et mål. En stram, testet sløyfe veier tyngre. Motvekt til omfangspress.

## 9. Åpne spørsmål

Spørsmålene blokkerer ikke arkitektur eller stories. Gruppa avgjør dem i testfasen.

1. Hva er billigst og best: å sende hele PDF-en eller å hente ut teksten? Og holder Haiku 5.5 kvaliteten mot Sonnet 5.5? Begge deler avgjøres i testfasen.
2. Hvilke testdokumenter kan brukes uten å bryte opphavsretten?
3. Hvor lang er en typisk generering av 30 spørsmål? Svaret avgjør om grensen i FR-15 holder.

**Avklart i møtet 11.11:** Fristen er 15.12.2026 kl. 15:00. Dekningsgraden for et emne er snittet av notatene.

## 10. Antakelser bekreftet av gruppa

Gruppa bekreftet disse antakelsene i møtet 11.11.2026. De står som krav i kap. 4.

- §4.1 FR-1: Passordet må ha minst 8 tegn.
- §4.2 FR-4: Et emnenavn må være unikt per bruker.
- §4.4 FR-11: Standardvalg er middels og 10 spørsmål.
- §4.4 FR-14: Stegene i fremdriften er «Leser filen», «Lager spørsmål» og «Sjekker quizen».
- §4.4 FR-15: Grensen for timeout er 120 sekunder.
- §4.5 FR-18: En quiz har høyst ett påbegynt forsøk om gangen.
- §4.5 FR-20: En levert quiz kan tas på nytt som et nytt forsøk.
- §4.6 FR-22: En økt med «Øv på feil» lagres underveis som et forsøk, men vises ikke i historikken.
- §4.6 FR-23: Svar i «Øv på feil» og i nye forsøk på den opprinnelige quizen teller begge mot «to riktige på rad».
- §4.7 FR-24: Spørsmål som ikke er besvart i et levert forsøk, er ikke dekket.
- §4.8 FR-27: Mock-svar har 30 spørsmål per testdokument og vanskelighetsgrad, og appen bruker de første N.
- §4.8 FR-27: En ukjent fil i testmodus får mock-svarene for et standard testdokument, med en melding om det.
- §4.8 FR-28: Testbrukeren har ferdige eksempeldata.
