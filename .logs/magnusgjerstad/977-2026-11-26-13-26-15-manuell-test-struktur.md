# Struktur for manuell test

## 2026-11-26 kl. 13:26 — MagnusGjerstad

### Oppgave
Lage en struktur der Magnus, Christian og Martin fører sine egne tilbakemeldinger, funn, feil og forbedringer fra den manuelle testingen. Det skal være én fil per person på et logisk sted.

### Plan
- Ny mappe `_bmad-output/implementation-artifacts/manuell-test/`, ved siden av sjekklistene for manuell test (6.3, 6.4 og 6.5).
- Én fil per person, så de ikke får konflikter i git. En README forklarer formatet og lenker til det som skal testes.

### Resultat
- Commit `5322744` på `main`, ikke pushet.
- [manuell-test/README.md](../../_bmad-output/implementation-artifacts/manuell-test/README.md) har:
  - fordelingen av filer og prefikser for ID (`MAG`, `CHR`, `MAR`);
  - hva som skal testes, med lenker til sjekklistene;
  - typer: feil, forbedring, observasjon og UU;
  - alvorlighet, med samme skala som brukertesten;
  - statusene.
- Filene `test_feedback_magnus.md`, `test_feedback_christian.md` og `test_feedback_martin.md` har hver:
  - en tabell over testøktene;
  - en oversiktstabell;
  - en mal per funn med steg for å gjenskape, forventet og faktisk resultat, forslag og status.

### Åpne punkter
Ingen.
