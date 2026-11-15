---
name: FåreQuiz
description: Quizapp der studenter laster opp forelesningsnotater og får en KI-laget quiz tilbake. Responsiv web med Django-maler. Christians individuelle UX-versjon.
status: final
created: 2026-11-15
updated: 2026-11-15
author: Christian
sources:
  - ../../briefs/brief-G82-bull-knold-skjerven-2026-09-16/brief.md
  - ../../prds/prd-G82-bull-knold-skjerven-2026-11-11/prd.md
  - ../../prds/prd-G82-bull-knold-skjerven-2026-11-11/addendum.md
colors:
  # Tema B «Frisk grønn». Kontrast er målt mot surface (#FFFFFF) hvis ikke annet er oppgitt.
  background: '#F6FBF8'
  surface: '#FFFFFF'
  text: '#0B1F17'              # 16.4:1 mot background
  text-muted: '#4B5563'        # 7.56:1 · 7.22:1 mot background
  border: '#D1D5DB'            # dekorativ kant rundt kort og bokser
  border-input: '#4B5563'      # kant på inndatafelt, 7.56:1
  track: '#E5E7EB'             # bakgrunn i fremdrifts- og dekningsstolper
  primary: '#047857'           # 5.48:1 · knapper, lenker, fokus, valgt svar, stolper
  primary-hover: '#065F46'     # hvit tekst 7.68:1
  primary-foreground: '#FFFFFF'
  selected: '#ECFDF5'          # flate bak valgt svar og «Fortsett der du slapp»; primary 5.21:1
  # «Øv på feil» bytter primary-familien med practice-familien (aksent fra tema C).
  practice: '#C2410C'          # 5.18:1 · hvit tekst 5.18:1
  practice-hover: '#9A3412'    # hvit tekst 7.31:1
  practice-selected: '#FFF7ED' # practice 4.88:1
  practice-tag-text: '#9A3412' # 6.88:1 mot practice-selected
  practice-tag-border: '#FDBA74'
  success: '#15803D'           # 5.02:1 · alltid med ✓ og tekst
  success-surface: '#F0FDF4'   # success 4.79:1
  danger: '#B91C1C'            # 6.47:1 · alltid med ✗ og tekst
  danger-hover: '#991B1B'
  danger-surface: '#FEF2F2'    # danger 5.91:1
  danger-text: '#7F1D1D'       # 9.16:1 mot danger-surface
  started-text: '#92400E'      # 6.84:1 mot started-surface
  started-surface: '#FFFBEB'
  started-border: '#FCD34D'
  disabled-surface: '#E5E7EB'
  disabled-text: '#4B5563'     # 6.10:1 mot disabled-surface
typography:
  # Systemfonter, ingen nettfonter.
  family:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
  body:
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  small:
    fontSize: 14px
    lineHeight: '1.5'
  label:
    fontSize: 12px
    fontWeight: '600'
  h1:
    fontSize: 26px              # 22px under 480 px
    fontWeight: '700'
    lineHeight: '1.25'
  h2:
    fontSize: 18px
    fontWeight: '700'
  question:
    fontSize: 18px
    fontWeight: '600'
  option:
    fontSize: 17px
    fontWeight: '400'
  coverage-figure:
    fontSize: 36px              # 32px under 480 px
    fontWeight: '800'
    lineHeight: '1'
  score-figure:
    fontSize: 56px
    fontWeight: '800'
    lineHeight: '1'
rounded:
  sm: 4px
  md: 8px
  lg: 10px
  full: 9999px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 20px
  '6': 24px
  '8': 32px
  '12': 48px
  gutter: 16px
  content-max: 760px
  target-min: 44px
