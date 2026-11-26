# Manuell test

Her fører hver i gruppa sine egne funn fra den manuelle testingen: feil, forbedringer, observasjoner og tilbakemeldinger. Én fil per person, så dere ikke får konflikter i git.

| Person | Fil | Prefiks for ID |
|---|---|---|
| Magnus Gjerstad | [test_feedback_magnus.md](test_feedback_magnus.md) | `MAG` |
| Christian R Bull | [test_feedback_christian.md](test_feedback_christian.md) | `CHR` |
| Martin Skjerven | [test_feedback_martin.md](test_feedback_martin.md) | `MAR` |

## Hva skal testes

Sjekklistene for det som skal testes, ligger i mappen over:

- [sluttkontroll-6-3.md](../sluttkontroll-6-3.md), del 4: tastatur og skjermleser (NVDA eller VoiceOver), 320 px og 200 % tekst.
- [brukertest-6-5.md](../brukertest-6-5.md): brukertest med 3–5 medstudenter. Funnene derfra samles i funntabellen i den fila.
- [ki-kvalitet-6-4.md](../ki-kvalitet-6-4.md): vurdering av spørsmålene fra ekte modell. Krever API-nøkkelen.
- Test med ny klone (6.2): følg README-en i prosjektroten ordrett på en maskin uten `.env`.
- Kjerneflyten som testbrukeren (`sensor@farequiz.no` / `sensor123` etter `seed_testdata`): S3, S4 og S7 med data, quiz, levering, «Øv på feil», dekningsgrad og historikk.

## Slik fører du et funn

1. Legg til en linje i «Oversikt» øverst i fila di, med neste ledige ID (`MAG-01`, `MAG-02` …).
2. Skriv funnet nederst etter malen i fila. Ett funn per problem.
3. Når noen retter funnet, settes status til «rettet» med commit-hashen. Funn som ikke skal rettes, får status «avvist» eller «åpent punkt» med begrunnelse.

**Type:**
- **Feil:** noe virker ikke som det skal.
- **Forbedring:** noe virker, men kan bli bedre.
- **Observasjon:** noe du la merke til, uten at det nødvendigvis må endres.
- **UU:** brudd på universell utforming.

**Alvorlighet** (samme skala som i brukertesten):
- **Kritisk:** man kommer ikke videre eller mister data. Rettes før levering.
- **Alvorlig:** man kommer videre, men med stor nøling eller feil forståelse. Bør rettes.
- **Mindre:** kort nøling eller en kommentar. Rettes hvis det er enkelt.
- **Kosmetisk:** ordvalg eller utseende.

Skjermbildene heter S1–S16, S1b, S6b og S6c, som i [EXPERIENCE.md](../../planning-artifacts/ux-designs/ux-G82-bull-knold-skjerven-2026-11-11/EXPERIENCE.md).

Funn som ikke rettes før levering, føres også i `.logs/<bruker>/issues.md`.
