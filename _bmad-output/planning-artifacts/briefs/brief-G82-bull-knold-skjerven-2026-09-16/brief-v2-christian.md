---
title: "Product Brief v2: Foredragsnotater → Sammendrag & Quiz"
status: draft
version: 2
author: Christian R Bull (individuelt utkast)
created: 2026-10-26
updated: 2026-10-26
based_on: brief.md (v1, 2026-09-16) og tilbakemelding-product-brief.md (2026-10-06)
---

# Product Brief v2: Foredragsnotater → Sammendrag & Quiz

> Individuelt utkast fra Christian. Bygger på v1 av briefen og faglærerens tilbakemelding. Utkastene fra gruppemedlemmene slås sammen til én felles v2.

## Endringer fra v1

| Endring | Begrunnelse (fra tilbakemeldingen) |
|---|---|
| v1 utvides med interaktiv quiz i appen: poeng, «øv på feil» og historikk per opplastet notat | Omfanget var lite for fire personer. Utvidelsen gir egen logikk og mer å teste. |
| Kurs-FAQ-chatboten (forslag 7) er tatt ut av planen, også som strekkmål | Den er et eget, middels vanskelig produkt. Tiden brukes heller på kvalitet og testing. |
| Innlogging er bestemt: e-post og passord | Feide/SSO er mye mer krevende og frarådes i v1. |
| Språkmodell er foreslått (Claude Sonnet 5.5), med modellvalg som kan byttes i konfigurasjonen | Modell og kostnad måtte planlegges nå. |
| Ny seksjon om kjørbarhet: testmodus med mock-svar, `.env.example`, testbruker og faste testdokumenter | Sensor må kunne kjøre appen uten gruppens nøkler. |
| Ny seksjon om kvalitetssikring av KI-svar i tre nivåer | Briefen manglet en plan for å kontrollere det KI-en lager. |
| Plan for PDF-er som er lysbilder: sendes direkte til modellen i stedet for egen tekstuttrekking | Lysbildebaserte PDF-er gir ofte rotete tekst. |
| Plan for ventetid: generering i bakgrunnen med synlig status, og sammendraget vises før quizen | Faglæreren ba gruppen tenke på ventetid mens KI-en genererer. |
| Overordnet datamodell med sju tabeller. Status per spørsmål regnes ut fra svarene. | Datamodellen må tåle historikk per notat uten å bli mer kompleks enn nødvendig. |
| Primærbrukeren er beskrevet konkret, med konsekvenser for språk, mobil og brukertest | Designet trenger en tydelig bruker å bygges rundt. |
| Sletting av notat med alle tilhørende data, og melding om at innhold sendes til ekstern KI-tjeneste | Notater kan være kursbeskyttet og sendes til en ekstern tjeneste. |
| Suksesskriteriene er skrevet om til konkrete, testbare kriterier per funksjon | «Fullt fungerende» og «oppleves som representative» kunne ikke sjekkes. |
| Lokale filstier og avsnittet om det separate backend-skjelettet er fjernet | De sa ingenting for andre som leser briefen. |
| Avklarte [ASSUMPTION]-punkter er lukket | Historikken skal vise hvordan planen har utviklet seg. |

## Executive Summary

Studenter samler store mengder forelesningsnotater gjennom et semester, men å repetere dem effektivt før eksamen er noe annet. Dette prosjektet er en nettapplikasjon der studenten laster opp forelesningsnotater (PDF, tekst eller Word) og får tilbake et sammendrag, en begrepsliste og en quiz generert av en språkmodell. Quizen tas direkte i appen: studenten får poeng, kan øve på nytt på spørsmålene hen fortsatt svarer feil på, og ser historikken sin for hvert notat. Målet er en aktiv, testbasert måte å repetere pensum på, i stedet for å lese notatene på nytt.

Prosjektet bygger på forslag 8 i IBE160-kursets prosjektliste («Foredragsnotater → Sammendrag & Quizgenerator»). Gruppe G82 (Christian R Bull, Henrik L Knold, Martin Skjerven og Magnus Gjerstad) lager det som semesteroppgave i «Programmering med KI». Planleggingen gjøres med BMAD, og koden skrives med Claude Code. Innleveringen er midt i desember 2026 **[ASSUMPTION: eksakt dato ikke bekreftet, antatt 15. desember 2026]**.

