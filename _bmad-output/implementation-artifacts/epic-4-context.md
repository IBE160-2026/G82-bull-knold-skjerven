# Epic 4 Context: Øv på feil til det sitter

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->
<!-- Kompilert 25.11.2026, etter at Martins design ble felles UX (23.11), og etter at Epic 3 er bygget. -->

## Goal

Studenten øver på spørsmålene i notatets feilbank i en egen øvingsøkt (S12) med terrakotta-aksent, med alternativene stokket på nytt og uten fasit. Ved levering teller svarene likt med svar i forsøk, og spørsmål som blir lært i økten, viser «Lært. Riktig svar var: …» med begrunnelse, slik at feilbanken krymper synlig. Studenten kan også melde et spørsmål som feil eller uklart, så hen ikke blir sittende fast med et spørsmål der KI-en har laget feil fasit. Epicen lager ingen ny leveringsflyt. Den bruker `Okt`-tjenestene og feilbankregelen fra Epic 3 med `type=oving`. Kjerne: visning av fasit når spørsmålet er lært (FR-23). Bør: FR-22 (øving). Kan kuttes: ny stokking for hver økt og FR-31 (melde som feil).

## Stories

- Story 4.1: Øve på feilbanken
- Story 4.2: Levere øvingen og se hva som er lært
- Story 4.3: Melde et spørsmål som feil

## Requirements & Constraints

- **Øv på feil:** økten inneholder spørsmålene i feilbanken med alternativene stokket på nytt for hver økt og uten fasit. Alle spørsmål må besvares før levering, og svar lagres underveis. Økten vises aldri i historikken, verken påbegynt eller levert.
- **Knappen:** «Øv på feil (N)» på S7. Låst bare når feilbanken er tom og det ikke finnes noen påbegynt øvingsøkt. Da har den `aria-disabled` og viser «Ingen spørsmål i feilbanken». En påbegynt øvingsøkt gir «Fortsett», også om feilbanken er blitt tom. S11 får knappen «Øv på feil» når feilbanken ikke er tom.
- **Lært (fra Epic 3, uendret):** to riktige på rad etter at spørsmålet kom i feilbanken. Feil svar nullstiller telleren, også for et lært spørsmål, som da kommer tilbake og mister synlig fasit. Svar i øving og i forsøk teller likt.
- **Fasit:** vises bare for lærte spørsmål, sammen med begrunnelsen. Aldri for spørsmål som ikke er lært.
- **Melde som feil (FR-31):** et meldt spørsmål er ikke i feilbanken, telles ikke i nevneren i dekningsgraden og kommer ikke med i nye økter. Meldingen lagres med tidspunkt. Fasiten vises fortsatt ikke. **Forutsetning:** gruppa må først legge regelen inn i arkitekturen (feilbank, dekningsgrad og låst innhold i økter) og FR-31 i PRD-en. Per 25.11 står den ingen av stedene.
- **Tilgang:** andres øvingsøkt, notat eller spørsmål (også i meldingen) gir «Fant ikke siden», og ingenting endres.
- **KI-merking:** «Laget av KI (<modell>). Spørsmålene kan inneholde feil.» på S12, med modellen fra spørsmålets quiz, også i testmodus.
- **Universell utforming (WCAG 2.2 A/AA)** og 360 px uten vannrett rulling er akseptansekriterier i hver story med grensesnitt.

## Technical Decisions

- **Gjenbruk fra Epic 3:** `lagre_svar`, `lever_okt`, `element`, `besvarte`, `forste_ubesvarte` i `studier/services/okter.py` og `registrer_svar`/`fasit_synlig` i `studier/services/feilbank.py` brukes uendret. Views `sporsmal`, `lever` og `resultat` og malene `sporsmal.html`, `lever.html` og `resultat.html` gjenbrukes med `type=oving`, ikke kopieres. URL-ene `/okter/<id>/…` er de samme.
- **Øvingsøkt (AD-6):** `Okt` med `type=Okttype.OVING`, `notat` satt og `quiz=None` (`CheckConstraint`). Høyst én påbegynt `oving` per notat (betinget `UniqueConstraint`, finnes allerede). Starter med POST.
- **Start:** dagens `start_eller_fortsett_okt(quiz)` lager bare `forsok`. Epic 4 må utvide tjenesten (eller lage en søster for notat) med samme mønster: hent påbegynt økt, ellers opprett i `atomic`, og hent den andre ved `IntegrityError`.
- **`Okt.innhold` for øving (AD-16):** spørsmålene med åpen `Feilbankrad` (`laert_tidspunkt IS NULL`) for notatet når økten opprettes, sortert på `Feilbankrad.opprettet`, med alternativene stokket. Listen endres aldri, selv om feilbanken endres i en annen fane.
- **Levering (AD-18, AD-2):** samme `lever_okt`. Den kjører `registrer_svar` for hvert spørsmål og lagrer `Svar.hendelse` ∈ {`lagt_i`, `nullstilt`, `opp`, `laert`, `ingen`}. Resultatet leser hendelsene og regner dem aldri ut på nytt.
- **Resultat av øving:** spørsmål med `hendelse=laert` øverst med riktig alternativ og `Sporsmal.begrunnelse`. Telleren «1 av 2 riktige på rad» bygger på `Feilbankrad.riktige_pa_rad` og `RIKTIGE_FOR_LAERT = 2`. Fasit bare når `fasit_synlig(sporsmal)` er sann (AD-20).
- **Fasit i malen (AD-20):** `er_riktig` og `begrunnelse` sendes aldri til spørsmålsmalen. `_vis_sporsmal` har allerede bare `pk`, `tekst`, `quiz__modell` og `quiz__sprak`, og det må forbli slik for øving.
- **Steder som antar `forsok` eller en quiz (må håndteres):**
  - `resultat.html` har «Ta på nytt» med `{% url 'studier:start_quiz' okt.quiz_id %}`, som gir `NoReverseMatch` (500) for første leverte øvingsøkt. Skjul skjemaet når `okt.quiz_id` er tom, og legg til en test (utsatt fra 3.4).
  - `resultat`-viewet regner `har_pabegynt` på `quiz_id`.
  - `_fortsett_rader` i `farequiz/views.py` filtrerer på `FORSOK` og bruker `okt.quiz.get_vanskelighetsgrad_display()` i tittelen. Øvingsøkter må inn i «Fortsett der du slapp» med en tittel som ikke trenger quiz. Ordlyden er ikke bestemt i designet, så avklar den.
  - `notat`-viewet henter bare påbegynte `forsok`.
