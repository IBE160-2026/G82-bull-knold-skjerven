---
name: FåreQuiz
description: Quizapp for studenter som lager quiz av forelesningsnotater. Tailwind CSS i Django-maler. Dokumentet beskriver bare det som avviker fra Tailwinds standarder.
status: final
created: 2026-11-11
updated: 2026-11-11
sources:
  - ../../prds/prd-G82-bull-knold-skjerven-2026-11-11/prd.md
  - ../../prds/prd-G82-bull-knold-skjerven-2026-11-11/addendum.md
colors:
  # Varm palett: beige og brunt med terrakotta og ochre. Kontrast er målt mot surface (#FFFDF9).
  surface: '#FFFDF9'               # kremhvit, kort og flashcard
  surface-muted: '#FBF7F1'        # svak variasjon, bakgrunn i tallfelt og bak hover
  surface-sunken: '#EFE6D8'       # KI-merke og testmodus-banner
  page-bg: '#F6F1EA'              # varm beige bakgrunn for hele siden, med prikkemønster
  border-subtle: '#E5DDD0'        # skillelinjer og kortkanter, bare til pynt
  border-control: '#7A6456'       # 5.46:1, kanter på inndatafelt og alternativer
  ink: '#2C1E16'                  # espressobrun, 15.85:1 mot surface
  ink-secondary: '#6B5A4E'        # 6.46:1 mot surface
  accent: '#D9A21B'               # ochre, 2.05:1 mot page-bg. Bare dekorativt, aldri tekst eller fremdrift
  accent-strong: '#B04A26'        # terrakotta, 5.45:1 med hvit tekst, 5.36:1 mot surface
  accent-hover: '#8E3A1C'         # 7.58:1 mot hvit, hover og trykk
  card-hover: '#FBE9B7'           # ochre lys, bakgrunn på svaralternativ ved hover. 13.37:1 med ink
  success: '#3F5F0F'              # oliven, 7.24:1 mot surface
  error: '#B91C1C'                # rød, 6.37:1, bare til feilmeldinger
  surface-inverse: '#2C1E16'      # espressobrun, toppfelt og tallfliser. Ingen mørk modus i v1
  ink-inverse: '#FFFDF9'          # 15.85:1 mot surface-inverse
  ink-inverse-secondary: '#E5DDD0' # 11.95:1 mot surface-inverse
  focus-inverse: '#F4D03F'        # gul, 10.69:1 mot surface-inverse, fokusring i toppfeltet
typography:
  # Systemfonter (Tailwinds font-sans). Ingen nettfonter, så appen virker uten nett.
  page-title:
    fontFamily: 'ui-sans-serif, system-ui, sans-serif'
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  section-title:
    fontFamily: 'ui-sans-serif, system-ui, sans-serif'
    fontSize: 18px
    fontWeight: '600'
    lineHeight: '1.4'
  question:
    fontFamily: 'ui-sans-serif, system-ui, sans-serif'
    fontSize: 20px
    fontWeight: '500'
    lineHeight: '1.45'
  body:
    fontFamily: 'ui-sans-serif, system-ui, sans-serif'
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  meta:
    fontFamily: 'ui-sans-serif, system-ui, sans-serif'
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.4'
  score:
    fontFamily: 'ui-sans-serif, system-ui, sans-serif'
    fontSize: 36px
    fontWeight: '700'
    lineHeight: '1.1'
rounded:
  sm: 4px
  md: 6px
  lg: 8px
  full: 9999px
spacing:
  # Tailwinds 4-baserte skala brukes som den er. Bare navngitte unntak her.
  gutter-mobile: 16px
  gutter-desktop: 24px
  content-max: 768px              # max-w-3xl
  tap-min: 44px                   # minste høyde på knapper og alternativer