## Problemet

Forelesningsnotater er laget for å *ta imot* informasjon, ikke for å *repetere* den. Å lese lange PDF-er på nytt før eksamen er tidkrevende og passivt. Det gir gjenkjenning, men ikke nødvendigvis forståelse. Aktiv gjenkalling, for eksempel gjennom quizspørsmål, er en velkjent og effektiv læringsteknikk. Men å lage gode spørsmål fra egne notater tar tid som få studenter har midt i semesteret. Og selv med en quiz vet studenten sjelden hvilke deler av stoffet hen faktisk ikke kan.

Resultatet er at mange repeterer mindre effektivt enn de kunne, og bruker tid på stoff de allerede kan i stedet for på det de ikke kan.

## Løsningen

En webapplikasjon der studenten:

1. **Oppretter konto og logger inn** med e-post og passord. Notatene og resultatene er bare synlige for eieren.
2. **Laster opp forelesningsnotater** som PDF, tekst (`.txt`) eller Word (`.docx`). PDF-er kan være vanlige notater, eksporterte lysbilder eller skannede sider. Opplastingssiden minner kort om at innholdet sendes til en ekstern KI-tjeneste, og at studenten bare skal laste opp materiale hen har lov til å bruke.
3. **Velger preferanser:** detaljnivå på sammendraget (kort / middels / detaljert), vanskelighetsgrad (lett / middels / vanskelig) og antall quizspørsmål.
4. **Får generert** et sammendrag, en begrepsliste med korte forklaringer og en quiz der hvert spørsmål har tre svaralternativer og ett riktig svar. Genereringen går i bakgrunnen. Studenten ser hvilket steg appen er på, og kan lese sammendraget mens quizen lages (se under). Innholdet er merket som KI-generert og kan inneholde feil. Det genererte innholdet får samme språk som notatet (for eksempel engelsk for engelske lysbilder), mens grensesnittet er på norsk.
5. **Tar quizen i appen.** Studenten svarer på ett og ett spørsmål og får til slutt poengsum og fasit, med markering av hva som var riktig og galt.
6. **Øver på feil.** Studenten kan starte en øvingsrunde med alle spørsmålene i notatet som hen fortsatt svarer feil på, helt til alle er riktige (se under).
7. **Ser historikk per notat:** alle forsøk med dato og poengsum, slik at det er lett å se fremgang.
8. **Rapporterer feil spørsmål.** Et spørsmål som virker feil eller uklart, kan markeres. Markeringen lagres, slik at gruppen kan bruke den i kvalitetssjekken.
9. **Sletter et notat** når hen vil. Da slettes også filen og alt som er generert og lagret for notatet.

Quiz, «øv på feil» og historikk skal fungere på mobilskjerm. Opplasting kan forutsette pc.

### «Øv på feil»: status per spørsmål

Hvert spørsmål har status **riktig** eller **feil** etter siste gang det ble besvart, uansett om det var i en hel quiz eller i en øvingsrunde. «Øv på feil» gir alle spørsmålene i notatet som nå står som feil.

Eksempel med en quiz på 10 spørsmål:

1. Hel quiz: studenten svarer feil på A, B og C. «Øv på feil» gir da A, B og C.
2. Øvingsrunde: A blir riktig, mens B og C fortsatt er feil. Neste runde gir B og C.
3. Ny hel quiz: B blir riktig, men D blir feil. Neste runde gir C og D.
4. Når ingen spørsmål står som feil, er «øv på feil» stengt, og studenten får beskjed om at alt er riktig.

Svaralternativene vises i ny rekkefølge i hver øvingsrunde, slik at studenten ikke bare husker hvor det riktige svaret sto.

Poengsum, status per spørsmål og hva som er med i en øvingsrunde regnes ut i appens egen kode. Språkmodellen lager bare innholdet. Repetisjon med intervaller (spaced repetition) er bevisst holdt utenfor v1, se **Visjon**.

