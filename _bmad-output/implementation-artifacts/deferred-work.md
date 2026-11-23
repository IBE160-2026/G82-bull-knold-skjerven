# Utsatt arbeid

- source_spec: `_bmad-output/implementation-artifacts/spec-1-1-prosjektskjelett-med-datamodell-og-ci.md`
  summary: Ingen test eller CI-steg sjekker at testmodus tvinges på i arbeidsprosessene når testene kjøres med `--parallel`.
  evidence: Django 5.2 kaller `process_setup` bare med spawn (standard på Windows). CI kjører testene serielt, så fjernes `TestmodusParallelSuite.process_setup`, blir CI fortsatt grønn. Et parallelt CI-steg krever eksplisitt spawn-oppsett, fordi Python 3.14 på Linux bruker forkserver som standard.
