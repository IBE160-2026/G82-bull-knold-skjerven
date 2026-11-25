# Epic 2 Context: Fra notat til quiz

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->
<!-- Kompilert 25.11.2026, etter at Martins design ble felles UX (23.11). -->

## Goal

Studenten laster opp et notat (PDF, DOCX eller TXT) under et emne, velger nivå og antall på Notatsiden, og får en KI-laget quiz med synlige fremdriftssteg, låst knapp og «Prøv igjen» ved feil. Hele løpet virker i testmodus uten API-nøkkel, med mock-svar laget fra ekte genereringer på fem testdokumenter. Epicen bygger `ki`-adapteren (lese fil, generere, sjekke format) og kontrakten mot den, slik at alle quizer som lagres har samme form uansett kilde. Story 2.1 og 2.2 rører bare `ki` og kan bygges parallelt med resten av Epic 1. Kjerne: FR-8, FR-9, FR-11–FR-14, FR-27. Bør: fremdrift og låst knapp, FR-15 og FR-16.

## Stories

- Story 2.1: Lese filen og sjekke quizutkastet
- Story 2.2: Generere med modellen eller mock-svar
- Story 2.3: Laste opp notat
- Story 2.4: Lage quiz med fremdrift
- Story 2.5: Feil, timeout og «Prøv igjen»
- Story 2.6: Flere quizer per notat

## Requirements & Constraints

- **Fil:** PDF, DOCX eller TXT, maks 5 MB, uansett sideantall. Andre formater (MP4, PPTX, bilder) og for store filer avvises på serveren, med sjekk i nettleseren i tillegg. Filen lagres, slik at nye quizer kan lages uten ny opplasting. Opplastingen avvises i tjenesten hvis vilkårene ikke er godtatt.
- **Lese filen:** PDF sendes hel til modellen, slik at lysbilder og skannede sider kan brukes. Fra DOCX og TXT hentes teksten ut. Alle fem testdokumentene skal gi en gyldig quiz, også lysbilde-PDF-en og den skannede.
- **Testdokumenter:** fem filer i `testdokumenter/`: en tekst-PDF på ca. 10 sider, en lysbilde-PDF, en skannet PDF, en DOCX og en TXT. Minst ett på et annet språk enn norsk. `testdokumenter/KILDER.md` oppgir kilde og lisens for hvert dokument (ingen brudd på opphavsretten). Story 2.2 (mock-svar), 6.1 (seed) og 6.4 (KI-kvalitet) bygger på dem.
- **Quizformat:** nøyaktig valgt antall spørsmål (5–30, standard middels og 10), tre ulike alternativer, nøyaktig ett riktig, ingen like spørsmål, på notatets språk. Feil format gir én ny generering. Feiler den igjen, får brukeren en feilmelding og ingen quiz lagres.
- **Fremdrift:** stegene «Leser filen», «Lager spørsmål», «Sjekker quizen». «Lag quiz» er låst til genereringen er ferdig eller har feilet, og det finnes høyst én aktiv generering per notat.
- **Timeout:** 120 sekunder. «Prøv igjen» bruker den lagrede filen og samme valg.
- **Flere quizer:** et notat kan ha mange quizer, også med samme valg. En quiz kan ikke slettes alene.
- **Testmodus:** ingen nettverkskall i testmodus (verifiseres med blokkert nettverk). 30 lagrede spørsmål per testdokument og nivå, og appen bruker de første N. En ukjent fil gir et standard testdokument og en synlig merknad.
- **Sporbarhet og merking:** hver quiz lagrer modell og prompt-versjon, og vises med KI-merke. Innhold sendes bare til KI-tjenesten ved generering, og logger inneholder aldri filinnhold.
- **Universell utforming (WCAG 2.2 A/AA)** er akseptansekriterier i hver story med grensesnitt, som i Epic 1.

## Technical Decisions

