---
title: 'Story 4.2: Levere øvingen og se hva som er lært'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '8b11397002f985253e6d359b6c4d1d1db141dd9e'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** En levert øvingsøkt vises i dag som et vanlig S11. Studenten ser ikke hvilke spørsmål som ble lært, fasiten og begrunnelsen for dem, hvor langt de andre har kommet, eller at feilbanken er tom (FR-23, UX-DR21, UX-DR22, TF-2).

**Approach:** Gjenbruk `resultat`-viewet og `resultat.html` med `er_oving`. For øving: terrakotta-omslaget `ovemodus`, en seksjon øverst med spørsmålene som ble lært i økten, lært-prikker og teller på radene som ikke er lært, og meldingen når feilbanken er tom. Leveringen (`lever_okt`, S10) endres ikke.

## Boundaries & Constraints

**Always:**
- **Lært i økten** = `Svar.hendelse == laert` **og** `fasit_synlig(sporsmal)` nå (AD-18, AD-20). Er spørsmålet nullstilt senere, står det som en vanlig rad med teller og uten fasit.
- **S12-resultat**, bare når `okt.type == oving`. Rekkefølgen på siden:
  1. h1 «Øv på feil».
  2. «4 av 5 riktige» med `role="status"`, som på S11.
  3. «N spørsmål er lært.» når N > 0.
  4. h2 «Lært», med ett element per lært spørsmål: spørsmålsteksten, «Lært. Riktig svar var: <alternativ>» og «Begrunnelse: <tekst>», med `lang` fra quizen.
  5. h2 «Svar» med radene som på S11 (✓/✕, «Riktig»/«Feil», ikonet `aria-hidden`).
- **Radene:**
  - En lært rad viser «Lært» i stedet for teller. Fasiten gjentas ikke i raden, fordi den står over.
  - En rad som ikke er lært, viser to prikker (`aria-hidden`) og teksten «K av 2 riktige på rad». K er `Feilbankrad.riktige_pa_rad` nå, og 2 er `RIKTIGE_FOR_LAERT`. Fylte prikker = K.
- **Tom feilbank:** når `apne_rader(notat)` er tom, står «Alle spørsmålene er lært. Feilbanken er tom.» og lenken «Tilbake til notatet». Ingen feiring, utropstegn, lyd eller animasjon.
- **Side og navigasjon:**
  - Tittel «Øv på feil – Resultat – <notat>», og brødsmulen «Øv på feil – Resultat».
  - Innholdet ligger i `<div class="ovemodus">`.
  - «Øv på feil (N)»/«Fortsett» og «Tilbake til notatet» står som i dag.
- **Forsøk (S11)** er uendret: h1, tittel, fasit inne i raden for lærte spørsmål og «lagt i feilbanken».
- Ingen `er_riktig` eller begrunnelse for spørsmål som ikke er lært, i konteksten eller i HTML-en.
- Andres økt gir 404. Ingen JavaScript.

**Never:**
- Ikke endre `lever_okt`, `registrer_svar`, `lagre_svar`, modellene eller migreringene.
- Ikke melde som feil (4.3). Ikke historikk eller dekningsgrad (Epic 5).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Noen lært | 3 åpne rader med K = 1, 1, 0, alle svart riktig | «3 av 3 riktige», «2 spørsmål er lært.», to i «Lært» med fasit og begrunnelse, den tredje «1 av 2 riktige på rad» | N/A |
| Feil svar | åpen rad med K = 1, svart feil | ✕ «Feil», «0 av 2 riktige på rad», ingen fasit | N/A |
| Alt lært | alle åpne rader blir lært | «Alle spørsmålene er lært. Feilbanken er tom.» og lenke til S7, ingen øvingsknapp | N/A |
| Ubesvarte | øving med 1 av 3 besvart, Lever | samme melding med lenker som i 3.3, ingenting registreres | `UbesvarteSporsmal` |
| Lært, så feil | lært i øving, senere feil i forsøk | raden nullstilt, i feilbanken igjen. Øvingsresultatet viser ingen fasit og «0 av 2 riktige på rad» | N/A |
| Forsøk | levert forsøk | S11 uendret, ingen `ovemodus` og ingen «Lært»-seksjon | N/A |
| Tilgang | annens øvingsøkt | 404 | N/A |

