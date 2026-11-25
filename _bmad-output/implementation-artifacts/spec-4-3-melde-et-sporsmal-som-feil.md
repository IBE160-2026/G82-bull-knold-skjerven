---
title: 'Story 4.3: Melde et spørsmål som feil'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '18d036ff356eaddbed4b6416f53cefe4fa3d4d45'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/sprint-change-proposal-2026-11-25-fr31.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Har KI-en laget feil fasit, sitter studenten fast. Riktig svar legger spørsmålet i feilbanken, og eneste vei ut er å velge det gale svaret to ganger (FR-31, faglærers tilbakemelding § 4.1).

**Approach:** Et spørsmål kan meldes fra en ✕-rad på S11 eller S12, etter en bekreftelse på egen side. Et meldt spørsmål er ute av feilbanken, dekningsgraden og nye økter. Regelen følger B1–B8 i endringsforslaget, som gruppa godkjente 25.11.

## Boundaries & Constraints

**Always:**
- **Én kilde:**
  - `SporsmalQuerySet.ikke_meldt()` (`meldt_tidspunkt IS NULL`), tilgjengelig som `Sporsmal.objects.ikke_meldt()` og på `quiz.sporsmal`. Andre modeller filtrerer med `sporsmal__in=Sporsmal.objects.ikke_meldt()`.
  - Ingen annen kode sjekker `meldt_tidspunkt` direkte, bortsett fra vakten i `registrer_svar` og visningen av raden.
- **Melde:** `studier/services/sporsmal.py` `meld_sporsmal(sporsmal) -> bool` setter `meldt_tidspunkt` med en betinget oppdatering (bare når feltet er tomt), og gir `True` hvis dette kallet meldte. Logger spørsmål-ID, quiz-ID og modell. Ingen angre. Eneste sted som skriver feltet.
- **Feilbanken:**
  - `apne_rader` utelater meldte spørsmål, og «Øv på feil (N)» teller dem derfor ikke.
  - `registrer_svar` gir `ingen` for et meldt spørsmål og endrer ikke raden. `Feilbankrad` slettes aldri.
- **Nye økter:**
  - `_lag_innhold` og `_lag_oving_innhold` utelater meldte spørsmål.
  - En quiz uten spørsmål som ikke er meldt, og uten påbegynt forsøk, gir `None` fra `start_eller_fortsett_okt`, og ingen økt lages. `start_quiz` sender da til S7.
  - En påbegynt økt er uendret (AD-16): spørsmålet vises og må besvares, og poengsummen telles som før.
- **Dekningsgraden:** `services.dekningsgrad.for_notat` teller bare spørsmål som ikke er meldt. Et nivå der alle spørsmålene er meldt, er `None` («Ingen quiz»).
- **S7-kortet:** en quiz uten spørsmål som ikke er meldt, og uten påbegynt forsøk, får en låst knapp (`aria-disabled="true"`) med `aria-describedby` til teksten «Alle spørsmålene er meldt som feil». Det er fortsatt et POST-skjema, som i 4.1.
- **S11 og S12:**
  - En rad med ✕ «Feil» der spørsmålet ikke er meldt, får lenken «Meld som feil eller uklart» til `GET /okter/<id>/meld/<nr>/` (`studier:meld`), med `aria-describedby` til spørsmålet.
  - En rad med et meldt spørsmål viser «Meldt som feil» i stedet for lenken, og på S12 i stedet for prikkene og telleren.
  - Fasiten vises ikke på grunn av meldingen.
- **Bekreftelsessiden (`studier/meld.html`):**
  - h1 «Melde spørsmålet som feil eller uklart?», spørsmålsteksten med `lang` og teksten «Spørsmålet tas ut av feilbanken og dekningsgraden og kommer ikke med i nye quizer eller øvinger. Det kan ikke angres.».
  - «Avbryt» (lenke til resultatet) kommer før knappen «Meld som feil» (POST, samme URL).
  - POST melder og sender til resultatet (POST/redirect/GET).
  - Tittel «Meld som feil – <notat>», og brødsmulene Oversikt › emne › notat › «Meld som feil».
- **Tilgang og gyldighet:** `hent_egen(Okt, pk, …)`. Økten må være levert, `nr` må finnes i `innhold`, og svaret på spørsmålet må være feil. Ellers 404, og ingenting endres. Gjelder både GET og POST. Er spørsmålet alt meldt, sender GET og POST til resultatet.
- Ingen migrering. Ingen JavaScript.