components:
  button-primary:
    background: '{colors.accent-strong}'
    foreground: '{colors.surface}'
    hover: '{colors.accent-hover}'
    radius: '{rounded.md}'
    minHeight: '{spacing.tap-min}'
  button-secondary:
    background: '{colors.surface}'
    foreground: '{colors.ink}'
    border: '1px solid {colors.border-control}'
    radius: '{rounded.md}'
    minHeight: '{spacing.tap-min}'
  button-danger:
    background: '{colors.error}'
    foreground: '{colors.surface}'
    radius: '{rounded.md}'
    minHeight: '{spacing.tap-min}'
  input:
    background: '{colors.surface}'
    border: '1px solid {colors.border-control}'
    radius: '{rounded.sm}'
    minHeight: '{spacing.tap-min}'
  option-card:
    background: '{colors.surface}'
    border: '1px solid {colors.border-control}'
    border-selected: '2px solid {colors.accent-strong}'
    background-selected: '{colors.surface-muted}'
    radius: '{rounded.lg}'
    minHeight: '{spacing.tap-min}'
  card:
    background: '{colors.surface}'
    border: '1px solid {colors.border-subtle}'
    radius: '{rounded.lg}'
  coverage-bar:
    track: '{colors.border-subtle}'
    fill: '{colors.accent-strong}'
    height: 8px
    radius: '{rounded.full}'
  ai-badge:
    background: '{colors.surface-sunken}'
    foreground: '{colors.ink-secondary}'
    radius: '{rounded.full}'
  test-mode-banner:
    background: '{colors.surface-sunken}'
    foreground: '{colors.ink}'
    border-bottom: '2px solid {colors.accent}'
  result-mark-correct:
    foreground: '{colors.success}'
  result-mark-wrong:
    foreground: '{colors.error}'
  focus-ring:
    outline: '2px solid {colors.accent-strong}'
    offset: 2px
---

## Brand & Style

FåreQuiz skal føles **effektiv, enkel og seriøs, med litt mer liv enn et skjema**. Den er et verktøy for studenter som skal lære noe. Flatene er kremhvite og varme beige, og det er mye luft rundt innholdet. Terrakotta viser hva som er neste handling, og ochre gir små lekne detaljer. Startsiden peker alltid mot det neste studenten kan gjøre. Det er ingen konfetti eller maskoter. Fremgangen vises med tydelige markører, for eksempel lært-prikkene under «Øv på feil».

Appen bruker Tailwind CSS i Django-maler og arver Tailwinds standarder for farger, avstand og skygger. Dette dokumentet beskriver bare avvikene: aksentfargen, typografien, minstestørrelser og noen få egne komponenter. Den ferdige CSS-filen fra Tailwind committes i repoet, slik at sensor ikke trenger Node eller et byggesteg.

## Colors

Paletten er varm beige og espressobrun, med terrakotta som hovedfarge og ochre som detalj. Den erstatter den kalde grå- og grønnfargen, og den er valgt for å være varm og innbydende.

- **Tonet bakgrunn (`{colors.page-bg}`)** er bakgrunnen for siden. Den har et diskret prikkemønster (dot-grid): `{colors.border-subtle}` (`#E5DDD0`), 1px prikker i et 20px rutenett. Mønsteret gir tekstur uten å konkurrere med innholdet. Teksten har fortsatt full kontrast mot bakgrunnen (14,33:1 for `{colors.ink}`). **Hvit (`{colors.surface}`)** er bakgrunnen for kort og flashcard.
- **Ochre (`{colors.accent}`, `#D9A21B`)** er dekorativ. Kontrasten mot beige er 2,05:1, så den brukes **bare** til ullskyss-merket i toppfeltet, til den tynne linjen under testmodus-banneret og til dekor. Den brukes aldri til tekst, og heller ikke til fremdrift.
- **Terrakotta (`{colors.accent-strong}`, `#B04A26`)** er hovedfargen. Den brukes på hovedknapper (hvit tekst, 5,45:1), lenker, fokusringen, valgt svaralternativ og fremdriftslinjen. Ved hover blir den **`{colors.accent-hover}`** (`#8E3A1C`, 7,58:1). Vi bruker `#B04A26` og ikke `#C85A32`, fordi `#C85A32` bare gir 4,23:1 med hvit tekst, under WCAG-kravet på 4,5:1 for vanlig tekst.
- **Tekst:** Vanlig tekst bruker `{colors.ink}`. Hjelpetekst og metadata som dato, antall og modellnavn bruker `{colors.ink-secondary}`, med 7,6:1.
- **Kanter:** Inndatafelt og svaralternativer bruker `{colors.border-control}` (4,8:1), fordi WCAG 1.4.11 krever minst 3:1 for kanter som viser hvor man kan klikke. `{colors.border-subtle}` brukes bare til skillelinjer og kortkanter som ikke er klikkbare.
- **Riktig og feil:** `{colors.success}` og `{colors.error}` brukes bare i resultater og feilmeldinger, og alltid sammen med ikon og tekst.