components:
  top-bar:
    background: '{colors.surface}'
    border-bottom: '{colors.border}'
  back-button:
    background: '{colors.surface}'
    foreground: '{colors.text}'
    border: '{colors.border}'
    radius: '{rounded.md}'
    min-height: '{spacing.target-min}'
  menu-button:
    background: '{colors.surface}'
    border: '{colors.border}'
    border-open: '{colors.primary}'
    radius: '{rounded.md}'
    min-height: '{spacing.target-min}'
  menu-panel:
    background: '{colors.surface}'
    border: '{colors.border}'
    radius: '{rounded.lg}'
    shadow: '0 8px 24px rgba(0,0,0,.12)'
    width: 260px
  button-primary:
    background: '{colors.primary}'
    background-hover: '{colors.primary-hover}'
    foreground: '{colors.primary-foreground}'
    radius: '{rounded.md}'
    min-height: '{spacing.target-min}'
  button-secondary:
    background: 'transparent'
    background-hover: '{colors.selected}'
    foreground: '{colors.primary}'
    border: '{colors.primary}'
    radius: '{rounded.md}'
  button-practice:
    background: '{colors.practice}'
    background-hover: '{colors.practice-hover}'
    foreground: '{colors.primary-foreground}'
    radius: '{rounded.md}'
  button-danger:
    background: '{colors.danger}'
    background-hover: '{colors.danger-hover}'
    foreground: '{colors.primary-foreground}'
    radius: '{rounded.md}'
  button-disabled:
    background: '{colors.disabled-surface}'
    foreground: '{colors.disabled-text}'
  list-row:
    background: '{colors.surface}'
    background-hover: '{colors.selected}'
    border: '{colors.border}'
    border-hover: '{colors.primary}'
    radius: '{rounded.lg}'
    min-height: 64px
  coverage-bar:
    track: '{colors.track}'
    fill: '{colors.primary}'
    height: 10px
    radius: '{rounded.full}'
  coverage-card:
    background: '{colors.surface}'
    figure: '{typography.coverage-figure}'
  level-box:
    border: '{colors.border}'
    radius: '{rounded.md}'
  continue-box:
    background: '{colors.selected}'
    border: '2px solid {colors.primary}'
    radius: '{rounded.lg}'
  question-box:
    background: '{colors.surface}'
    border: '1.5px solid {colors.border}'
    radius: '{rounded.lg}'
    type: '{typography.question}'
  answer-option:
    background: '{colors.surface}'
    border: '1.5px solid {colors.border}'
    border-selected: '2px solid {colors.primary}'
    background-selected: '{colors.selected}'
    radius: '{rounded.lg}'
    min-height: 56px
    type: '{typography.option}'
  quiz-progress:
    track: '{colors.track}'
    fill: '{colors.primary}'
    height: 8px
  ai-label:
    background: '{colors.background}'
    foreground: '{colors.text-muted}'
    border: '{colors.border}'
    radius: '{rounded.full}'
  tag-started:
    background: '{colors.started-surface}'
    foreground: '{colors.started-text}'
    border: '{colors.started-border}'
    radius: '{rounded.full}'
  tag-practice:
    background: '{colors.practice-selected}'
    foreground: '{colors.practice-tag-text}'
    border: '{colors.practice-tag-border}'
    radius: '{rounded.full}'
  segmented-choice:
    border: '1.5px solid {colors.border}'
    border-selected: '{colors.primary}'
    background-selected: '{colors.selected}'
    radius: '{rounded.md}'
  text-input:
    border: '1.5px solid {colors.border-input}'
    radius: '{rounded.md}'
    min-height: '{spacing.target-min}'
  notice:
    background: '{colors.selected}'
    border-left: '4px solid {colors.primary}'
  terms-box:
    background: '{colors.surface}'
    border: '1.5px solid {colors.border}'
    radius: '{rounded.lg}'
  error-message:
    background: '{colors.danger-surface}'
    foreground: '{colors.danger-text}'
    border: '1.5px solid {colors.danger}'
    radius: '{rounded.md}'
  result-row:
    background: '{colors.surface}'
    border: '{colors.border}'
    correct: '{colors.success}'
    wrong: '{colors.danger}'
  learned-box:
    background: '{colors.success-surface}'
    border: '2px solid {colors.success}'
    radius: '{rounded.lg}'
  score-card:
    figure: '{typography.score-figure}'
  wait-panel:
    spinner-track: '#D1FAE5'
    spinner-fill: '{colors.primary}'
    step-on: '{colors.primary}'
    step-off: '{colors.track}'
  history-table:
    header-background: '{colors.background}'
    header-foreground: '{colors.text-muted}'
    border: '{colors.border}'
---

## Brand & Style

FåreQuiz skal føles **brukervennlig og rask**, og være **perfekt for å teste om man har fått med seg pensum**. Studenten kommer for å finne ut hva hen kan. Appen skal ikke stå i veien for det. Uttrykket er derfor enkelt og ryddig, uten pynt: hvite bokser på en lys, grønnskjær bakgrunn, én grønn aksentfarge og store, tydelige klikkflater.

Det skal ikke være «for fancy». Det betyr ingen animasjoner utover en enkel venteindikator, ingen illustrasjoner og ingen poengjakt. Det eneste unntaket er en liten feiring når et spørsmål blir **lært**. Det er selve målet i læringssløyfen og fortjener et øyeblikk.

«Øv på feil» er en egen modus og får en varm oransje aksent i stedet for grønn. Studenten skal se med en gang at hen øver på feilene sine og ikke tar en ny quiz.

## Colors

