# G82 — Pusher 30

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

Repoet inneholder gruppens applikasjon og dokumentasjon av utvikling, testing og kvalitetssikring med KI.

## Medlemmer

- Christian R Bull
- Martin Skjerven
- Magnus Gjerstad

Changelog: Fjernet Henrik L Knold ettersom han fortsatt ikke har gitt en lyd fra seg :/

## Testbruker

Kommandoen under lager en testbruker med emnet «Webutvikling», tre notater fra `testdokumenter/`, quizer, leverte forsøk, en feilbank og et påbegynt forsøk:

    uv run python manage.py seed_testdata

Logg inn med:

- E-post: `sensor@farequiz.no`
- Passord: `sensor123`

Kommandoen kjører alltid i testmodus og kaller ikke KI-tjenesten, men trenger mock-svarene i `ki/mock/` (se under). Du kan kjøre den flere ganger. Da slettes testbrukerens emner, og dataene lages på nytt. E-posten og passordet står også på innloggingssiden i testmodus.

## Testmodus og mock-svar

Uten `ANTHROPIC_API_KEY`, eller med `TESTMODUS=1`, kjører appen i testmodus. Da kalles ikke KI-tjenesten. Quizene hentes fra forhåndslagrede svar i `ki/mock/`, laget fra de fem filene i `testdokumenter/` (30 spørsmål per dokument og nivå, appen bruker de første N). En fil som ikke er et testdokument, gir et standard testdokument med en merknad. Testene kjører alltid i testmodus.

Mock-svarene lages med ekte modell av den som har gruppas nøkkel:

    uv run python manage.py lag_mocksvar

Kommandoen nekter å kjøre i testmodus, så sett `ANTHROPIC_API_KEY` og `TESTMODUS=0` i `.env` først. Den skriver `ki/mock/` (filene og `manifest.json`), som så committes. Filene er ikke committet ennå. Til noen med gruppas nøkkel har kjørt `lag_mocksvar` og committet `ki/mock/`, feiler generering i testmodus med `api_feil`. Kjør den på nytt når et testdokument, prompten eller `PROMPT_VERSJON` endres.
