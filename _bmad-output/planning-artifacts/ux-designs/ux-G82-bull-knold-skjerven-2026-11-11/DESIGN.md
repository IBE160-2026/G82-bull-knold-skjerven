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
  # Gråtoner fra Tailwinds gray-skala. Kontrast er målt mot surface (#FFFFFF).
  surface: '#FFFFFF'
  surface-muted: '#F9FAFB'        # gray-50, sidebakgrunn bak kort
  surface-sunken: '#F3F4F6'       # gray-100, KI-merke, testmodus-banner
  border-subtle: '#E5E7EB'        # gray-200, 1.24:1, bare til pynt (skillelinjer)
  border-control: '#6B7280'       # gray-500, 4.83:1, kanter på inndatafelt og alternativer
  ink: '#111827'                  # gray-900, 17.7:1
  ink-secondary: '#4B5563'        # gray-600, 7.6:1
  accent: '#D97757'               # Claude-oransje, 3.12:1, bare til flater, ikoner og stor tekst
  accent-strong: '#B85636'        # 4.75:1, knapper, lenker, fokusring, dekningsstolpe
  accent-hover: '#9C4A2B'         # 6.13:1, hover og trykk
  success: '#15803D'              # green-700, 5.02:1
  error: '#B91C1C'                # red-700, 6.47:1
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

FåreQuiz skal føles **effektiv, enkel og seriøs**. Den er et arbeidsverktøy for studenter som skal lære noe, ikke et spill. Flatene er hvite og gråtonede, og det er mye luft rundt innholdet. Én varm aksentfarge viser hva som er neste handling og hvor langt studenten har kommet. Det er ingen konfetti, maskoter, streaker eller feiringer. Fremgangen er belønningen.

Appen bruker Tailwind CSS i Django-maler og arver Tailwinds standarder for farger, avstand og skygger. Dette dokumentet beskriver bare avvikene: aksentfargen, typografien, minstestørrelser og noen få egne komponenter. Den ferdige CSS-filen fra Tailwind committes i repoet, slik at sensor ikke trenger Node eller et byggesteg.

## Colors

Paletten er hvit og grå med én aksentfarge.

- **Hvit (`{colors.surface}`)** er bakgrunnen for alt innhold. **Gray-50 (`{colors.surface-muted}`)** brukes bak kort på emne- og notatsidene, slik at kortene skiller seg ut uten skygge.
- **Claude-oransje (`{colors.accent}`, `#D97757`)** er aksentfargen. Kontrasten mot hvitt er 3,1:1, så den brukes **bare** til flater, ikoner, store tall og den tynne linjen under testmodus-banneret. Den brukes aldri til vanlig tekst.
- **Mørk oransje (`{colors.accent-strong}`, `#B85636`)** er den brukbare varianten med 4,75:1. Den brukes på hovedknapper (hvit tekst), lenker, fokusringen, valgt svaralternativ og dekningsstolpen. Ved hover blir den **`{colors.accent-hover}`**.
- **Tekst:** Vanlig tekst bruker `{colors.ink}`. Hjelpetekst og metadata som dato, antall og modellnavn bruker `{colors.ink-secondary}`, med 7,6:1.
- **Kanter:** Inndatafelt og svaralternativer bruker `{colors.border-control}` (4,8:1), fordi WCAG 1.4.11 krever minst 3:1 for kanter som viser hvor man kan klikke. `{colors.border-subtle}` brukes bare til skillelinjer og kortkanter som ikke er klikkbare.
- **Riktig og feil:** `{colors.success}` og `{colors.error}` brukes bare i resultater og feilmeldinger, og alltid sammen med ikon og tekst.

Unngå gradienter, flere aksentfarger og oransje bak tekst. V1 har ikke mørk modus.

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

Appen bruker ikke skygger for å vise hierarki. Kort skilles fra bakgrunnen med `{colors.surface-muted}` bak og en tynn `{colors.border-subtle}`-kant. Den eneste skyggen er Tailwinds `shadow-sm` på toppfeltet når siden rulles.

## Shapes

Hjørnene er avrundet, men forsiktig. Inndatafelt har `{rounded.sm}`, knapper `{rounded.md}`, og kort og svaralternativer `{rounded.lg}`. `{rounded.full}` brukes bare på dekningsstolpen og KI-merket.

## Components

- **Hovedknapp (`button-primary`):** `{colors.accent-strong}` med hvit tekst. Det er høyst én per skjermbilde, for eksempel «Lag quiz», «Neste», «Lever» eller «Last opp».
- **Sekundærknapp (`button-secondary`):** Hvit med grå kant, for «Forrige», «Avbryt» og «Gi nytt navn».
- **Fareknapp (`button-danger`):** Rød med hvit tekst. Brukes bare på bekreftelsessiden for sletting av emne.
- **Svaralternativ (`option-card`):** Hele kortet er en radioknapp med etikett. Et valgt alternativ får tykkere `{colors.accent-strong}`-kant, grå bakgrunn og en fylt radioknapp. Valget vises altså med form og ikke bare med farge. Det er tre alternativer, og de står under hverandre på alle skjermer.
- **Dekningsstolpe (`coverage-bar`):** Stolpen er 8px høy, og prosenttallet står alltid som tekst ved siden av. På notatsiden vises en liten stolpe for hvert nivå (lett, middels og vanskelig) under totalen.
- **KI-merke (`ai-badge`):** Et grått merke med et lite ikon og teksten «Laget av KI». På quizsidene står den fulle teksten (se EXPERIENCE.md).
- **Testmodus-banner (`test-mode-banner`):** Et grått felt med teksten «Testmodus: quizene er forhåndslagret, ingen KI kalles». Det ligger under toppfeltet på alle sider når testmodus er på, med en tynn oransje linje under.
- **Resultatmerke (`result-mark-*`):** Ikonene ✓ eller ✗ (SVG) sammen med teksten «Riktig» eller «Feil», i `{colors.success}` eller `{colors.error}`.
- **Kort (`card`):** For emner, notater og quizer i lister. Hele kortet er én lenke.
- **Fokusring (`focus-ring`):** 2px `{colors.accent-strong}` med 2px avstand, på alle elementer som kan få fokus. Den fjernes aldri (`outline: none` er forbudt).

## Do's and Don'ts

| Gjør | Ikke gjør |
|---|---|
| Bruk `{colors.accent-strong}` til tekst, knapper og fokus | Bruk `{colors.accent}` (#D97757) til tekst eller som bakgrunn bak hvit tekst |
| Vis prosent som tekst ved siden av hver stolpe | La farge eller stolpelengde være eneste informasjon |
| Vis riktig og feil med ikon, tekst og farge | Vis riktig og feil bare med grønt og rødt |
| Ha høyst én hovedknapp per skjermbilde | Ha flere oransje knapper som konkurrerer |
| Gi knapper og alternativer minst 44px høyde | Bruk små tekstlenker som eneste handling på mobil |
| Hold deg til hvitt, grått og én aksentfarge | Bruk gradienter, illustrasjoner, konfetti eller maskoter |