### Håndtering av filer

| Filtype | Hva appen gjør |
|---|---|
| PDF | Sendes direkte til språkmodellen, som leser både teksten og et bilde av hver side. Lysbilder og skannede sider kan dermed brukes uten egen tekstuttrekking eller tekstgjenkjenning (OCR). |
| Word (`.docx`) og tekst (`.txt`) | Teksten trekkes ut lokalt og sendes som tekst. |

- Før noe sendes til modellen, sjekker appen lokalt filtype, filstørrelse og antall sider i PDF-er. Filer over grensene blir avvist. Det holder kostnad og ventetid nede. **[ASSUMPTION: forslag 10 MB og 50 sider, settes endelig i arkitekturen]**
- Appen advarer når stoffet er for tynt, ikke ut fra filformatet. Svaret fra modellen inneholder et felt som sier om stoffet holder til det valgte antallet spørsmål. Hvis ikke, lagres ingen quiz, og studenten blir bedt om å velge færre spørsmål eller laste opp mer materiale.
- PowerPoint-filer (`.pptx`) støttes ikke direkte. Appen gir et tips om å eksportere til PDF først.

### Mens KI-en genererer

En generering kan ta 30 sekunder eller mer. Derfor går den i bakgrunnen og har en status:

1. **Opplastingen svarer med én gang.** Serveren lagrer notatet med status «Genererer» og gjør jobben i bakgrunnen. Nettleseren spør etter status med noen sekunders mellomrom.
2. **To kall i stedet for ett.** Først sammendrag og begrepsliste, deretter quizen. Studenten kan begynne å lese sammendraget mens quizen lages. Det koster litt mer fordi dokumentet sendes to ganger, men prompt-caching reduserer det.
3. **Ærlige steg, ikke en falsk prosentlinje:** Fil lest ✓ → Lager sammendrag … → Lager quiz … → Ferdig. I tillegg vises tid brukt og teksten «Dette tar vanligvis 20–60 sekunder».
4. **Studenten kan gå fra siden.** I listen over notater står «Genererer …», og resultatet ligger klart når studenten kommer tilbake.
5. **Ingen dobbel generering.** Knappen er låst mens appen jobber, og serveren avviser en ny generering for samme notat mens en kjører.
6. **Tidsgrense og ny sjanse.** Etter en tidsgrense får notatet status «Feilet», med en forståelig melding og knappen «Prøv igjen». Er sammendraget allerede ferdig, beholdes det, og bare quizen lages på nytt. **[ASSUMPTION: forslag 3 minutter, settes i arkitekturen]**

Strømming av tekst mens den skrives og en avbryt-knapp er holdt utenfor v1. Quizen kommer som JSON og kan ikke vises før den er ferdig, og en avbryt-knapp gir lite i forhold til jobben med å bygge den.

### Språkmodell

- **Forslag: Claude Sonnet 5.5** (`claude-sonnet-5-5`).
  - Den største risikoen er feil fasit og spørsmål som ikke står i notatet. Da lønner det seg å bruke en sterk modell.
  - Kostnaden er lav. Et notat på 10 sider koster omtrent $0,07 per generering. En lysbilde-PDF på 30 sider koster omtrent $0,10 til $0,20, fordi bildet av hver side også telles. Tallene er grove anslag basert på listepris.
- Modellen settes i konfigurasjonen (for eksempel `LLM_MODEL` i `.env`), ikke i koden. Gruppen kjører de faste testdokumentene gjennom både Sonnet 5.5 og den billigere Haiku 5.5, og velger ut fra resultatet i kvalitetssjekken. Valget og begrunnelsen dokumenteres.
- Alle kall til språkmodellen samles i én modul, slik at modellen kan byttes og testes isolert.
- Quiz og begrepsliste hentes som strukturert utdata låst til et JSON-skjema.

### Kvalitetssikring av KI-svar

Kvalitetssikringen skjer på tre nivåer:

1. **Format: automatisk, ved hver generering.**
   - Appen validerer at antall spørsmål er det studenten valgte, at hvert spørsmål har tre ulike alternativer og nøyaktig ett riktig svar, og at ingen felt er tomme.
   - Hvis svaret er ugyldig, prøver appen én gang til. Feiler det igjen, lagres ingenting, og brukeren får en forståelig feilmelding.
   - Dette testes automatisk med mock-svar, også bevisst ødelagte svar.
2. **Egen logikk: automatisk, uten KI.** Poengsum, status per spørsmål, «øv på feil» og historikk er vanlig kode som dekkes av enhetstester.
3. **Innhold: manuelt, med ekte modell.**
   - Testdokumentene kjøres på nytt hver gang prompten eller modellen endres.
   - Hvert spørsmål vurderes mot en sjekkliste:
     1. Svaret finnes i notatet.
     2. Fasiten er riktig.
     3. De gale alternativene er tydelig gale.
     4. Spørsmålet er ikke tvetydig.
   - For hvert begrep sjekkes det at det står i notatet og er forklart riktig.
   - Resultatet føres i en tabell i repoet, med modell, dato og prompt-versjon.

Gruppen bruker ikke en annen språkmodell som automatisk dommer og bygger ikke automatisk faktasjekk. Begge deler gjør løsningen mer komplisert uten å fjerne behovet for at mennesker kontrollerer innholdet.

### Kjørbarhet

- **Testmodus med mock-svar:** Appen kan kjøres uten API-nøkkel. Da brukes faste, forhåndsdefinerte svar i stedet for kall til språkmodellen. Modus velges med en miljøvariabel. Testmodus har en kunstig forsinkelse på noen sekunder, som kan stilles inn, slik at ventetilstanden kan vises i en demo og testes.
- `.env.example` i repoet viser hvilke miljøvariabler som trengs. Ekte nøkler ligger aldri i repoet.
- En **testbruker** opprettes automatisk ved oppstart i testmodus, og innloggingsdetaljene står i README.
- **Faste testdokumenter** ligger i repoet og brukes både i automatiske tester og i den manuelle kvalitetssjekken:
  - en vanlig PDF med notater
  - en lysbilde-PDF som gruppen selv har eksportert fra PowerPoint
  - en `.docx`-fil
  - en `.txt`-fil
  - minst ett dokument på engelsk

### Datamodell (overordnet)

| Tabell | Innhold | Kobling |
|---|---|---|
| **Bruker** | e-post, passord-hash, opprettet | |
| **Notat** | originalfil, filnavn, filtype, antall sider, opplastet, preferanser (detaljnivå, vanskelighetsgrad, antall spørsmål), genereringsstatus og eventuell feilmelding, sammendrag | tilhører én bruker |
| **Begrep** | begrep, forklaring | tilhører ett notat |
| **Spørsmål** | spørsmålstekst, tre alternativer i fast rekkefølge, hvilket som er riktig | tilhører ett notat |
| **Forsøk** | type (hel quiz eller «øv på feil»), tidspunkt, poengsum | tilhører ett notat |
| **Svar** | valgt alternativ, riktig eller feil | tilhører ett forsøk og ett spørsmål |
| **Rapport** | kommentar, tidspunkt | tilhører ett spørsmål og én bruker |

Tre valg holder modellen enkel og riktig:

1. **Status per spørsmål lagres ikke.** Den regnes ut fra det siste svaret på hvert spørsmål. Da finnes det bare én kilde til sannhet, og status og historikk kan aldri bli uenige.
2. **Svaret lagrer hvilket alternativ som ble valgt, ikke hvor det sto på skjermen.** Alternativene stokkes i hver øvingsrunde, så plasseringen på skjermen betyr noe forskjellig fra gang til gang.
3. **Én generering per notat, uten versjoner.** «Prøv igjen» gjelder bare en generering som har feilet. Vil studenten ha en ny quiz, laster hen opp notatet på nytt.

Originalfilen lagres, slik at «Prøv igjen» kan sende den til modellen på nytt. Når et notat slettes, slettes alt som hører til det. Felttyper og databasevalg bestemmes i arkitekturen.

