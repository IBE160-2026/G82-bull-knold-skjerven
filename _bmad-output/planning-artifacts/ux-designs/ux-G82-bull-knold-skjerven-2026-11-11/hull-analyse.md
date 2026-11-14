# Hulanalyse: PRD mot UX-design

Gått gjennom FR-, NFR- og UJ-krav i `prd.md` mot `EXPERIENCE.md` og `DESIGN.md`, på branchen `forslag-design-martin`. Kun hull der designet ikke sier noe om en tilstand eller oppførsel som kravet forutsetter, er tatt med. Det som er dekket, er ikke listet.

## Mangler i designet

| # | Krav | Hva mangler | Forslag |
|---|---|---|---|
| 1 | FR-1: ugyldig e-post og passord under 8 tegn | S2 har bare tilstanden «E-posten finnes alt». | Legg til tilstander for ugyldig e-post og for kort passord, og en hjelpetekst om minst 8 tegn. |
| 2 | FR-4: tomt navn og samme navn to ganger | Ingen tilstander for emnenavn på S3 eller S4. | Legg til «Navnet kan ikke være tomt» og «Du har allerede et emne med dette navnet». |
| 3 | FR-5: gi emne nytt navn | S4 nevner «Gi nytt navn», men designet sier ikke om det er en egen side eller et skjema på S4. | **Må besluttes.** Forslag: skjema på S4 som åpnes med knappen, med samme feilmeldinger som FR-4. |
| 4 | FR-26: historikk | Ingen tilstand for notat uten leverte forsøk. | «Ingen forsøk ennå» på S7 i historikkdelen. |
| 5 | FR-12, FR-13, FR-15: feil fra KI-tjenesten | Timeout og feil format er dekket. Ingen tilstand for at tjenesten svarer med feil eller er utilgjengelig. | «KI-tjenesten svarte ikke. Prøv igjen.» med «Prøv igjen» som bruker samme fil og valg. |
| 6 | FR-8: opplasting uten valgt fil | Ingen tilstand for at brukeren trykker «Last opp» uten å ha valgt en fil. | «Velg en fil først.» ved filvelgeren, med fokus dit. |
| 7 | FR-18 og UJ-3: svar som må lagres | Designet forutsetter at svar er lagret, men sier ingenting om at økten kan være utløpt. Dette er ikke et krav i PRD-en. | **Spørsmål til gruppa.** Er det nok at svarene er lagret og brukeren logger inn på nytt? Hvis ja, legg til en kort tilstand på S1 som sender brukeren tilbake til samme spørsmål. |

## Funnet ved gjennomgang, ikke mangler

- Kravnumrene i `EXPERIENCE.md` stemmer med PRD-en. Det er ingen referanse til et FR-nummer som ikke finnes.
- FR-10 er fjernet, og designet nevner det ikke. Det er riktig.
- Dekningsgraden for emne uten notater er dekket på S3 og S4.
- Testmodus er dekket på alle sider, også S1 med testbrukerens påloggingsdata.

## Åpne spørsmål til gruppa

1. Skal rename være et skjema på S4, eller en egen side? (Punkt 3.)
2. Skal økt-utløp være med i v1? (Punkt 7.)
