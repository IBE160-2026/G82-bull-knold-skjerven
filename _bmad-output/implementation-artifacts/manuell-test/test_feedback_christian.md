# Testtilbakemeldinger: Christian R Bull

Slik fører du funn: se [README.md](README.md). ID-er: `CHR-01`, `CHR-02` …

## Testøkter

| Dato | Hva ble testet | Enhet, OS og nettleser | Modus (testmodus / ekte modell) |
|---|---|---|---|
| 26.11.2026 | Kjerneflyten med testbrukeren | PC, Windows 10, nettleser: | testmodus |

## Oversikt

| ID | Type | Skjermbilde | Kort beskrivelse | Alvorlighet | Status |
|---|---|---|---|---|---|
| CHR-01 | forbedring | S3 | «Fortsett der du slapp» viser alle påbegynte forsøk øverst og blir rotete | mindre | åpen |
| CHR-02 | forbedring | S4 | «I feilbanken» sier ikke hva tallet teller; bør være «Spørsmål i feilbanken» | kosmetisk | åpen |
| CHR-03 | forbedring | S12 | Etter «Øv på feil» bør man få tre valg: tilbake til emnet, øv på feil igjen og avslutt | mindre | åpen |
| CHR-04 | forbedring | S4 | Emnesiden mangler en underoverskrift over notatene/quizene som er lastet opp | mindre | åpen |
| CHR-05 | forbedring | S4 | «Gi nytt navn» tar for mye plass og er for synlig | kosmetisk | åpen |

## Funn

<!-- Kopier blokken under for hvert nye funn, og fyll ut. -->

### CHR-01: kort tittel

- **Type:** feil / forbedring / observasjon / UU
- **Skjermbilde:** S…
- **Alvorlighet:** kritisk / alvorlig / mindre / kosmetisk
- **Dato og enhet:**
- **Steg for å gjenskape:**
  1.
- **Forventet:**
- **Faktisk:**
- **Forslag:**
- **Skjermbilde eller lenke:**
- **Status:** åpen / rettet (commit) / avvist (begrunnelse) / åpent punkt (begrunnelse)

### CHR-01: «Fortsett der du slapp» blir rotete med mange påbegynte forsøk

- **Type:** forbedring
- **Skjermbilde:** S3
- **Alvorlighet:** mindre
- **Dato og enhet:** 26.11.2026, PC med Windows 10, testmodus
- **Steg for å gjenskape:**
  1. Logg inn som testbrukeren.
  2. Start flere quizer uten å levere dem.
  3. Gå til Oversikt (S3).
- **Forventet:** Oversikten er ryddig, og emnene er lette å finne, selv om man har flere påbegynte forsøk.
- **Faktisk:** Hvert påbegynte forsøk får sitt eget kort under «Fortsett der du slapp», og alle kortene ligger øverst på siden, før overskriften «Oversikt» og emnene. Med flere forsøk blir siden rotete, og emnene skyves langt ned.
- **Forslag:** Slå seksjonen sammen til én boks, for eksempel «Fortsett der du slapp (3)». Trykker man på den, vises resten av forsøkene. Det kan lages med `<details>`/`<summary>` uten JavaScript, som «Meny» i toppfeltet. Det siste forsøket kan gjerne vises direkte, så den vanligste handlingen fortsatt er ett trykk unna.
- **Skjermbilde eller lenke:**
- **Status:** åpen

### CHR-02: «I feilbanken» sier ikke hva tallet teller

- **Type:** forbedring
- **Skjermbilde:** S4
- **Alvorlighet:** kosmetisk
- **Dato og enhet:** 26.11.2026, PC med Windows 10, testmodus
- **Steg for å gjenskape:**
  1. Logg inn som testbrukeren.
  2. Gå til Oversikt (S3) og åpne emnet «Webutvikling» (S4).
  3. Se på tallflisene under overskriften og på notatkortene.
- **Forventet:** Teksten sier hva tallet teller: «Spørsmål i feilbanken» i flisen og «N spørsmål i feilbanken» på notatkortene.
- **Faktisk:** Flisen ved siden av «Dekningsgrad» heter bare «I feilbanken», og notatkortene viser «N i feilbanken». Det står ikke at det er spørsmål som telles. Andre steder i appen står ordet: «N spørsmål er lagt i feilbanken.» på resultatsiden (S11) og «Ingen spørsmål i feilbanken» i «Øv på feil».
- **Forslag:** Endre teksten til «Spørsmål i feilbanken» i `templates/studier/emne.html`, linje 31 (flisen) og linje 67 (notatkortene). Sjekk om testene i `studier/tests/test_dekningsgrad_emne.py` ser etter den gamle teksten.
- **Skjermbilde eller lenke:**
- **Status:** åpen

