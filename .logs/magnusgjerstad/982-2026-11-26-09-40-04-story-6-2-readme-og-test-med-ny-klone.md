# Story 6.2: README og test med ny klone

## 2026-11-26 kl. 09:40 — MagnusGjerstad

### Oppgave
Pushe story 6.1 og gå videre til 6.2, slik at sensor kan installere og kjøre appen med README-en alene, uten hjelp og uten API-nøkkel (FR-29, FR-30, SM-1).

### Plan
- **Story 6.1:**
  - Pushet `story-6-1-testbruker-med-eksempeldata` og laget PR #13.
  - Basen er 5.3-branchen, fordi #12 ikke er merget ennå.
- **Branch:** `story-6-2-readme-og-test-med-ny-klone`, laget fra 6.1-branchen.
- **`bmad-build`** med [epic-6-context.md](../../_bmad-output/implementation-artifacts/epic-6-context.md).
  - Spec: [spec-6-2-readme-og-test-med-ny-klone.md](../../_bmad-output/implementation-artifacts/spec-6-2-readme-og-test-med-ny-klone.md).
  - Beslutninger 26.11:
    - CI-seed kjører bare når `ki/mock/manifest.json` finnes. Ellers gir CI en advarsel.
    - Spec-en beholdes som én story.
  - Implementert av en subagent. Deretter review i tre lag og rettelser.

### Resultat
- Commit `b0b3840` på `story-6-2-readme-og-test-med-ny-klone`, ikke pushet.
- **Funn under planleggingen:** `requirements.txt` manglet `whitenoise` siden 1.3, så pip-veien ga en app som ikke starter. Fila er generert på nytt med `uv export --no-hashes --frozen --no-dev`, uten `ruff`.
- **README:** skrevet om til en oppskrift for sensor:
  - hva appen gjør og hva som trengs
  - kloning og de fire stegene med uv eller pip, med `py -3.14` og hint om PowerShell-policy for Windows
  - testbrukeren og testmodus (når den er på, og hva banneret betyr)
  - ekte modell med `.env` og standardmodellen
  - mobil på samme nett, med en advarsel om `DEBUG=True`
  - et avsnitt for gruppa om `lag_mocksvar` og `requirements.txt`
- **`farequiz/tests_readme.py`:** 13 tester. De sjekker seksjonene og stegene i rekkefølge for uv og pip. Testbrukeren, banneret og Python-versjonen leses fra koden, og `.env`-variablene sjekkes mot `.env.example`. `requirements.txt` skal ha alle avhengighetene og ikke dev-verktøy.
- **CI:**
  - Nytt steg: «requirements.txt er i takt».
  - Nytt steg: «Seed på tom database», som hopper over med en advarsel til `ki/mock/` finnes.
- **Review:** 26 funn. 15 ble rettet og 10 avvist med begrunnelse. 1 er utsatt til `deferred-work.md`: uv-versjonen i CI kan gi en falsk diff.
- **Verifisert:**
  - ruff, `makemigrations --check` og 560 tester er grønne (1 hoppet over).
  - Eksporten gir samme `requirements.txt` hver gang.
  - Underagenten installerte fra `requirements.txt` i et rent venv med Python 3.14, og `manage.py check` gikk gjennom.
- **Sprint-status:** `6-2: review`, med en kommentar om klonetesten og `ki/mock/`.

### Åpne punkter
- **Manuell test med ny klone.** Den gjøres av en i gruppa som ikke skrev README-en, når `ki/mock/` er committet. Følg README-en ordrett uten `.env`, én gang på Windows og én gang på macOS eller Linux. Noter hvem, hvilket OS og hvilken dato. Sjekkliste:
  - [ ] klone, `uv sync` (eller pip), `migrate`, `seed_testdata` og `runserver` virker
  - [ ] logge inn som testbrukeren
  - [ ] laste opp et testdokument og lage en quiz
  - [ ] ta quizen og levere
  - [ ] øve på feil
  - [ ] se at dekningsgraden endrer seg
  - [ ] avvik rettes i README-en eller koden, og testen føres i sesjonsloggen
- Når `ki/mock/` committes, fjern setningen «Filene er ikke committet ennå …» under «For gruppa» i README-en. Sjekk også at CI-steget «Seed på tom database» faktisk kjører.
- README-en slutter med «Changelog: Fjernet Henrik L Knold … :/» under «Medlemmer». Sensor leser den, så gruppa bør vurdere å fjerne eller omformulere linjen.
