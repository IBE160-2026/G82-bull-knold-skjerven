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
- source_spec: `_bmad-output/implementation-artifacts/spec-2-3-laste-opp-notat.md`
  summary: Nytt emne (S16) med valgfrie filer (UX-DR34): opprett emnet og last opp hver fil med `last_opp` og samme regler som S6. Feiler én fil, opprettes ikke emnet, og ingen filer blir liggende.
  evidence: Skilt ut fra story 2.3 etter brukerens valg 25.11, slik at 2.3 blir mindre. Det kan leveres for seg, og det gjenbruker `valider_fil` og `last_opp` fra 2.3.
- source_spec: `_bmad-output/implementation-artifacts/spec-2-3-laste-opp-notat.md`
  summary: Opplastingsflyten i `static/js/opplasting.js` har ingen automatisk test. Det gjelder sjekken i nettleseren, valget mellom omdirigering og utbytting, fremdriften og S6c.
  evidence: Repoet har ikke noe testoppsett for JavaScript. Flyten ble prøvd manuelt i headless Edge i story 2.3. En Playwright-test eller lignende hører hjemme i en egen oppgave (for eksempel sammen med axe-testen i Epic 6).