### CHR-03: Tre tydelige valg når «Øv på feil» er ferdig

- **Type:** forbedring
- **Skjermbilde:** S12
- **Alvorlighet:** mindre
- **Dato og enhet:** 26.11.2026, PC med Windows 10, testmodus
- **Steg for å gjenskape:**
  1. Logg inn som testbrukeren.
  2. Åpne et notat med spørsmål i feilbanken (S7) og trykk «Øv på feil».
  3. Svar på spørsmålene og lever.
  4. Se på knappene under resultatet.
- **Forventet:** Tre tydelige valg når øvingen er ferdig:
  1. **Tilbake til emnet** (S4).
  2. **Øv på feil**, bare hvis det fortsatt er spørsmål i feilbanken.
  3. **Avslutt**, som tar deg tilbake til forsiden (Oversikt, S3).
- **Faktisk:** Under resultatet står «Øv på feil (N)» når det er spørsmål igjen, og lenken «Tilbake til notatet». Man kommer ikke direkte til emnet eller forsiden, og det finnes ikke noe tydelig «Avslutt». Det er ikke klart hva man skal gjøre når man er ferdig med å øve.
- **Forslag:** Gi resultatsiden for øving (`er_oving` i `templates/studier/resultat.html`, linje 67–80) tre handlinger: «Tilbake til emnet», «Øv på feil (N)» når feilbanken ikke er tom (`_ov_pa_feil.html` finnes allerede) og «Avslutt» som lenke til Oversikt. Avklar i gruppa om «Tilbake til notatet» skal erstattes eller stå i tillegg, siden «Tilbake» i toppfeltet allerede går til notatet. Hvis resultatsiden for vanlig quiz (S11) også skal endres, bør den ha de samme valgene.
- **Skjermbilde eller lenke:**
- **Status:** åpen

### CHR-04: Emnesiden mangler en underoverskrift over notatene

- **Type:** forbedring
- **Skjermbilde:** S4
- **Alvorlighet:** mindre
- **Dato og enhet:** 26.11.2026, PC med Windows 10, testmodus
- **Steg for å gjenskape:**
  1. Logg inn som testbrukeren.
  2. Gå til Oversikt (S3) og åpne emnet «Webutvikling» (S4).
- **Forventet:** En underoverskrift over listen, for eksempel «Notater og quizer», så det er tydelig at det er her notatene som er lastet opp og quizene deres ligger.
- **Faktisk:** Siden har bare emnenavnet som overskrift (h1). Under følger tallflisene, «Last opp notat», «Gi nytt navn» og notatkortene, uten noen underoverskrift. Det er ikke tydelig hva listen med kort er, eller hvor quizene er.
- **Forslag:** Legg til en h2, for eksempel «Notater og quizer», rett over notatkortene i `templates/studier/emne.html`. Det hjelper også skjermleserbrukere som hopper mellom overskrifter, for i dag finnes ingen h2 på siden. Notatsiden (S7) har allerede h2-er som «Quizer» og «Historikk».
- **Skjermbilde eller lenke:**
- **Status:** åpen

### CHR-05: «Gi nytt navn» tar for mye plass

- **Type:** forbedring
- **Skjermbilde:** S4
- **Alvorlighet:** kosmetisk
- **Dato og enhet:** 26.11.2026, PC med Windows 10, testmodus
- **Steg for å gjenskape:**
  1. Logg inn som testbrukeren.
  2. Åpne emnet «Webutvikling» (S4).
- **Forventet:** «Gi nytt navn» er en lite brukt handling og står diskret, så den ikke konkurrerer med notatene og «Last opp notat».
- **Faktisk:** «Gi nytt navn» står som en egen boks i full bredde med kant og fet skrift, mellom «Last opp notat» og notatkortene. Den tar mye plass og ser like viktig ut som hovedinnholdet.
- **Forslag:** Gjør den mindre, for eksempel som en vanlig tekstlenke eller en liten knapp ved siden av emnenavnet eller sammen med «Slett emne». Behold `<details>` og målet på minst 44 px, så den fortsatt virker uten JavaScript og er lett å treffe.
- **Skjermbilde eller lenke:**
- **Status:** åpen