**Never:**
- Ikke angre, fritekst eller melding fra S9/S10. Ikke vise fasiten for meldte spørsmål.
- Ikke endre `lever_okt`, `lagre_svar`, `Okt.innhold` i eksisterende økter eller modellfeltene.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Melde | levert forsøk, rad 2 ✕, åpen rad | `meldt_tidspunkt` satt, redirect S11, rad 2 «Meldt som feil», «Øv på feil (N−1)» | N/A |
| Allerede meldt | meldt spørsmål, POST igjen | tidspunktet uendret, redirect S11 | N/A |
| Riktig rad | rad med ✓ | 404, ingenting endres | N/A |
| Påbegynt økt | GET/POST mot påbegynt økt | 404 | N/A |
| Ugyldig nr | nr 0 eller over antall | 404 | N/A |
| Andres økt | annen brukers økt | 404, ingenting endres | N/A |
| Ny øving | 3 åpne rader, 1 meldt | ny øving med 2 spørsmål | N/A |
| Nytt forsøk | quiz med 5, 1 meldt | nytt forsøk med 4 | N/A |
| Alle meldt | quiz med alle meldt, ingen påbegynt | S7 låst med teksten; POST start lager ingen økt, redirect S7 | N/A |
| Påbegynt med meldt | påbegynt forsøk, spørsmål meldes, så levering | spørsmålet besvares, hendelse `ingen`, raden uendret, poengsum som før | N/A |
| Dekningsgrad | meldt spørsmål, de andre dekket | andelen 1,0 på nivået | N/A |
| Nivå alle meldt | alle spørsmål på lett meldt | lett `None` | N/A |

</frozen-after-approval>

## Code Map

- `studier/models.py:157` `Sporsmal` -- legg til `SporsmalQuerySet` med `ikke_meldt()` og `objects = SporsmalQuerySet.as_manager()`. Uten `use_in_migrations`, så `makemigrations --check` er uendret.
- `studier/services/sporsmal.py` (ny) -- `meld_sporsmal`. Samme mønster som `studier/services/vilkar.py`: `filter(pk=…, meldt_tidspunkt__isnull=True).update(…)`, og oppdater objektet.
- `studier/services/feilbank.py` -- `registrer_svar`: vakt øverst, før låsen. `apne_rader`: `sporsmal__in=Sporsmal.objects.ikke_meldt()`.
- `studier/services/okter.py:43,59,74` -- `_lag_innhold` (`quiz.sporsmal.ikke_meldt()`), `_lag_oving_innhold` (via `apne_rader`, som alt filtrerer). `start_eller_fortsett_okt`: tomt innhold gir `None` også for quiz. Docstringen oppdateres.
- `studier/services/dekningsgrad.py` (fra story 5.1) -- start utvalget med `Sporsmal.objects.ikke_meldt()`, og la et nivå uten spørsmål som ikke er meldt, telle som uten quiz. Fjern merknaden i docstringen om at 4.3 gjenstår.
- `studier/views.py` -- `start_quiz:403` håndterer `None`. `jobb`/`steg:397` lager alltid en ny quiz uten meldte spørsmål og trenger ingen endring. `notat:242` annoterer `antall_ikke_meldt=Count("sporsmal", filter=Q(sporsmal__meldt_tidspunkt__isnull=True))` eller tilsvarende via `ikke_meldt`. `resultat` legger `meldt` på hver rad, og den nye `meld`-viewet (`@require_http_methods(["GET", "HEAD", "POST"])`) bruker `_emne_kontekst(notat.emne, "Meld som feil", notat=notat)`.
- `studier/urls.py` -- `okter/<int:pk>/meld/<int:nr>/`, `name="meld"`.
- `templates/studier/notat.html`, `resultat.html` og ny `meld.html` -- etter mønsteret i `slett_emne.html` (Avbryt først). Bruk bare klasser som finnes i `app.css`, ellers bygg den på nytt som i spec 5.1.
- Tester: ny `studier/tests/test_melde.py` med `OvingTestCase` fra `test_oving.py` og `_annen_bruker` fra `test_okter.py`. Eksisterende tester for 3.x, 4.x og 5.1 skal være grønne uten endringer.

## Tasks & Acceptance

**Execution:**
- [x] `studier/models.py`, `studier/services/sporsmal.py` -- `ikke_meldt` og `meld_sporsmal`.
- [x] `studier/services/feilbank.py`, `studier/services/okter.py`, `studier/services/dekningsgrad.py` -- filteret alle steder og vakten i `registrer_svar`.
- [x] `studier/urls.py`, `studier/views.py` -- `meld`, `start_quiz`, kontekst for S7 og S11/S12.
- [x] `templates/studier/meld.html`, `resultat.html`, `notat.html` -- lenken, «Meldt som feil», bekreftelsen og den låste knappen.
- [x] `studier/tests/test_melde.py` -- én test per rad i matrisen. I tillegg:
  - en test som sjekker at fasiten ikke står på S11 etter melding;
  - en grep-test som sjekker at `meldt_tidspunkt` bare brukes i `models.py`, `services/sporsmal.py`, `services/feilbank.py` (vakten) og visningskoden for raden.

**Acceptance Criteria:**
- Gitt et meldt spørsmål, når S7 vises, så er «Øv på feil (N)» og dekningsgraden regnet uten spørsmålet.
- Gitt bekreftelsessiden, når den vises, så kommer «Avbryt» før «Meld som feil» i tab-rekkefølgen, og teksten sier at meldingen ikke kan angres.

