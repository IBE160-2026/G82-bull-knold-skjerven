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
  # Varm palett: sand, krem og espressobrun, med kaffebrun som hovedfarge og latte som detalj.
  # Kontrast er målt mot surface (#FAF7F2).
  surface: '#FAF7F2'               # kremhvit, kort og flashcard. 15.25:1 for ink
  surface-muted: '#F5EFE6'        # svak variasjon, bakgrunn i tallfelt og bak hover
  surface-sunken: '#E3D6C2'       # KI-merke og testmodus-banner. 6.10:1 for ink-secondary
  page-bg: '#EFE6D8'              # varm sand for hele siden, med prikkemønster
  border-subtle: '#DFD2BE'        # skillelinjer, prikkemønster og kortkanter, bare til pynt
  border-control: '#5C3A21'       # 9.44:1 mot surface. Kanter på inndatafelt og alternativer
  ink: '#2B1D14'                  # espressobrun, 15.25:1 mot surface
  ink-secondary: '#5E4636'        # 8.17:1 mot surface
  accent: '#D5BC96'               # latte, bare dekor, hover-bakgrunn og merke. Aldri tekst eller fremdrift
  accent-strong: '#5C3A21'        # kaffebrun, knapper, lenker, fokus, fremdrift og valgt alternativ. 9.44:1
  accent-hover: '#3E2716'         # 13.04:1 mot surface, hover og trykk på knapper
  card-hover: '#D5BC96'           # latte, bakgrunn på svaralternativ ved hover. 8.90:1 med ink
  success: '#3F624D'              # salvie, 6.41:1 mot surface. Riktig svar, med ✓
  error: '#A34420'                # terrakotta, 5.77:1 mot surface og 6.17:1 med hvit tekst. Feil svar, med ✕
  surface-inverse: '#2B1D14'      # espressobrun, toppfelt og tallfliser. Ingen mørk modus i v1
  ink-inverse: '#FAF7F2'          # 15.25:1 mot surface-inverse
  ink-inverse-secondary: '#D5BC96' # 8.90:1 mot surface-inverse
  focus-inverse: '#D5BC96'        # latte, 8.90:1 mot surface-inverse, fokusring i toppfeltet
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

Paletten er varm og holder seg til sand, krem og brunt. Kaffebrun er hovedfargen, latte er detaljen, og terrakotta og salvie brukes bare til tilbakemelding om svar. Den erstatter den kalde grå-, svarte og grønne fargen, og den er valgt for å være varm og innbydende.

- **Tonet bakgrunn (`{colors.page-bg}`)** er bakgrunnen for siden, fra topp til bunn. Den har et mønster av små biler og lastebiler i `{colors.border-subtle}`, tegnet som SVG-bakgrunn (`vehicles.svg`) med en rute på 240×160px. Mønsteret viser sedan, sportsbil, F1-bil, stasjonsvogn, pickup, SUV, cabriolet, planbil, semitrailer og vogntog. Mønsteret er rolig og lavt i kontrast, så det gir tekstur uten å konkurrere med innholdet. Bilene er dekor og har ingen informasjon.
- **Krem (`{colors.surface}`)** er bakgrunnen for kort og flashcard. Kortene har en brunlig skygge (`rgba(62, 39, 35, 0.12)`), slik at de løfter seg frem.
- **Tekst:** Vanlig tekst bruker `{colors.ink}` (espressobrun, 15,25:1). Hjelpetekst og metadata bruker `{colors.ink-secondary}`, med 8,17:1.
- **Kaffebrun (`{colors.accent-strong}`)** er hovedknapper (med krem tekst), lenker, fokusring, fremdriftslinje og valgt svaralternativ. Hover-tilstand på knapper er `{colors.accent-hover}`.
- **Latte (`{colors.accent}`)** er dekorativ. Den brukes til hover-bakgrunn på svaralternativ (`{colors.card-hover}`), til ikonet i logoen og til dekor. Latte gir for lav kontrast mot sand (1,48:1) til å være kant, ikon eller fremdrift alene, så den brukes ikke til noe som må synes.
- **Terrakotta (`{colors.error}`, `#A34420`)** brukes bare til feil svar. Den erstatter den skarpe rødfargen. Vi bruker `#A34420` og ikke `#C85A32`, fordi `#C85A32` bare gir 4,23:1 med hvit tekst, under WCAG-kravet på 4,5:1.
- **Salvie (`{colors.success}`, `#3F624D`)** brukes bare til riktig svar. Den erstatter den skarpe grønnfargen.

Tilbakemelding om svar skal alltid ha ikon og tekst i tillegg til farge: ✓ og «Riktig» for riktig svar, ✕ og «Feil» for feil svar.

Den eneste mørke flaten er toppfeltet og tallfliene (`{colors.surface-inverse}`). Resten av siden er lys. Det gir et moderne uttrykk uten mørk modus, som gruppa sa nei til for v1. Unngå gradienter, flere farger enn de som står her, og farget bakgrunn bak tekst.

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

