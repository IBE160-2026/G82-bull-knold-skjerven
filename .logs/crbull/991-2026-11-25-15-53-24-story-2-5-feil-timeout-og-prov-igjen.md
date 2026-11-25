# Story 2.5: feil, timeout og «Prøv igjen»

## 2026-11-25 kl. 15:53 — crbull

### Oppgave
Bygge story 2.5 med bmad-build, direkte på `main`. Når genereringen feiler, skal S8 si hva som gikk galt og hva brukeren kan gjøre, og det skal gå an å prøve igjen uten ny opplasting. Bygger på 2.4 ([logg](992-2026-11-25-15-11-45-story-2-4-lage-quiz-med-fremdrift.md)).

### Plan
- Spec: [spec-2-5-feil-timeout-og-prov-igjen.md](../../_bmad-output/implementation-artifacts/spec-2-5-feil-timeout-og-prov-igjen.md). Godkjent med omtrent 2400 tokens.
- Christian bestemte å ta med nettfeil, serverfeil og utløpt økt på S8 (åpent punkt fra 2.4).
- En subagent implementerte. Tre subagenter gjorde review, og etterpå kom patcher og ny verifisering.

### Resultat
- Commit `37fbd2c` på `main` (ikke pushet).
  - Én feiltekst per kode i `feilmeldinger.py`.
  - «Prøv igjen» er et vanlig skjema mot S7 med samme valg.
  - Tidsfristen sjekkes også når S8 lastes.
  - Sluttfragment når jobben eller notatet er slettet (`hent_egen_eller_none`).
  - `static/js/fremdrift.js` viser en melding ved serverfeil og nettfeil.
  - `HtmxOmdirigeringMiddleware` gir `HX-Redirect` med `next` lik S8 ved utløpt økt.
- Review, pass 1: 19 funn.
  - To intent_gap ble avgjort av Christian, og koden ble beholdt: `next` peker på S8 i stedet for steg-endepunktet (det ga 405), og «Filen er lagret …» vises ikke for `for_lite_innhold` og `for_stor`.
  - Rettet som patch: `#handlinger` tømmes ved serverfeil, og tekst-testen bruker `Feilkode.values`.
  - Utsatt: ingen automatisk test av `fremdrift.js`, ført i `deferred-work.md`. Resten er avvist med begrunnelse i triageloggen.
- Verifisert:
  - ruff, `makemigrations --check` og 306 tester grønne (1 hoppet over).
  - Headless Edge mot en midlertidig server: feiltekst med fokus på «Prøv igjen», ny S8 som ender på S7, melding ved 500, og innlogging med `next=/jobber/<id>/` ved utløpt økt.
- Lukket punktet fra 2.4 om at S8 stoppet stille ved 500, nettfeil og utløpt økt.
- `sprint-status.yaml`: 2.5 står som `review`.

### Åpne punkter
- `fremdrift.js` har ingen automatisk test (står i `deferred-work.md`). Kontrollert manuelt i headless Edge.
