# Addendum til PRD: teknologi og vurderte alternativer

Dette er innspill til arkitekturen. Kravene står i [prd.md](prd.md).

## Valgt tech stack (gruppemøte 11.11.2026)

- **Django + SQLite.** SQLite er en ekte database i én fil i prosjektmappen. Den krever ingen server, så sensor kan kjøre appen lokalt (NFR-4).
- **Grensesnitt:** Django-maler med litt HTMX/JS for fremdrift (FR-14) og lagring av svar underveis (FR-18).
- **KI:** Anthropics Python-SDK. Standardmodellen er Claude Sonnet 5.5, og modellnavnet settes i `.env` (FR-29).
- **PDF** sendes hel til modellen som dokument (FR-9). For DOCX hentes teksten ut, for eksempel med `python-docx`.
- **Testmodus:** Et flagg i `.env`. Står det på, leser KI-modulen lagrede JSON-svar fra mock-mappen i stedet for å kalle API-et (FR-27). Mock-svarene lages ved å kjøre testdokumentene mot ekte modell én gang.
- **Testbruker og eksempeldata** lages med en seed-kommando eller fixture (FR-28).
- **KI-modul:** Alle kall går gjennom én modul (NFR-5). Den har prompt, JSON-skjema for quizen, formatsjekk og én ny generering (FR-13).
- **Ingen bakgrunnsjobb i v1.** Genereringen kjøres i forespørselen, med timeout (FR-15).

## Plassering i repoet

Faglærers kriterium 7 gjelder ryddighet i repoet.

- **Testdokumenter og mock-svar:** I egne mapper i repoet, slik at testmodus virker rett etter kloning.
- **`.env`:** Ligger i `.gitignore`. Bare `.env.example` uten ekte nøkkel ligger i repoet.
- **SQLite-fil og opplastede filer:** Ligger i `.gitignore`. Testbrukeren lages med seed-kommandoen.

## Vurderte alternativer

| Alternativ | Hvorfor ikke valgt |
|---|---|
| FastAPI/Flask + SQLite | Innlogging, sesjoner og tilgangssjekk må settes sammen selv. Django har dette innebygd, og FR-1 til FR-3 er suksesskriterier. |
| Next.js + SQLite | Innlogging må settes sammen selv, og React gir mer å lære. Gruppa valgte den anbefalte stacken. |
| Andre KI-leverandører | Gruppa valgte bare Anthropic for å holde det enkelt. |