- **Grønn primærfarge (`{colors.primary}` #047857)** brukes til primærknapper, lenker, fokusring, valgt svaralternativ, fremdriftsstolper og dekningsstolper. Hover er `{colors.primary-hover}`. Grønt gir følelsen av fremgang.
- **Valgt-flate (`{colors.selected}`)** er en blek grønn bakgrunn bak valgt svar, valgt vanskelighetsgrad, rad under musepekeren og boksen «Fortsett der du slapp».
- **Oransje øvefarge (`{colors.practice}` #C2410C)** brukes bare i «Øv på feil» og på knappen som starter det. Inne i økten erstatter practice-familien primary-familien helt (knapper, valgt svar, fremdrift).
- **Riktig (`{colors.success}`) og feil (`{colors.danger}`)** står aldri alene. Riktig har alltid ✓ og ordet «Riktig», feil har alltid ✗ og ordet «Feil» (WCAG 1.4.1). Riktig og primærfargen er to nyanser av grønt. Det er greit fordi ikon og tekst skiller dem.
- **Påbegynt (`{colors.started-surface}` / `{colors.started-text}`)** er en gul merkelapp for påbegynte forsøk.
- **Nøytrale:** `{colors.background}` for siden, `{colors.surface}` for kort og bokser, `{colors.text}` for tekst og `{colors.text-muted}` for hjelpetekst og metadata.
- **Kanter:** `{colors.border}` er dekorativ og rammer inn kort. Inndatafelt bruker `{colors.border-input}`, som har 7,56:1 og oppfyller 1.4.11.

Alle tekstfarger har minst 4,5:1 mot bakgrunnen de står på. Tallene står ved hvert token i frontmatter. Det finnes ingen mørk modus i v1.

## Typography

Systemfonter (`{typography.family.fontFamily}`). Ingen nettfonter, så appen laster raskt og virker uten nett.

- **Brødtekst** er 16 px. Hjelpetekst og metadata er 14 px (`{typography.small}`).
- **Spørsmålsteksten** (`{typography.question}`) er 18 px halvfet, og **svaralternativene** (`{typography.option}`) er 17 px. Quizen er det viktigste i appen, så teksten der er større enn ellers.
- **Store tall:** poengsummen på resultatsiden (`{typography.score-figure}`, 56 px) og dekningsgraden på emne- og notatsiden (`{typography.coverage-figure}`, 36 px). Det er tallene studenten kommer for å se.
- Alle størrelser er i `rem` i koden, så 200 % tekstforstørrelse virker (1.4.4).

## Layout & Spacing

Én kolonne, sentrert, med maks bredde `{spacing.content-max}` (760 px) på alle skjermer. Det gir samme oppsett på pc og mobil, og det er bare bredden som endrer seg. Sidemargen er `{spacing.gutter}` (16 px).

Avstander følger 4-skalaen i frontmatter. Mellom rader i en liste brukes `{spacing.3}`, og mellom seksjoner `{spacing.8}`.

Alle klikkflater er minst `{spacing.target-min}` (44 px) høye. Det er mer enn WCAG-kravet på 24 px og gjør appen lett å bruke med tommelen. Svaralternativene er minst 56 px.

Under 400 px skjules logoen i topplinjen, slik at det blir plass til Tilbake og Meny. Under 480 px blir overskrifter og store tall litt mindre. Ingenting ruller vannrett ned til 320 px.

## Elevation & Depth

Flatt. Kort og bokser skilles fra bakgrunnen med kant og hvit flate, ikke med skygge. Det eneste som har skygge, er menypanelet (`{components.menu-panel.shadow}`), fordi det ligger over innholdet.

## Shapes

Myke, men ikke runde hjørner. `{rounded.md}` (8 px) brukes på knapper, felt og små bokser. `{rounded.lg}` (10 px) brukes på kort, listerader, spørsmålsboks og svaralternativer. `{rounded.full}` brukes bare på merkelapper, stolper og venteindikatoren.

## Components

| Komponent | Utseende |
|---|---|
| **Topplinje** (`top-bar`) | Hvit stripe med kant under. Til venstre: Tilbake-knapp (ikke på startsiden) og logoen «FåreQuiz» i fet grønn. Til høyre: menyknapp. |
| **Tilbake-knapp** (`back-button`) | «← Tilbake», hvit med grå kant. Grønn kant og tekst ved hover. |
| **Menyknapp og menypanel** (`menu-button`, `menu-panel`) | «☰ Meny» med grå kant, som blir grønn når menyen er åpen. Panelet er 260 px bredt med skygge og har seksjonene *Mine emner* (overskrift med små store bokstaver), *+ Nytt emne*, *Fortsett der du slapp* og *Logg ut*, skilt med tynne linjer. |
| **Primærknapp** (`button-primary`) | Fylt grønn med hvit tekst. Større variant (18 px, mer luft) for «Lag quiz» og «Opprett ditt første emne». |
| **Sekundærknapp** (`button-secondary`) | Grønn kant og tekst, gjennomsiktig. Brukes til «Forrige», «Ta på nytt», «Avbryt». |
| **Øveknapp** (`button-practice`) | Fylt oransje. Brukes bare til «Øv på feil». |
| **Fareknapp** (`button-danger`) | Fylt rød. Brukes bare til «Ja, slett emnet». |
| **Låst knapp** (`button-disabled`) | Grå flate med mørkegrå tekst. |
| **Listerad** (`list-row`) | Hvitt kort med navn i halvfet, metadata i liten grå tekst under og dekningsstolpe og prosent til høyre. Hele raden er klikkbar og blir blekgrønn med grønn kant ved hover. |
| **Dekningsstolpe** (`coverage-bar`) | 10 px høy, grå bane og grønn fyll. Står alltid sammen med prosenttallet. |
| **Dekningskort** (`coverage-card`) | Overskrift «Dekningsgrad for …» i liten grå tekst, stort tall og stolpe. På notatsiden ligger tre nivåbokser under. |
| **Nivåboks** (`level-box`) | Tre like brede bokser: «Lett · 20 %», «Middels · 30 %», «Vanskelig · 50 %» i liten grå tekst, med resultatet i fet under. |
| **Fortsett-boks** (`continue-box`) | Blekgrønn flate med 2 px grønn kant. Overskrift og listerader for hvert påbegynte forsøk og hver påbegynte øvingsøkt. |
| **Spørsmålsboks** (`question-box`) | Hvit boks med grå kant og spørsmålet i 18 px halvfet. |
| **Svaralternativ** (`answer-option`) | Hvit boks med radioknapp til venstre og tekst. Valgt alternativ har blekgrønn flate og 2 px grønn kant (oransje i «Øv på feil»). Grønn kant ved hover. |
| **Quizfremdrift** (`quiz-progress`) | «Spørsmål 3 av 10» til venstre og KI-merke til høyre, med en 8 px stolpe under. |
| **KI-merke** (`ai-label`) | Liten pille: «Laget av KI (Claude Sonnet 5.5) · kan inneholde feil». |
| **Merkelapper** (`tag-started`, `tag-practice`) | Gul pille «Påbegynt» / «Påbegynt 5/10». Oransje pille «Øv på feil». |
| **Valgknapper** (`segmented-choice`) | Lett / Middels / Vanskelig som tre bokser med radioknapp. Valgt boks har grønn kant og blekgrønn flate. |
| **Inndatafelt** (`text-input`) | Mørkegrå kant på 1,5 px, 44 px høyt. Brukes til filvelger, antall og emnenavn. |
| **Merknad** (`notice`) | Blekgrønn flate med grønn stripe til venstre. Brukes til KI-tjeneste-merknaden ved opplasting. |
| **Vilkårsboks** (`terms-box`) | Hvit boks med avkrysningsboks «Jeg godtar vilkårene» og en lenke «Les vilkårene» som folder ut teksten. |
| **Feilmelding** (`error-message`) | Lys rød flate med rød kant, fet rød overskrift og mørkerød tekst. Lenker i meldingen er fete. |
| **Resultatrad** (`result-row`) | Hvit rad med «✓ Riktig» i grønt eller «✗ Feil» i rødt, fulgt av «Spørsmål N». |
| **Lært-boks** (`learned-box`) | Blekgrønn flate med 2 px grønn kant. «Lært! ✓» i fet grønn, så spørsmålet og «Fasit: …» i fet. |
| **Poengkort** (`score-card`) | Sentrert. Quizinfo i grå tekst over, «7 av 10» i 56 px, «riktige svar» under. |
| **Ventepanel** (`wait-panel`) | Sentrert spinner, overskriften «Lager quiz, håper du er klar!», steglinje i grå tekst og tre små stolper som fylles grønt. |
| **Historikktabell** (`history-table`) | Kolonnene Dato, Quiz og Poengsum. Overskriftsraden har liten grå tekst på bakgrunnsfarge. |

Skissene i [mockups/](mockups/) viser komponentene i bruk. Ved konflikt gjelder dette dokumentet og `EXPERIENCE.md`, ikke skissene.

## Do's and Don'ts

| Gjør | Ikke gjør |
|---|---|
| Vis riktig og feil med ✓/✗ og tekst i tillegg til farge. | Bruk farge alene for å vise status. |
| Bruk oransje bare i «Øv på feil». | Bruk oransje som pynt eller i vanlig quiz. |
| Vis alltid prosenttallet ved en dekningsstolpe. | Vis stolpen uten tall. |
| Hold klikkflater på minst 44 px. | Lag små ikonknapper uten tekst. |
| Ett grønt hovedvalg per skjerm (Lag quiz, Neste, Lever). | Flere fylte primærknapper ved siden av hverandre. |
| Hold appen flat: kant og hvit flate. | Skygger, gradienter eller illustrasjoner. |
| Merk hver quiz med KI-merket der den vises. | Skjul eller forkort KI-merket. |