- **`ki`-adapteren (AD-11):** `ki/__init__.py` eksponerer `les_fil`, `generer`, `sjekk`, `er_testmodus`, `tving_testmodus`, `visningsnavn` og `PROMPT_VERSJON`. `ki` kjenner ikke databasen og importerer aldri fra `studier` eller `kontoer` (en test sjekker det). All KI-trafikk går gjennom denne ene modulen.
  - `les_fil(sti) -> Innhold(sha256, type, data)`: `sha256` er hashen av filens bytes. PDF: `data` er hele filen. DOCX og TXT: `data` er uttrukket tekst. TXT leses som UTF-8 med cp1252 som reserve.
  - `generer(innhold, vanskelighetsgrad, antall, timeout) -> RaattSvar(tekst, forhandslagret, modell, prompt_versjon)`.
  - `sjekk(raatt, antall) -> QuizUtkast`: håndhever formatreglene og at alle felt finnes, også for mock-svar.
  - **`QuizUtkast`:** `sprak` (BCP 47), `modell`, `prompt_versjon`, `forhandslagret`, `sporsmal: [{tekst, begrunnelse, alternativer: [{tekst, er_riktig}] × 3}]`. Feltene er låst. Prompttekst eies av `ki`, og `PROMPT_VERSJON` økes ved hver endring av prompt eller skjema.
- **Feilkoder (AD-10):** `ki` hever bare `KIFeil(kode)` med `kode` ∈ {`timeout`, `format`, `for_lite_innhold`, `for_stor`, `api_nokkel`, `api_feil`}. Fil som mangler → `api_feil`. DOCX/TXT uten tekst → `for_lite_innhold`. Ugyldig JSON, feil antall spørsmål eller alternativer, ikke nøyaktig ett riktig, like alternativer, like spørsmål eller manglende felt → `format`. Ugyldig nøkkel → `api_nokkel`, for stor fil/for mange sider → `for_stor`. Brukertekstene står i `farequiz/feilmeldinger.py`.
- **Modellkall:** `KI_MODELL` (standard `claude-sonnet-5-5`), PDF som dokument eller tekst, structured outputs (`output_config.format`) med samme skjema som `QuizUtkast`, og `effort` satt eksplisitt. `ki.visningsnavn(modell)` gir f.eks. «Claude Sonnet 5.5». Malene viser alltid modellen fra quizen, aldri gjeldende innstilling.
- **Testmodus og mock (AD-12):** `er_testmodus()` er sann når `TESTMODUS` er `1/true/yes/on` eller nøkkelen mangler. I testmodus slås `innhold.sha256` opp i `ki/mock/manifest.json` (`{sha256: dokument}` + `standard`), og de første N spørsmålene hentes fra `ki/mock/<dokument>/<vanskelighetsgrad>.json` med `modell` og `prompt_versjon` fra filens metadata. Ukjent fil → standarddokumentet med `forhandslagret=True`. `manage.py lag_mocksvar` kjører testdokumentene mot ekte modell (30 per nivå), sjekker med `sjekk` og skriver mock-filene og manifestet, som committes. `.gitattributes` har `testdokumenter/** binary` og `ki/mock/** -text`, slik at hashene stemmer på Windows.
- **Avhengigheter:** `anthropic` ≥ 2.8 < 3 og `python-docx` 1.2.0. Arkitekturen nevner ingen PDF-bibliotek, fordi PDF sendes hel. Nye pakker legges til med `uv add`, fulgt av `uv export --no-hashes -o requirements.txt`.
- **Opplasting (AD-1, AD-14, AD-23):** bare `services.notater.last_opp` lager `Notat`. Filen lagres som `notater/<eier-id>/<uuid4><endelse>` med `originalnavn`, `filtype` ∈ {`pdf`, `docx`, `txt`} og `storrelse`. Originalfiler serveres aldri over HTTP. Emnet hentes med `hent_egen`.
- **Generering (AD-9):** `Genereringsjobb` med `notat`, `vanskelighetsgrad`, `antall`, `startet`, `status`, `runde` (1–2), `i_gang`, `feilkode`, `raatt_svar`, `forhandslagret`, `modell`, `prompt_versjon`. `services.generering.aktiv_jobb(notat)` er eneste definisjon av aktiv jobb og setter jobber eldre enn 120 s til `feilet`/`timeout`. Hvert kall på `/jobber/<id>/steg/` (HTMX-POST) tar jobben med `filter(pk, status=S, i_gang=False).update(i_gang=True)` og kjører ett steg: `leser` validerer filen, `lager` leser filen på nytt og kaller `generer`, `sjekker` kjører `sjekk` og lagrer quizen. Formatfeil i runde 1 → tilbake til `lager` med `runde=2`. `Quiz.jobb` er `OneToOneField`. Mangler jobben eller notatet, returneres et sluttfragment, ikke 404. `generer_synkront(notat, vanskelighetsgrad, antall)` kjører de samme stegene uten HTMX (brukes av seed).
- **Transaksjoner (AD-19):** ingen `ki`-kall mens en transaksjon er åpen. Statusoverganger committes før og etter KI-kallet. Filinnholdet lagres aldri på jobben eller i sesjonen.
- **Lagring av quiz (AD-7, AD-11):** `Quiz` lagrer `jobb`, `vanskelighetsgrad`, `sprak`, `modell`, `prompt_versjon`, `forhandslagret`. Hvert `Sporsmal` lagrer `begrunnelse` og har tre `Alternativ`, nøyaktig ett med `er_riktig`.
- **URL-er:** `/emner/<id>/last-opp/` (S5/S6), `/notater/<id>/` (S7), `/jobber/<id>/` (S8), `/jobber/<id>/steg/`. Feilede jobber logges med jobb-ID og feilkode.