- **Historikk (AD-6):** `type=forsok`, `status=levert`. Øvingsøkter skal aldri med.
- **Melde som feil:** en tjeneste i `studier/services/` setter `Sporsmal.meldt_tidspunkt` (finnes fra 1.1, ingen ny migrering). Én hjelper, for eksempel `Sporsmal.objects.ikke_meldt()`, brukes i alle utvalg (innhold i nye økter, telling av feilbanken og senere dekningsgraden). I en påbegynt økt der spørsmålet alt står, gir `registrer_svar` `ingen` ved levering. `Feilbankrad` slettes aldri.
- **Lagdeling og tilgang (AD-1, AD-8):** bare `studier/services/` skriver `Okt`, `Svar`, `Feilbankrad` og `Sporsmal`. Alle ID-er går gjennom `hent_egen`/`egne`. Alle knapper er POST-skjemaer som virker uten JavaScript, med POST/redirect/GET (AD-13).

## UX & Interaction Patterns

- **S12 Øv på feil:** samme flyt og samme sider som S9, S10 og S11, med overskriften «Øv på feil». Aksentfargen settes på seksjonen og er terrakotta (`error` #A34420), slik at fremdrift, prikker og knapper blir terrakotta. Det går foran DESIGN.md, som sier at terrakotta bare brukes til feil svar. Valgt alternativ vises fortsatt med form (tykkere kant og fylt radioknapp) og kontrast på minst 4,5:1.
- **Brødsmulesti og Tilbake** peker på notatet. `lang` fra spørsmålets quiz når språket ikke er norsk.
- **Resultat av øving:** «4 av 5 riktige» i `score` med `role="status"`. Øverst for hvert lært spørsmål: spørsmålet, «Lært. Riktig svar var: …» og begrunnelsen. Deretter resultatradene som på S11 (✓ «Riktig» / ✕ «Feil», ikonet `aria-hidden`), og for spørsmål som ikke er lært, lært-prikker og «1 av 2 riktige på rad». Prikkene er pynt, og teksten gir samme informasjon.
- **Alt lært:** «Alle spørsmålene er lært. Feilbanken er tom.» og lenke tilbake til notatet. Ingen feiring, utropstegn, lyd eller animasjon.
- **Melde som feil:** «Meld som feil eller uklart» (POST) på resultatrader med ✕ «Feil» på S11 og S12, bekreftelse på egen side (ikke popup), og raden viser deretter «Meldt som feil».
- **«Fortsett der du slapp» på S3:** påbegynte øvingsøkter står i boksen sammen med forsøk, sortert på `sist_endret`, nyeste først. S3 har ikke noe eget «Øv på feil»-kort, og «Øv på feil» står ikke i Meny. Øving startes bare fra S7 og S11.
- **Tone:** norsk bokmål, du-form, kort og saklig, uten utropstegn og emojier.

## Cross-Story Dependencies

- Epic 4 krever Epic 3: `Okt`-tjenestene, `registrer_svar`, S9–S11 og «Fortsett der du slapp» (3.5). Alle modellene og `Sporsmal.meldt_tidspunkt` finnes fra 1.1.
- 4.1 eier oppstart av øvingsøkter, knappen på S7 og S11, terrakotta-aksenten og øvingsøkter i «Fortsett der du slapp».
- 4.2 bygger på 4.1 og eier resultatet av øving, inkludert å skjule «Ta på nytt» for øvingsøkter.
- 4.3 kan bygges etter 3.3 og kan kuttes. Den krever at arkitekturen og PRD-en er oppdatert først, og at `ikke_meldt()` tas i bruk i 4.1-utvalget og i Epic 5 (dekningsgraden).
- Epic 5 kan bygges parallelt. Dekningsgraden teller riktige svar i leverte økter av begge typer, og historikken viser bare `forsok`. `seed_testdata` (Epic 6) skal gi testbrukeren en feilbank å øve på.