## Hva gjør dette annerledes

Dette konkurrerer ikke med generelle «last opp PDF, få sammendrag»-verktøy. Det som skiller det ut:

- **Fra notat til øving i én flyt.** Sammendrag, begrepsliste og quiz lages fra samme kilde, og quizen tas og rettes i appen.
- **Øving rettet mot det studenten ikke kan.** Status per spørsmål og «øv på feil» gjør repetisjonen målrettet i stedet for generell.
- **Tilpasset studenthverdagen.** Bygget for forelesningsnotater og lysbilder, og for eksamensøving, ikke for generelle dokumenter.

Det er ikke teknisk unikt. Verdien ligger i en stram, velfungerende kjerneopplevelse fremfor mange halvferdige funksjoner.

## Hvem dette er for

Appen bygges for studenter generelt, men designes og testes med studenter i eget kurs.

- **Generell i det tekniske.** Ingenting i appen forutsetter et bestemt kurs, fag eller lærested. Derfor brukes e-post og passord i stedet for Feide, og notater ordnes ikke etter kurs eller emne.
- **Konkret i designet.** Skjermbilder og flyt designes for primærbrukeren under, og prøves ut på medstudenter.

**Primærbruker:** En bachelorstudent som har fått lysbilder og notater fra forelesninger, som PDF fra læringsplattformen eller egne notater i Word. Mye av pensum er på engelsk. Hen vil repetere i korte økter: forbereder seg på pc-en, og tar gjerne quizen på mobilen på bussen eller mellom forelesninger. Hen har ikke tid til å lage spørsmål selv, og vil vite hva hen ikke kan.

Suksess for brukeren: Hen laster opp notater eller lysbilder fra en forelesning, får sammendrag og quiz uten å måtte forstå noe teknisk, tar quizen og ser hva hen må øve mer på.

Dette betyr for løsningen:

- Grensesnittet er på norsk, og det genererte innholdet får samme språk som notatet.
- Quiz, «øv på feil» og historikk fungerer på mobilskjerm.
- Opplastingssiden minner om at innholdet sendes til en ekstern KI-tjeneste, og at studenten bare skal laste opp materiale hen har lov til å bruke.
- Tre til fem medstudenter prøver appen med egne notater før innlevering. Funnene og endringene dokumenteres i repoet.
- Appen kjøres lokalt. Offentlig drift og hosting er ikke en del av prosjektet.

Det er ingen sekundærbrukere eller admin-roller i v1.

## Suksesskriterier

Kriteriene er formulert slik at de kan bli testtilfeller. «Testmodus» betyr at appen kjører med mock-svar.

### Innlogging og tilgang
- En ny bruker kan registrere seg med e-post og passord og deretter logge inn.
- Registrering med en e-post som allerede finnes, gir feilmelding, og det opprettes ingen ny konto.
- Innlogging med feil passord blir avvist.
- Passord lagres aldri i klartekst.
- En bruker får ikke tilgang til en annen brukers notater, sammendrag, quizer eller historikk, verken via grensesnittet eller ved å endre ID-er i URL eller API-kall.
- Sider som krever innlogging, sender en utlogget bruker til innloggingssiden.

### Opplasting
- Hvert av de faste testdokumentene (vanlig PDF, lysbilde-PDF, `.docx` og `.txt`) blir lastet opp og gir generert innhold uten feil.
- En fil i et format som ikke støttes (for eksempel `.pptx` eller `.png`), blir avvist med en forståelig feilmelding. For `.pptx` foreslår feilmeldingen å eksportere til PDF.
- En tom eller ødelagt fil blir avvist med en forståelig feilmelding.
- En fil over grensen for størrelse, eller en PDF med flere sider enn grensen, blir avvist før den sendes til språkmodellen.
- Opplastingssiden viser en melding om at innholdet sendes til en ekstern KI-tjeneste.