Den eneste mørke flaten er toppfeltet og tallfliene (`{colors.surface-inverse}`). Resten av siden er lys. Det gir et moderne uttrykk uten mørk modus, som gruppa sa nei til for v1. Unngå gradienter, flere aksentfarger og farget bakgrunn bak tekst. V1 har ikke mørk modus.

## Typography

Appen bruker systemfonter (Tailwinds `font-sans`). De er raske, ser kjente ut på alle enheter og krever ingen nedlasting.

- `{typography.page-title}`: én per side, for eksempel emnenavnet eller notatnavnet.
- `{typography.section-title}`: deloverskrifter som «Quizer», «Historikk» og «Lag ny quiz».
- `{typography.question}`: selve spørsmålsteksten i quiz og «Øv på feil». Den er større enn brødteksten, fordi den er det viktigste på skjermen.
- `{typography.body}`: alt annet, inkludert svaralternativene.
- `{typography.meta}`: dato, antall, vanskelighetsgrad og KI-merket.
- `{typography.score}`: poengsum og dekningsgrad i prosent. Tallene bruker `tabular-nums`, slik at de står på linje.

All tekst angis i `rem`, slik at 200 % tekstforstørrelse virker (WCAG 1.4.4). Teksten skrives aldri i store bokstaver, og den er aldri smalere enn 16px på mobil.

## Layout & Spacing

Siden har én kolonne med maks bredde `{spacing.content-max}` (768px), sentrert. Sidemargen er `{spacing.gutter-mobile}` på mobil og `{spacing.gutter-desktop}` fra `md` og oppover. Avstand følger Tailwind-skalaen (4, 8, 12, 16, 24, 32 px). Mellom seksjoner er det 32px, og mellom elementer i en liste 12px.

Knapper og svaralternativer er minst `{spacing.tap-min}` (44px) høye. Det er godt over WCAG-kravet på 24px (2.5.8). På mobil er knappene i quizen like brede som skjermen.

## Elevation & Depth

Kort skal løftes fra bakgrunnen. De hvite kortene har en tydelig, men lett skygge (`card`), og flashcardet i quizen har en litt tyngre skygge (`flashcard`). Skyggen er mørk nok til å se, men den er ikke tung. Kort som kan klikkes, løftes 2px når musepekeren er over, med mykere skygge. Bevegelsen slås av hvis brukeren har valgt redusert bevegelse. Toppfeltet har ingen skygge, siden det er mørkt.

## Shapes

Hjørnene er avrundet, men forsiktig. Inndatafelt har `{rounded.sm}`, knapper `{rounded.md}`, og kort og svaralternativer `{rounded.lg}`. `{rounded.full}` brukes bare på dekningsstolpen og KI-merket.

## Components

