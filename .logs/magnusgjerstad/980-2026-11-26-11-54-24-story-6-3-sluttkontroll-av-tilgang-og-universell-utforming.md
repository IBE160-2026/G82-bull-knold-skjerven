# Story 6.3: Sluttkontroll av tilgang og universell utforming

## 2026-11-26 kl. 11:54 — MagnusGjerstad

### Oppgave
Neste story etter mock-svarene: en sluttkontroll som viser at ingen ser andres data (SM-5), at alle sider krever innlogging (FR-2), at quizsidene er KI-merket med modellnavn (SM-8), og at skjermbildene ikke bryter WCAG 2.2 A/AA (SM-7).

### Plan
- **Branch:** `story-6-3-sluttkontroll-av-tilgang-og-universell-utforming`, laget fra `main` (`d9ab386`).
- **Først en egen commit, `e0efaef`:** fjernet `skipTest`-vakten i `EkteMockfilerTest`, nå som `ki/mock/` er committet.
- **`bmad-build`** med [spec-6-3-sluttkontroll-av-tilgang-og-universell-utforming.md](../../_bmad-output/implementation-artifacts/spec-6-3-sluttkontroll-av-tilgang-og-universell-utforming.md).
- **Beslutninger 26.11:**
  - axe kjøres med Playwright og axe-core som dev-avhengigheter, både lokalt og i et eget CI-steg.
  - 405 godtas for metoder viewet ikke tar imot, når svaret er det samme som for en ID som ikke finnes.
  - Storyen er beholdt som én spec.
- **Gjennomføring:** en underagent implementerte. Deretter kom review i tre lag og rettelser fra samme underagent. Den traff bruksgrensen én gang og ble startet igjen.

### Resultat
- **Commit:** `507fa3b`, ikke pushet.
- **`studier/tests/test_tilgang_urler.py`:**
  - Går gjennom alle URL-mønstrene fra resolveren.
  - Med Olas ID-er får Kari 404 med «Fant ikke siden», og hele databasen er uendret.
  - Metoder viewet ikke tar imot gir 405, samme svar som for en ukjent ID.
  - Et nytt mønster med ID uten oppsett gir feil med navnet sitt.
  - En kontrolltest viser at Ola ikke får 404 på egne ID-er, også for mønstrene som bare tar imot POST.
  - Utlogget GET og POST sendes til Logg inn med `next`. Logg inn, Registrer og Personvern er offentlige.
- **`studier/tests/test_ki_merke.py`:** «Laget av KI» og modellnavnet vises på S7, S9 og S12 i testmodus.
- **`farequiz/tests_axe.py`:** axe-core 4.14.0 i Chromium 159.
  - 44 tilstander: S1–S16 med S1b, S6b og S6c, 5 tilstander ved 320 px og en side med engelsk innhold. Ingen brudd.
  - Kjøres med `--tag nettleser`. Vanlig `manage.py test` utelater den.
  - Mangler Playwright, feiler testen i stedet for å bli hoppet over.
- **`farequiz/testrunner.py`:** utelater taggen `nettleser`. Hjelperne `godta` og `lag_olas` er flyttet til `fabrikk.py`.
- **CI:**
  - Nye steg for Chromium og nettlesertesten.
  - «Seed på tom database» kjører nå alltid.
- **[sluttkontroll-6-3.md](../../_bmad-output/implementation-artifacts/sluttkontroll-6-3.md):** axe-resultatet med versjoner, avviket om 405, og sjekklisten for den manuelle kontrollen.
- **Review:** 22 funn. 11 er rettet og 11 avvist med begrunnelse. Ingenting er utsatt.
- **Verifisert:** ruff og `makemigrations --check` er rene. 572 tester er grønne, nettlesertesten har 45 grønne tester, og `requirements.txt` er uendret.
- **Sprint-status:** `6-3: review`.

### Åpne punkter
- Den manuelle kontrollen med tastatur og med NVDA eller VoiceOver gjøres av en i gruppa etter sjekklisten i `sluttkontroll-6-3.md`. Den dekker fokus, statusmeldinger, S1b, feilmeldinger, 320 px og 200 % tekst.
- **Kontrasten på feiltekst er for lav:** `--color-error` `#A34420` gir 4,14:1 mot kartlinjene `#DFD2BE`, under kravet på 4,5:1.
  - Forslag: endre fargen til `#963D1C`, som gir 4,73:1. Alternativet er en bakgrunn bak feilmeldingene.
  - Gruppa bestemmer, fordi det er en endring i designet.
- **`/jobber/<id>/steg/`** gir 200 for en jobb som ikke finnes, men 404 for en annens jobb. Det viser bare at en fortløpende ID finnes, ingen data. Vurder om de to svarene skal være like.
- **CI-stegene for Chromium og axe** er ikke kjørt på GitHub ennå. Sjekk den første kjøringen etter push.
