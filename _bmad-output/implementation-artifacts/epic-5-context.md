# Epic 5 Context: Se progresjonen

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->
<!-- Kompilert 25.11.2026, etter at Martins design ble felles UX (23.11), og etter at Epic 1–4 er bygget (unntatt 4.3). -->

## Goal

Studenten ser hvor mye av stoffet hen kan: dekningsgraden per notat med fordeling på lett, middels og vanskelig (S7), dekningsgraden per emne på emnesiden (S4) og Oversikt (S3), og historikken med alle leverte forsøk på notatsiden. Dekningsgraden regnes alltid ut fra svar og feilbank og lagres aldri, slik at den alltid stemmer med det studenten har gjort. Den skal også vise ærlig at den kan gå ned når en ny quiz lages. Prioritet: FR-24 (per notat) og FR-26 (historikk) er «bør», og FR-25 (per emne) kan kuttes.

## Stories

- Story 5.1: Dekningsgrad per notat
- Story 5.2: Dekningsgrad per emne
- Story 5.3: Historikk per notat

## Requirements & Constraints

- **Dekket spørsmål:** minst ett riktig svar i en levert økt (forsøk eller øving) og ingen åpen feilbankrad. Svar bare i påbegynte økter teller ikke. Et dekket spørsmål som havner i feilbanken igjen, er ikke lenger dekket.
- **Per notat:** for hvert nivå andelen dekkede spørsmål av alle spørsmålene på nivået i notatets quizer. Totalen er 0,2 × lett + 0,3 × middels + 0,5 × vanskelig. Nivå uten quiz teller 0. Testtilfelle: lett 100 %, middels 50 %, vanskelig uten quiz gir nøyaktig 35 %.
- **TF-6 (akseptansekriterier):** en ny quiz på et nivå gjør at dekningsgraden går ned, og uten quiz på vanskelig blir den aldri over 50 %. Begge deler forklares med en kort hjelpetekst på S7 (ordlyden er ikke bestemt, avklar den).
- **Per emne:** snittet av notatene som har minst én quiz, uavhengig av notatlengde. 80 % og 40 % gir 60 %, og et tredje notat uten quiz endrer ikke snittet. Emne uten notater, eller der ingen notater har quiz, har ingen dekningsgrad.
- **Historikk:** alle leverte forsøk på notatet med dato (i `Europe/Oslo`), quiz (nivå og antall) og poengsum («7 av 10»), nyeste øverst. Hver rad lenker til resultatsiden. Påbegynte forsøk og øvingsøkter vises aldri.
- **Ytelse:** S3 og S4 skal ikke gjøre én databasespørring per spørsmål, så de er raske også for testbrukeren.
- **Melde som feil (4.3, ikke bygget):** hvis 4.3 bygges, telles meldte spørsmål ikke i nevneren. Dekningsgraden må da bruke samme hjelper som feilbanken og innholdet i nye økter.
- **Universell utforming (WCAG 2.2 A/AA)** og 360 px uten vannrett rulling er akseptansekriterier i hver story med grensesnitt.

## Technical Decisions

