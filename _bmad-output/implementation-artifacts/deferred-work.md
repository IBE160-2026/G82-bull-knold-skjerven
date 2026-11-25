# Utsatt arbeid

- source_spec: `_bmad-output/implementation-artifacts/spec-1-1-prosjektskjelett-med-datamodell-og-ci.md`
  summary: Ingen test eller CI-steg sjekker at testmodus tvinges på i arbeidsprosessene når testene kjøres med `--parallel`.
  evidence: Django 5.2 kaller `process_setup` bare med spawn (standard på Windows). CI kjører testene serielt, så fjernes `TestmodusParallelSuite.process_setup`, blir CI fortsatt grønn. Et parallelt CI-steg krever eksplisitt spawn-oppsett, fordi Python 3.14 på Linux bruker forkserver som standard.

- source_spec: `_bmad-output/implementation-artifacts/spec-1-2-registrere-konto-logge-inn-og-godta-vilkarene.md`
  summary: Personvernerklæringen (S15) lover ting v1 ikke gjør: sletting av brukerkonto, varsel per e-post og at feilmeldinger slettes automatisk etter 30 dager.
  evidence: v1 har ingen kontosletting og ingen e-postutsending, og logging går bare til konsollen. Teksten er Martins fra prototypen og ble tatt inn uendret etter beslutningen 23.11. Martin eller gruppa må bestemme om teksten eller funksjonene skal endres.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-2-registrere-konto-logge-inn-og-godta-vilkarene.md`
  summary: Tre lenker i §4.1 i personvernerklæringen går til forsider (`claude.com`, `anthropic.com`), ikke til dokumentene de nevner (Privacy Center, veiledning om DPA og SCC, Trust Center).
  evidence: Plassholderlenker fra prototypen. De riktige adressene må slås opp og legges inn.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-2-registrere-konto-logge-inn-og-godta-vilkarene.md`
  summary: S1b sier «Ved å gå videre godtar du våre brukervilkår», men det finnes ingen egen vilkårsside, og `vilkar_godtatt` har ingen versjon, så dialogen kan ikke vises på nytt når vilkårene endres.
  evidence: Teksten kommer fra prototypen. Versjonering står ikke i PRD-en, men §9 i personvernerklæringen lover varsel ved vesentlige endringer.

- source_spec: `_bmad-output/implementation-artifacts/spec-1-6-slette-emne.md`
  summary: CSS kan ikke bygges på en maskin uten Tailwind-binæren: `scripts/bygg-css.sh` krever `tailwindcss` i PATH, og `npx @tailwindcss/cli@4.3.5` i repoet feiler med «Can't resolve 'tailwindcss'».
  evidence: I story 1.6 måtte `tailwindcss@4.3.5` og `@tailwindcss/cli@4.3.5` installeres i en midlertidig mappe og kjøres mot en kopi av `input.css`. Skriptet bør få en reserve med npx (eller en `package.json` med låste versjoner), så neste story som endrer CSS, kan bygge med én kommando.
- source_spec: `_bmad-output/implementation-artifacts/spec-1-6-slette-emne.md`
  summary: En opplasting som kjører samtidig som emnet slettes, kan skrive fila til disk før `Notat`-raden feiler, slik at fila blir liggende uten rad.
  evidence: Ikke verifisert, fordi opplasting først kommer i story 2.3. `last_opp` må sørge for at fila slettes hvis raden ikke kan lagres, eller lagre fila etter raden. Sjekkes når 2.3 skrives.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-2-generere-med-modellen-eller-mock-svar.md`
  summary: Når svaret ender med `stop_reason == "max_tokens"`, er det avkuttet og blir `format`. Et nytt forsøk med samme `MAKS_TOKENS = 16000` feiler trolig på samme måte (ikke verifisert, middels).
  evidence: Det er uvisst om 30 spørsmål med begrunnelse og tenking ved `effort: "medium"` får plass i 16000 tokens. Det avgjøres ved første ekte kjøring av `lag_mocksvar`. Ender noen kall med `max_tokens`, øk `MAKS_TOKENS` (under SDK-grensen for kall uten streaming) eller bytt til streaming.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-2-generere-med-modellen-eller-mock-svar.md`
  summary: Når `ki/mock/` committes, må vakten i `EkteMockfilerTest` (`skipTest` når manifestet mangler) fjernes. Det må også komme en test som kaller `generer` mot den ekte, upatchede `MOCK_MAPPE` for hvert testdokument.
  evidence: Utsatt med vilje etter beslutningen «Bygg nå, kjør senere» (25.11). Til da kan testmodus mangle mock-filer uten at CI feiler.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-3-laste-opp-notat.md`
  summary: Nytt emne (S16) med valgfrie filer (UX-DR34): opprett emnet og last opp hver fil med `last_opp` og samme regler som S6. Feiler én fil, opprettes ikke emnet, og ingen filer blir liggende.
  evidence: Skilt ut fra story 2.3 etter brukerens valg 25.11, slik at 2.3 blir mindre. Det kan leveres for seg, og det gjenbruker `valider_fil` og `last_opp` fra 2.3.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-3-laste-opp-notat.md`
  summary: Opplastingsflyten i `static/js/opplasting.js` har ingen automatisk test. Det gjelder sjekken i nettleseren, valget mellom omdirigering og utbytting, fremdriften og S6c.
  evidence: Repoet har ikke noe testoppsett for JavaScript. Flyten ble prøvd manuelt i headless Edge i story 2.3. En Playwright-test eller lignende hører hjemme i en egen oppgave (for eksempel sammen med axe-testen i Epic 6).
- source_spec: `_bmad-output/implementation-artifacts/spec-2-5-feil-timeout-og-prov-igjen.md`
  summary: Feilhåndteringen på S8 i `static/js/fremdrift.js` har ingen automatisk test (melding ved `htmx:responseError`/`htmx:sendError` fra `#spor`, at `#spor` fjernes og at hendelser fra andre elementer ignoreres).
  evidence: Repoet har ikke noe testoppsett for JavaScript. Flyten ble kontrollert manuelt i headless Edge i story 2.5 (500 på `/steg/` ga meldingen, og ingen nye spørringer gikk). Hører sammen med det tilsvarende punktet for `opplasting.js` fra 2.3.
- source_spec: `_bmad-output/implementation-artifacts/spec-3-1-starte-og-svare-pa-en-quiz.md`
  summary: Story 3.3 må håndtere leverte økter i flyten fra 3.1. `steg` for en ferdig jobb kaller alltid `start_eller_fortsett_okt`, så en gammel S8-fane kan lage et nytt påbegynt forsøk etter levering. GET på S9 for en levert økt viser et skjema som kan redigeres. `except OktErLevert` i `sporsmal` har ingen view-test.
  evidence: Review av 3.1 (B3/E1, B7/E4, V3). Kan ikke nås før 3.3 kan levere. Forslag: `steg` sender til S7 når quizen har et levert forsøk og ikke noe påbegynt, S9 (GET og POST) for en levert økt sender til resultatsiden, og en view-test patcher `lagre_svar` til å heve `OktErLevert`.