### Generering av sammendrag, begrepsliste og quiz
- For en PDF på 10 sider fra testdokumentene gir genereringen en quiz med nøyaktig det valgte antallet spørsmål. Hvert spørsmål har nøyaktig tre ulike alternativer og nøyaktig ett riktig svar.
- Begrepslisten inneholder minst ett begrep, og hvert begrep har en forklaring.
- Sammendraget er ikke tomt, og valgt detaljnivå gir målbar forskjell i lengde (kort < middels < detaljert, målt i antall ord på testdokumentene).
- Et svar fra språkmodellen som ikke følger formatet, blir avvist av valideringen og lagres ikke. Appen prøver én gang til før brukeren får en feilmelding.
- Når modellen melder at stoffet er for tynt til valgt antall spørsmål, lagres ingen quiz, og brukeren får en forklaring.
- Ved feil fra språkmodellen (tidsavbrudd, ugyldig nøkkel) får brukeren en forståelig feilmelding, og appen krasjer ikke.
- Modellen kan byttes ved å endre konfigurasjonen, uten endringer i koden.
- Et engelsk testdokument gir sammendrag, begrepsliste og quiz på engelsk. Et norsk testdokument gir dem på norsk.

### Ventetid under generering
- Opplasting gir svar til brukeren innen 2 sekunder, og notatet får status «Genererer».
- Grensesnittet viser hvilket steg genereringen er på, og hvor lang tid som er brukt.
- Sammendrag og begrepsliste vises før quizen er ferdig.
- En ny generering for samme notat mens en allerede kjører, blir avvist.
- En generering som overskrider tidsgrensen, får status «Feilet» med knappen «Prøv igjen», og ferdige deler beholdes.
- Studenten kan forlate siden og finne ferdig resultat i listen over notater senere.

### Interaktiv quiz og poeng
- Poengsummen er lik antall riktige svar, og vises som for eksempel «7 av 10».
- Etter levering vises riktig svar for hvert spørsmål, og hvert svar studenten ga, er markert som riktig eller galt.
- Et forsøk der ikke alle spørsmål er besvart, kan ikke leveres. **[ASSUMPTION: alternativt telles ubesvarte som feil, avklares i PRD]**
- Et spørsmål kan rapporteres som feil eller uklart, og rapporten lagres med spørsmålet.

### Øv på feil
- Hvert spørsmål har status riktig eller feil etter siste gang det ble besvart, uansett om det var i en hel quiz eller i en øvingsrunde.
- «Øv på feil» gir nøyaktig spørsmålene i notatet som nå står som feil, og ingen andre.
- Et spørsmål som besvares riktig i en øvingsrunde, er ikke med i neste runde.
- Et spørsmål som tidligere var riktig, men som besvares feil i en ny hel quiz, er med i neste øvingsrunde.
- Når ingen spørsmål står som feil, er «øv på feil» ikke tilgjengelig, og studenten får en melding om at alt er riktig.
- Svaralternativene vises i ny rekkefølge i hver øvingsrunde. De samme tre alternativene og det samme riktige svaret er med.
- Status per spørsmål regnes ut fra siste svar og gir samme resultat som eksemplet under **«Øv på feil»: status per spørsmål**.
- Svar lagres med hvilket alternativ som ble valgt, slik at poengsummen er riktig uansett rekkefølgen på skjermen.

### Historikk per notat
- Hvert levert forsøk lagres med dato, type (hel quiz eller «øv på feil») og poengsum.
- Historikken for et notat viser alle forsøk på det notatet, nyeste først, og ingen forsøk fra andre notater.
- Historikk og status per spørsmål er lagret etter utlogging og ny innlogging.

### Sletting
- Når et notat slettes, slettes også fil, sammendrag, begreper, spørsmål, forsøk, svar og rapporter som hører til det.
- Andre notater, også notater fra samme bruker, påvirkes ikke.

### Design og brukeropplevelse
- Quiz, «øv på feil» og historikk kan brukes på mobilskjerm (360 px bred) uten vannrett rulling.
- Minst tre medstudenter har testet appen med egne notater. Funnene og endringene er dokumentert i repoet.