</frozen-after-approval>

## Code Map

- `studier/views.py:558` `resultat` -- utvides. Svarene hentes allerede med `select_related`. Hent `Feilbankrad` for alle spørsmålene i økten i én spørring (`{sporsmal_id: rad}`), og bygg `laerte` og `teller` per rad bare for øving. `fasit_synlig` brukes uendret for fasiten. Send `er_oving`, `laerte`, `antall_laert` og `feilbank_tom` (`not apne_rader(notat).exists()`, bare for øving). `_emne_kontekst(notat.emne, siste, notat=notat)` gir brødsmulene.
- `templates/studier/resultat.html` -- omslaget, h1/tittel, «Lært»-seksjonen, telleren i radene og tom-meldingen. Forsøksgrenen skal gi samme HTML som før.
- `studier/services/feilbank.py` -- `RIKTIGE_FOR_LAERT` og `apne_rader` importeres. Ingen endring, med mindre en lesehjelper for radene trengs.
- `templates/studier/sporsmal.html:17`, `lever.html:15` -- mønsteret for `ovemodus` og `er_oving` (4.1).
- `static/css/input.css` -- prikkene bruker Tailwind-klasser: `inline-block`, `w-3 h-3`, `rounded-full`, `border-2 border-accent-strong` og `bg-accent-strong` for fylt. `h-3` og `rounded-full` mangler i `app.css`, så bygg den på nytt med `npx --yes @tailwindcss/cli@4.3.5 -i static/css/input.css -o static/css/app.css --minify`, og fjern `node_modules` etterpå.
- Tester: `studier/tests/test_oving.py` har `OvingTestCase` med `_rader`, `_start` og `_svar_alle`. Lag en ny `studier/tests/test_oving_resultat.py` som arver den.

## Tasks & Acceptance

**Execution:**
- [x] `studier/views.py` -- `resultat` med øvingskontekst, som over.
- [x] `templates/studier/resultat.html` -- S12-grenen.
- [x] `static/css/app.css` -- bygd på nytt hvis nye klasser trengs.
- [x] `studier/tests/test_oving_resultat.py` -- én test per rad i matrisen. I tillegg:
  - S12 har ikke fasit eller begrunnelse for spørsmål som ikke er lært.
  - `ovemodus` vises bare for øving.
  - En spørringsgrense med `assertNumQueries`, så antallet ikke vokser med antall spørsmål utover dagens `fasit_synlig`.

**Acceptance Criteria:**
- Gitt en levert øvingsøkt der ett spørsmål ble lært, når S12 vises, så står spørsmålet under «Lært» med «Lært. Riktig svar var: …» og begrunnelsen. Den riktige alternativteksten for de andre spørsmålene står ikke på siden.
- Gitt et levert forsøk, når S11 vises, så er HTML-en den samme som før denne storyen: eksisterende tester i `test_levering.py` og `test_ta_pa_nytt.py` er grønne uten endringer.

## Implementation Notes

- **Implementert av en underagent.** Review med tre reviewere på Opus.
- **Feilbankrader:** `resultat` henter `riktige_pa_rad` for alle spørsmålene i én spørring, bare for øving. Fasiten avgjøres fortsatt av `fasit_synlig` (AD-20).
- **`feilbank_tom`** gjenbruker `ov["n"]` fra `_ov_knapp`, som er det samme som `apne_rader(notat).count()`. Det sparer én spørring.
- **Spørsmål som er lært utenfor økten** (lært nå, men `hendelse` er ikke `laert`): raden viser «Lært» og fasiten i raden, som S11. Spørsmålet står ikke under «Lært» og telles ikke i «N spørsmål er lært.».
- **Malen:** øvingsgrenene står inne i de eksisterende taggene, så et forsøk gir byte-lik HTML som før. Det er kontrollert ved å lagre S11 før og etter og sammenligne, og bare CSRF-tokenet var ulikt.
- **CSS:** `app.css` er bygd på nytt med Tailwind 4.3.5. Bare `.h-3`, `.w-3` og `.rounded-full` kom til. `npx --yes` alene fant ikke `tailwindcss`, så pakkene ble installert midlertidig med `--no-save`, og `node_modules` ble fjernet etterpå.