## Implementation Notes

- **Implementert av en underagent.** Review med tre reviewere på Opus.
- **S7-kortet:** `har_ikke_meldt` er en `Exists` over `ikke_meldt()` i stedet for tellingen `antall_ikke_meldt` som Code Map foreslo. Låsen trenger bare ja/nei. Antallet på kortet («5 spørsmål») teller fortsatt alle spørsmålene i quizen.
- **Valg spec-en ikke avgjorde:**
  - En rad på S12 som er både meldt og lært, viser «Meldt som feil» i stedet for «Lært».
  - `id="sporsmal-N"` settes bare på rader med lenken, så eksisterende tester for ✓-rader er uendret.
  - «Ta på nytt» på S11 er ikke låst når alle spørsmålene er meldt. POST sender til S7, der kortet er låst med forklaringen.
- **Grep-tester:** `meldt_tidspunkt` står bare i `models.py`, `services/sporsmal.py`, `services/feilbank.py` (vakten) og én gang i `views.py` (raden).
- **Etter review:** fasiten skjules for meldte spørsmål også når de var lært før, «Alle spørsmålene er lært» på S12 krever at notatet ikke har noen rader som ikke er lært (meldte medregnet), og `steg` sender til S7 når start gir `None`.
- **Verifisert:** ruff, `makemigrations --check` og 503 tester grønne, 1 hoppet over. Ikke kjørt i nettleser.

## Spec Change Log

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 25.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | Fasiten vises for et meldt spørsmål som var lært før det ble meldt | medium | Bekreftet: `fasit_synlig` ser ikke på meldingen. Bryter «Ikke vise fasiten for meldte spørsmål» | patch |
| V-a | S12 sier «Alle spørsmålene er lært» når det siste åpne spørsmålet ble meldt | medium | Bekreftet: `apne_rader` utelater meldte, så `feilbank_tom` blir sann. Teksten vises nå bare når notatet ikke har noen rader som ikke er lært | patch |
| E2 | `steg` bruker `okt.pk` når start kan gi `None` | low | Kan bare nås hvis invariantene brytes, men gir 500. Direkte vakt på to linjer | patch |
| V1 | Den låste S7-knappen er ikke testet med et påbegynt forsøk | medium | Bekreftet (filed gap) | patch |
| B7 | `test_ta_bare_get_head_og_post` sjekker bare PUT | low | Bekreftet. Direkte tilføyelse: HEAD gir 200 | patch |
| B8 | `aria-disabled` sjekkes mot hele S7 | low | Bekreftet. Begrens til skjemaet for «Øv på feil» | patch |
| V-b | «Ta på nytt» på S11 er ikke låst når alle er meldt | low | Spec-en låser bare S7. POST sender til S7, der forklaringen står. Sjeldent (alle spørsmål i quizen meldt) | avvist |
| E3 | Samme som V-b | low | Samme som V-b | avvist |
| B2 | Samme som V-b | low | Samme som V-b | avvist |
| E4 | Kortet på S7 teller meldte spørsmål | low | Quizen har fortsatt like mange spørsmål. Meldingen vises på radene og i låsen | avvist |
| B3 | Samme som E4, og avviket fra Code Map er ikke notert | low | Samme som E4. Avviket står nå i Implementation Notes | avvist |
| E1 | `registrer_svar` leser meldingen før låsen | low | SQLite kjører skrivinger én om gangen, og vinduet er millisekunder mellom innlasting og oppdatering | avvist |
| B4 | Samme som E1 | low | Samme som E1 | avvist |
| E5 | `refresh_from_db` gir `DoesNotExist` hvis emnet slettes samtidig | low | Krever sletting av emnet i samme øyeblikk som meldingen | avvist |
| B5 | Grep-testen teller kommentarer og tvinger frem en ekstra spørring | low | Testen holder regelen om én kilde. Én ekstra spørring på en bekreftelsesside | avvist |
| B6 | Regex for skriving fanger ikke `setattr`, `bulk_update` osv. | low | Testen er et sikkerhetsnett. Koden bruker ingen av dem | avvist |
| B9 | Flyttall sammenlignes eksakt | low | Fast summeringsrekkefølge, som i 5.1 | avvist |
| B10 | Delspørringen `ikke_meldt()` er ikke avgrenset til brukeren | low | Ytre filter avgrenser til notatet, og `set()` fjerner dubletter. Resultatet er riktig | avvist |
| B11 | Logglinjen mangler økt og bruker, og kan gi en ekstra spørring | low | Spørsmål, quiz og modell er nok for 6.4. Én spørring per melding | avvist |
| B12 | «feil eller uklart» i lenken, men «feil» i knapp og status | low | Ordlyden er godkjent i endringsforslaget (B1–B8) | avvist |

## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne

**Manual checks:**
- S11 og bekreftelsessiden ved 360 px og med bare tastatur: lenken nås og leses med spørsmålet, og «Avbryt» kommer først.