### Kjørbarhet for sensor
- Med en ny klone av repoet og bare stegene i README kan appen startes i testmodus uten API-nøkkel og uten betalte kontoer.
- I testmodus kan testbrukeren logge inn, laste opp et testdokument, generere innhold, ta quizen, øve på feil og se historikk. Hele kjerneflyten fungerer.
- `.env.example` finnes og dekker alle miljøvariabler appen leser.
- Repoet inneholder ingen ekte API-nøkler eller passord.

### Kvalitet på generert innhold (manuell sjekk med ekte modell)
- Alle de faste testdokumentene, også lysbilde-PDF-en, er kjørt gjennom den ekte modellen og vurdert etter sjekklisten under **Kvalitetssikring av KI-svar**.
- Minst 90 % av quizspørsmålene består sjekklisten.
- Resultatet er dokumentert i repoet med modell, dato og prompt-versjon.
- Valget mellom Sonnet 5.5 og Haiku 5.5 er begrunnet med resultatene.

## Scope

**Inn i v1:**
- Registrering og innlogging med e-post og passord
- Opplasting av PDF (også lysbilder og skannede sider), `.txt` og `.docx`
- Preferanser: detaljnivå, vanskelighetsgrad, antall quizspørsmål
- Generert sammendrag, begrepsliste og quiz (tre alternativer, ett riktig, med fasit)
- Generering i bakgrunnen med synlig status, sammendrag før quiz, tidsgrense og «Prøv igjen»
- Interaktiv quiz i appen med retting og poeng
- «Øv på feil» med status per spørsmål og ny rekkefølge på svaralternativene
- Historikk med forsøk og poeng per opplastet notat
- Rapportering av feil eller uklare spørsmål
- Sletting av notat med alle tilhørende data
- Generert innhold på samme språk som notatet (norsk eller engelsk)
- Quiz, «øv på feil» og historikk tilpasset mobilskjerm
- Brukertest med minst tre medstudenter
- Modellvalg i konfigurasjonen, med validering av formatet på KI-svar
- Testmodus med mock-svar, `.env.example`, testbruker og faste testdokumenter
- Automatiske tester for kriteriene over, og en dokumentert manuell kvalitetssjekk

**Ut av v1:**
- Kurs-FAQ-chatbot (forslag 7). Tatt ut av planen, også som strekkmål.
- Repetisjon med intervaller (spaced repetition)
- Strømming av generert tekst og avbryt-knapp under generering
- Versjonering av genereringer, og «lag ny quiz» for samme notat
- Organisering av notater i kurs, emner, mapper eller tagger
- Feide/SSO og andre innloggingsløsninger
- Direkte opplasting av PowerPoint (`.pptx`) og bilder. Studenten eksporterer til PDF.
- Egen tekstgjenkjenning (OCR). Skannede PDF-er håndteres av språkmodellen.
- Automatisk faktasjekk eller en annen språkmodell som dommer over innholdet
- Deling av quizer mellom brukere, lærerroller og admin-grensesnitt
- Offentlig lansering, drift og hosting. Appen kjøres lokalt.
- Kjøp eller betaling

## Visjon

Målet for semesteret er en solid, godt testet og godt dokumentert studieapp som gjør nøyaktig det briefen beskriver, og som sensor kan kjøre selv.

Dersom gruppen vil bygge videre etter semesteret, er naturlige neste steg:
- repetisjon med intervaller basert på historikken og statusen per spørsmål som allerede lagres
- eksport av quizer

Ingen av delene er med i denne planen.

## Åpne spørsmål

- Gir Sonnet 5.5 målbart bedre kvalitet enn Haiku 5.5 på testdokumentene? Avgjøres med kvalitetssjekken før endelig valg.
- Hva er eksakt innleveringsfrist? Antatt 15. desember 2026, bør bekreftes mot emneplanen.
- Skal ubesvarte spørsmål hindre levering eller telles som feil?
- Hva skal grensene være for filstørrelse, antall sider og antall quizspørsmål?
- Hvilke forelesningsnotater kan brukes som faste testdokumenter uten å bryte opphavsrett? Forslag: notater og lysbilder gruppen lager selv, eller åpent lisensiert materiale.