## Spec Change Log

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 25.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| V1 | Ingen test for en rad som er lært nå, men der `hendelse` ikke er `laert` | medium | Bekreftet (filed gap). Begge mutasjonene i funnet passerer i dag | patch (med B2, E3) |
| V2 | Bare fylte prikker telles, så de tomme kan forsvinne uten at en test feiler | medium | Bekreftet (filed gap) | patch |
| V3 | `er_oving`-vakten på `feilbank_tom` er ikke testet for forsøk med tom feilbank | medium | Bekreftet (filed gap). `test_forsok_uendret` har en åpen rad | patch (med B6) |
| B1 | Spørringstesten dekker ikke lærte rader. Bruk `laert_tidspunkt` fra samme spørring i stedet for `fasit_synlig` | low | `alternativer.get` per lært rad finnes fra før på S11. Arkitekturen sier `fasit_synlig` for fasiten | avvist |
| B2 | En rad kan vise både «Lært» og fasiten i raden | low | Bekreftet for spørsmål som er lært utenfor økten. Det er S11-oppførselen, og AD-20 tillater det. Nå festet med en test | patch (med V1) |
| B3 | «Feilbanken er tom» kan stå ved siden av «Fortsett» | low | Krever en ny påbegynt øving som så tømmes av et forsøk. Meldingen er fortsatt sann, og spec-en knytter den til `apne_rader` | avvist |
| B4 | Testhjelperne slår bare opp i `self.quiz`, og `_levert_oving` har tom standard for `k` | low | Bekreftet: virker bare på grunn av fixturens størrelse. Direkte rettelse | patch (med E5) |
| B5 | Flere sjekker i `test_ingen_fasit_for_ikke_laerte` kan aldri feile | medium | Bekreftet: nøklene finnes aldri på toppnivå eller i raden | patch |
| B6 | Ingen direkte sjekk av at S11 er uendret | low | Eksisterende tester i `test_levering.py` og `test_ta_pa_nytt.py` er grønne uten endringer, og HTML-en er sammenlignet manuelt. Vakten for tom feilbank er dekket av V3 | patch (med V3) |
| B7 | Gamle øvingsresultater blander økten med tilstanden nå | false | Spec-en sier at telleren og tom-meldingen leses nå («nå»). Det er valgt med vilje, ikke en feil | avvist |
| B8 | Punktene under «Lært» har ikke nummer og kan ikke knyttes til raden | low | Bekreftet. Direkte rettelse: `nr` i hvert punkt | patch |
| E1 | `feilbank_tom` når en annen øving er påbegynt | low | Samme som B3 | avvist |
| E2 | Gammel øving med bare feil svar viser «Alle spørsmålene er lært» | false | Samme som B7: meldingen gjelder feilbanken nå, slik spec-en sier | avvist |
| E3 | Lært utenfor økten blir ikke telt i «N spørsmål er lært.» | low | Samme som V1. Spec-en definerer «lært i økten» som `hendelse=laert` og lært nå | patch (med V1) |
| E4 | `lever_okt` kan kjøre mellom spørringen for telleren og `fasit_synlig` | low | Økten er alt levert når resultatet vises. Bare et samtidig forsøk på et annet notat kan endre radene i det korte vinduet | avvist |
| E5 | `_levert_oving` med standardverdien `k=()` gir `AttributeError` | low | Samme som B4 | patch (med B4) |
| E6 | Spørringsgrensen dekker ikke lærte rader | low | Samme som B1 | avvist |
| E7 | Den riktige alternativteksten står på siden for spørsmål som ikke er lært, men svart riktig | false | Det er studentens eget svar («Ditt svar»), som på S11 (FR-19). Fasiten vises ikke for spørsmål som ikke er lært | avvist |

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne

**Manual checks:**
- S12-resultatet ved 360 px: ingen vannrett rulling, prikkene og knappene er terrakotta, og teksten «K av 2 riktige på rad» står ved hver rad som ikke er lært.