- **Hovedknapp (`button-primary`):** `{colors.accent-strong}` med krem tekst (`{colors.surface}`). Det er høyst én per skjermbilde, for eksempel «Lag quiz», «Neste», «Lever» eller «Last opp».
- **Sekundærknapp (`button-secondary`):** Kremhvit med brun kant, for «Forrige», «Avbryt» og «Gi nytt navn».
- **Fareknapp (`button-danger`):** Rød med hvit tekst. Brukes bare på bekreftelsessiden for sletting av emne.
- **Svaralternativ (`option-card`):** Hele kortet er en radioknapp med etikett. Et valgt alternativ får tykkere `{colors.accent-strong}`-kant, beige bakgrunn og en fylt radioknapp. Valget vises altså med form og ikke bare med farge. Det er tre alternativer, og de står under hverandre på alle skjermer.
- **Fremdriftslinje med sportsbil (`progress`):** Stolpen er 8px høy i `{colors.border-subtle}`, med fyll i `{colors.accent-strong}`. En sportsbil i `{colors.accent-strong}` står på enden av fyllet og flyttes med fremdriften. Den er dekorativ (`aria-hidden`), og «Spørsmål 3 av 10» gir informasjonen i tekst.
- **Dekningsstolpe (`coverage-bar`):** Stolpen er 8px høy, og prosenttallet står alltid som tekst ved siden av. På notatsiden vises en liten stolpe for hvert nivå (lett, middels og vanskelig) under totalen.
- **KI-merke (`ai-badge`):** Et beige merke med et lite ikon og teksten «Laget av KI». På quizsidene står den fulle teksten (se EXPERIENCE.md).
- **Testmodus-banner (`test-mode-banner`):** Et beige felt med teksten «Testmodus: quizene bruker mock-svar, ingen KI kalles». Det ligger under toppfeltet på alle sider når testmodus er på, med en tynn `{colors.accent}`-linje under.
- **Resultatmerke (`result-mark-*`):** Ikonene ✓ eller ✗ (SVG) sammen med teksten «Riktig» eller «Feil», i `{colors.success}` eller `{colors.error}`.
- **Kort (`card`):** For emner, notater og quizer i lister. Hele kortet er én lenke. Hvit bakgrunn, `{colors.border-subtle}`-kant og skyggen `0 4px 12px` med lav opasitet.
- **Flashcard (`flashcard`):** Spørsmålet i quizen og «Øv på feil». Kortet står midt på siden, maks 560px bredt, med større skygge enn `card`. Svaralternativene står under kortet, i en egen liste.
- **Svaralternativ, hover (`option-card:hover`):** Bakgrunnen blir `{colors.card-hover}` (latte), kanten blir `{colors.accent-strong}`, og alternativet løftes 1px. Teksten beholder full kontrast.
- **Fokusring (`focus-ring`):** 2px `{colors.accent-strong}` med 2px avstand, på alle elementer som kan få fokus. I toppfeltet brukes `{colors.focus-inverse}`, fordi den mørke fargen ikke har nok kontrast der. Den fjernes aldri (`outline: none` er forbudt).
- **Logo (`brand`):** Et lite flashcard-merke, to kort på skrå, i `{colors.accent}` og `{colors.surface}`, foran navnet «FåreQuiz». Navnet er i fet skrift med tettere bokstavavstand. Merket er bare dekorativt.
- **Toppfelt (`topbar`):** `{colors.surface-inverse}` med `{colors.ink-inverse}`-tekst. «Logg ut» er `{colors.ink-inverse-secondary}`.
- **Tallflis (`stat-tile`):** `{colors.surface-inverse}` med tallet i `{typography.score}` og en kort tekst under. Brukes på emnesiden for dekning og antall i feilbanken.

## Do's and Don'ts

| Gjør | Ikke gjør |
|---|---|
| Bruk `{colors.accent-strong}` til tekst, knapper og fokus | Bruk `{colors.accent-strong}` til tekst og knapper, og `{colors.accent}` bare til dekor eller hover |
| Vis prosent som tekst ved siden av hver stolpe | La farge eller stolpelengde være eneste informasjon |
| Vis riktig og feil med ikon, tekst og farge | Vis riktig og feil bare med grønt og rødt |
| Ha høyst én hovedknapp per skjermbilde | Ha flere farget knapper som konkurrerer |
| Gi knapper og alternativer minst 44px høyde | Bruk små tekstlenker som eneste handling på mobil |
| Hold deg til sand, krem og brunt, med latte som detalj | Bruk gradienter, illustrasjoner, konfetti eller maskoter |

## Forside (S1)

Forsiden for besøkende har en hero: overskrift og kort intro til venstre med knappen «Registrer deg», og en stabel med tre flashcards til høyre. Under hero er tre kremhvite informasjonskort (last opp, ta quizen, øv på feilene), og så innloggingsskjemaet. Flashcardene er dekorative (`aria-hidden`), og informasjonen står i teksten.
