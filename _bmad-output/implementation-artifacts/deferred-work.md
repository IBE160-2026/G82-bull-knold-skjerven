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