- **Hovedknapp (`button-primary`):** `{colors.accent-strong}` med hvit tekst. Det er høyst én per skjermbilde, for eksempel «Lag quiz», «Neste», «Lever» eller «Last opp».
- **Sekundærknapp (`button-secondary`):** Kremhvit med brun kant, for «Forrige», «Avbryt» og «Gi nytt navn».
- **Fareknapp (`button-danger`):** Rød med hvit tekst. Brukes bare på bekreftelsessiden for sletting av emne.
- **Svaralternativ (`option-card`):** Hele kortet er en radioknapp med etikett. Et valgt alternativ får tykkere `{colors.accent-strong}`-kant, beige bakgrunn og en fylt radioknapp. Valget vises altså med form og ikke bare med farge. Det er tre alternativer, og de står under hverandre på alle skjermer.
- **Dekningsstolpe (`coverage-bar`):** Stolpen er 8px høy, og prosenttallet står alltid som tekst ved siden av. På notatsiden vises en liten stolpe for hvert nivå (lett, middels og vanskelig) under totalen.
- **KI-merke (`ai-badge`):** Et beige merke med et lite ikon og teksten «Laget av KI». På quizsidene står den fulle teksten (se EXPERIENCE.md).
- **Testmodus-banner (`test-mode-banner`):** Et beige felt med teksten «Testmodus: quizene bruker mock-svar, ingen KI kalles». Det ligger under toppfeltet på alle sider når testmodus er på, med en tynn grønn-blå linje under.
- **Resultatmerke (`result-mark-*`):** Ikonene ✓ eller ✗ (SVG) sammen med teksten «Riktig» eller «Feil», i `{colors.success}` eller `{colors.error}`.
- **Kort (`card`):** For emner, notater og quizer i lister. Hele kortet er én lenke. Hvit bakgrunn, `{colors.border-subtle}`-kant og skyggen `0 4px 12px` med lav opasitet.
- **Flashcard (`flashcard`):** Spørsmålet i quizen og «Øv på feil». Kortet står midt på siden, maks 560px bredt, med større skygge enn `card`. Svaralternativene står under kortet, i en egen liste.
- **Svaralternativ, hover (`option-card:hover`):** Bakgrunnen blir `{colors.card-hover}`, kanten blir `{colors.accent-strong}`, og alternativet løftes 1px. Teksten beholder full kontrast.
- **Fokusring (`focus-ring`):** 2px `{colors.accent-strong}` med 2px avstand, på alle elementer som kan få fokus. I toppfeltet brukes `{colors.focus-inverse}`, fordi den mørke fargen ikke har nok kontrast der. Den fjernes aldri (`outline: none` er forbudt).
- **Logo (`brand`):** Et lite ullskyss-merke i `{colors.accent}` (ochre) foran navnet «FåreQuiz». Navnet er i fet skrift med tettere bokstavavstand. Merket er bare dekorativt, og det er ingen figur med ansikt.
- **Toppfelt (`topbar`):** `{colors.surface-inverse}` med `{colors.ink-inverse}`-tekst. «Logg ut» er `{colors.ink-inverse-secondary}`.
- **Tallflis (`stat-tile`):** `{colors.surface-inverse}` med tallet i `{typography.score}` og en kort tekst under. Brukes på emnesiden for dekning og antall i feilbanken.

## Do's and Don'ts

| Gjør | Ikke gjør |
|---|---|
| Bruk `{colors.accent-strong}` til tekst, knapper og fokus | Bruk `{colors.accent}` (#D9A21B) til tekst eller som bakgrunn bak hvit tekst |
| Vis prosent som tekst ved siden av hver stolpe | La farge eller stolpelengde være eneste informasjon |
| Vis riktig og feil med ikon, tekst og farge | Vis riktig og feil bare med grønt og rødt |
| Ha høyst én hovedknapp per skjermbilde | Ha flere farget knapper som konkurrerer |
| Gi knapper og alternativer minst 44px høyde | Bruk små tekstlenker som eneste handling på mobil |
| Hold deg til beige, brunt, terrakotta og ochre | Bruk gradienter, illustrasjoner, konfetti eller maskoter |