## UX & Interaction Patterns

- **S5 (første opplasting, dvs. ingen notater ennå):** kort bekreftelse om at vilkårene er godtatt, lenke til personvernerklæringen, «Gå videre til opplasting» og «Avbryt». Ellers åpnes S6 direkte.
- **S6 Last opp:** vanlig `<input type="file">` med etikett, uten dra-og-slipp. Formater og maks størrelse over feltet, koblet med `aria-describedby`. KI-varsel om at innholdet sendes til Anthropic. Feil ved feltet med `role="alert"` og fokus: «Filen er over 5 MB. Velg en mindre fil.», «Formatet støttes ikke. Bruk PDF, DOCX eller TXT.», «Velg en fil først.». S6b (JS-forbedring): filnavn, fremdrift som reiserute, låst knapp og beskjed om ikke å lukke fanen. S6c: «Opplastingen ble avbrutt. Filen er ikke lagret. Last opp på nytt.»
- **S16 Nytt emne** får valgfrie filer med samme regler som S6. Feiler en fil, opprettes ikke emnet.
- **S7 Notat:** skjema for ny quiz (`<fieldset>`/`<legend>` med lett, middels, vanskelig; middels valgt; tallfelt 5–30, standard 10, med forklarende tekst; «Lag quiz»). Øverst når notatet ikke har quiz («Lag en quiz for å komme i gang»), ellers etter quizkortene. Quizkort med nivå, antall, dato og «Laget av KI», nyeste øverst. Testmodus-merknad på quiz fra ukjent fil: «Testmodus: denne quizen er laget fra et forhåndslagret testdokument, ikke fra filen din.»
- **S8 Generering:** egen side med de tre stegene i en liste, hvert markert ferdig, pågår eller venter med ikon og tekst, i en `aria-live="polite"`-region. Knappen er låst. Feil og timeout erstatter stegene med melding i `role="alert"` og «Prøv igjen», som får fokus: «Genereringen tok for lang tid. Filen er lagret, så du kan prøve igjen.», «Klarte ikke å lage en gyldig quiz. Prøv igjen, eller velg færre spørsmål.», «KI-tjenesten svarte ikke. Prøv igjen.», og egne tekster i samme tone for de andre kodene. Bare genereringskjeden krever JavaScript.
- **Tone:** norsk bokmål, du-form, kort og saklig, uten utropstegn og emojier.

## Cross-Story Dependencies

- 2.1 eier testdokumentene og `les_fil`/`sjekk`/`KIFeil`. 2.2 bygger på dem (mock-svar, `lag_mocksvar`), og 6.1 (seed) og 6.4 (KI-kvalitet) bruker samme filer.
- 2.1 og 2.2 rører bare `ki` og kan bygges parallelt med Epic 1. 2.3–2.6 krever Emnesiden (1.4), sidemalen (1.3) og vilkårsregelen (1.2).
- 2.3 lager `Notat` og S7-skallet. 2.4 legger skjemaet og genereringen på S7/S8 og trenger 2.1–2.3. 2.5 bygger på jobbkjeden i 2.4. 2.6 utvider S7 fra 2.4.
- 2.4 sender til Notatsiden etter ferdig quiz. Story 3.1 endrer dette til å åpne quizen på spørsmål 1.
- `generer_synkront` fra 2.4 brukes av `seed_testdata` (Epic 6).