- **Én implementasjon (AD-4):** ny `studier/services/dekningsgrad.py` er eneste sted som regner ut dekningsgraden, for notat og emne. Den gir et tall mellom 0 og 1 uten avrunding (eller `None` for emne uten dekningsgrad) og skriver aldri til databasen. Avrunding til hele prosent skjer bare i malen.
- **Datagrunnlag:** «riktig» = `Svar.alternativ.er_riktig` i en `Okt` med `status=levert` (begge `type`). «Åpen feilbankrad» = `Feilbankrad.laert_tidspunkt IS NULL`, samme definisjon som `apne_rader` i `studier/services/feilbank.py`. Nivået er `Quiz.vanskelighetsgrad` (`Vanskelighetsgrad`). Spørsmål identifiseres bare av ID, så lik tekst i to quizer er to spørsmål (AD-5).
- **Meldte spørsmål:** `Sporsmal.meldt_tidspunkt` finnes, men hjelperen `ikke_meldt()` fra 4.3 finnes ikke ennå. Lag ikke en egen variant i dekningsgraden. Bygges 4.3, skal den samme hjelperen brukes her.
- **Spørringer:** regn ut med aggregering per nivå (for eksempel `Count` med `filter`, `Exists`/`OuterRef` mot `Svar` og `Feilbankrad`), og for S3/S4 for alle notater i én eller noen få spørringer, ikke i en løkke per notat eller spørsmål.
- **S7 (`notat`-viewet i `studier/views.py`, `templates/studier/notat.html`):** siden har i dag «Øv på feil», quizkortene og «Lag ny quiz», men verken dekningsgrad eller historikk. Dekningskortet legges inn som en egen seksjon øverst, og historikken nederst. `_ov_knapp` og quizkortenes `har_levert`/`fremdrift` skal være uendret.
- **S4 (`_vis_emne` og `templates/studier/emne.html`):** notatkortene viser i dag bare filnavn og dato. De får dekningsgrad (eller «Ingen quiz») og antall i feilbanken, og siden får tallfliser for emnet. Antall i feilbanken teller åpne rader, som `apne_rader`.
- **S3 (`startside` i `farequiz/views.py`, `templates/studier/oversikt.html`):** emnekortene har i dag navn og antall notater. Dekningsgraden hentes fra `services.dekningsgrad`. «Fortsett der du slapp» endres ikke.
- **Historikk (AD-6):** `egne(Okt, bruker)` med `notat=…`, `type=Okttype.FORSOK`, `status=Oktstatus.LEVERT`, sortert på `-levert_tidspunkt`. `poengsum` og `antall` er satt av `lever_okt` og leses direkte. Lenken går til `studier:resultat`.
- **Reiserute-stolpen:** CSS-klassene `.reiserute` og `.reiserute-faar` (fåret og flagget som SVG) finnes i `static/css/input.css` og brukes i `sporsmal.html`. Gjenbruk dem til dekningsstolpen i stedet for å lage en ny komponent, og bygg `static/css/app.css` på nytt med Tailwind-CLI-en ved nye klasser.
- **Lagdeling og tilgang (AD-1, AD-8):** views leser via `hent_egen`/`egne` og kaller tjenesten. Ingen ny modell og ingen migrering.

## UX & Interaction Patterns

- **Dekningsstolpe (`coverage-bar`):** samme reiserute som quizfremdriften: stiplet spor i `accent-strong`, fyll i kaffebrun, fåret i ballongen på enden av fyllet (`aria-hidden`) og flagg ved 100 %. Prosenten står alltid som tekst ved siden av i `score` med `tabular-nums`. Stolpen har `role="img"` med prosenten i `aria-label`, eller er skjult for skjermleser fordi prosenten står som tekst. Mindre stolpe på kort og på S4.
- **S7 Dekningsgrad:** totalen øverst, lett, middels og vanskelig under med prosent eller «Ingen quiz», og teksten «Vanskelige spørsmål teller mest (50 %)». Notat uten quiz: 0 % og «Lag en quiz for å komme i gang».
- **S4:** tallfliser (`stat-tile`, `surface-inverse`, tallet i `score` og kort tekst under) for emnets dekningsgrad (eller «Ingen dekningsgrad») og antall i feilbanken. Notatkortene viser filnavn, opplastingsdato, stolpe med prosent og antall i feilbanken, eller «Ingen quiz».
- **S3 emnekort:** stolpe og prosent, «Ingen notater» for emne uten notater, «Ingen dekningsgrad» når ingen notater har quiz. Kortet er én lenke med tydelig tekst, for eksempel «Webutvikling, 4 notater, dekningsgrad 62 %».
- **Historikk på S7:** overskriften «Historikk». Fra `md` en ekte `<table>` med `<th scope="col">` for Dato, Quiz og Poengsum. Under `md` et lite kort per rad. Uten forsøk: «Ingen forsøk ennå. Ta en quiz for å se historikken.»
- **Tone:** norsk bokmål, du-form, kort og saklig, uten utropstegn og emojier.

## Cross-Story Dependencies

- Epic 5 krever Epic 3 (leverte økter, `Svar`, `Feilbankrad`) og bruker øvingsøkter fra Epic 4 i dekningsgraden. Ingen nye modeller.
- 5.1 eier `services/dekningsgrad.py` og dekningskortet på S7. 5.2 bygger på 5.1 og legger til emnesnittet, S4 og S3. 5.3 er uavhengig av 5.1 og 5.2.
- 4.3 er ikke bygget. Bygges den etter Epic 5, må dekningsgraden oppdateres til å bruke `ikke_meldt()`.
- `seed_testdata` (Epic 6) skal gi testbrukeren leverte forsøk og en feilbank, så dekningsgrad og historikk har innhold for sensor.
