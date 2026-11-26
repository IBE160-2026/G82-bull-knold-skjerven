# Story 6.5: Brukertest med medstudenter

## 2026-11-26 kl. 12:55 — MagnusGjerstad

### Oppgave
Forberede 6.5, som er en brukertest med 3–5 medstudenter (SM-6), og deretter pushe 6.4 og 6.5 med PR. Selve testen må gruppa gjøre.

### Plan
- Branch `story-6-5-brukertest-med-medstudenter`, laget fra 6.4-branchen.
- Gjort direkte uten `bmad-build`, fordi leveransen bare er et testopplegg og ingen kode.
- Oppgavene bygger på brukerreisene UJ-1 til UJ-3 i PRD-en. Knappenavnene er sjekket mot malene.

### Resultat
- Commit `412dad5`.
- [brukertest-6-5.md](../../_bmad-output/implementation-artifacts/brukertest-6-5.md) har:
  - en sjekkliste før testen (tom database, testdokumenter, mobil på samme nett, roller og samtykke uten navn);
  - en introduksjon som leses opp;
  - elleve oppgaver uten knappenavn. Oppgave 7 tar et påbegynt forsøk videre på mobil;
  - merknader om testmodus;
  - spørsmål til etterpå;
  - et observasjonsskjema per deltaker;
  - en funntabell med fire nivåer for alvorlighet og en oppsummering for SM-6.
- Sprint-status: `6-5: in-progress`, med en kommentar om at testen gjøres av gruppa.
- PR #16 (6.4) og #17 (6.5) er laget. Deretter er #15, #16 og #17 merget til `main` med fast-forward til `b71386d`. CI på `main` er grønn.

### Åpne punkter
- Gjennomfør brukertesten med 3–5 medstudenter etter `brukertest-6-5.md`. Minst én skal fortsette et påbegynt forsøk på mobil. Fyll ut funnene, og rett dem eller før dem som åpne punkter.
