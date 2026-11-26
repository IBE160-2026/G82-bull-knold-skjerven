---
title: 'Story 5.3: Historikk per notat'
type: 'feature'
created: '2026-11-26'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
baseline_commit: 'f62315ac2e106c2ce2934ea5ea9c8261c40853d7'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** S7 viser ikke de tidligere forsøkene på notatet, så studenten ser ikke om hen blir bedre (FR-26, UX-DR23).

**Approach:** Legg seksjonen «Historikk» nederst på S7.
- **Utvalg (AD-6):** én spørring på `egne(Okt, bruker)` med `notat=…`, `type=forsok` og `status=levert`, sortert på `-levert_tidspunkt` og `-pk`. Påbegynte forsøk og øvingsøkter vises aldri.
- **Kolonner:**
  - **Dato:** `levert_tidspunkt` i `Europe/Oslo`, som «26. november 2026 kl. 14:05». Klokkeslettet skiller flere forsøk samme dag.
  - **Quiz:** nivå og antall spørsmål i quizen, med samme tekst som overskriften på quizkortet («Middels, 10 spørsmål»), slik at raden kan kobles til kortet.
  - **Poengsum:** «7 av 10», fra `okt.poengsum` og `okt.antall` slik `lever_okt` satte dem.
- **Lenke:** hver rad lenker til `studier:resultat` for forsøket.
  - I tabellen er datoen lenken.
  - På mobil er hele kortet én lenke med datoen, quizen og poengsummen.
- **Visning (NFR-1, NFR-8, UX-DR29):**
  - Under `md`: en liste med ett lite kort per forsøk.
  - Fra `md`: en ekte `<table>` med `<caption>` «Forsøk, nyeste først» og `<th scope="col">` for Dato, Quiz og Poengsum.
  - Begge varianter ligger i HTML-en, og CSS skjuler den ene. Ingen vannrett rulling ved 360 px.
- **Tom tilstand:** uten leverte forsøk står «Ingen forsøk ennå. Ta en quiz for å se historikken.» i stedet for tabellen og listen.
- **Rammer:**
  - Ingen ny modell, migrering eller JavaScript.
  - Dekningskortet, «Øv på feil», quizkortene og skjemaet på S7 endres ikke.
  - Spørringen per side øker ikke med antall forsøk.

</frozen-after-approval>

## Implementation Notes

- **Code map:**
  - `studier/views.py` `notat` (S7): legg historikken i konteksten.
  - `templates/studier/notat.html`: seksjonen nederst, etter «Lag ny quiz».
  - `static/css/app.css`: bygg på nytt hvis `md:hidden` og `md:table` mangler.
  - Ny testfil `studier/tests/test_historikk.py`, med testhjelpere som i `test_levering.py`.
- **Implementert direkte, uten underagent:**
  - `notat`-viewet henter `historikk` i én spørring: `egne(Okt, …)` med `select_related("quiz")`, `Count("quiz__sporsmal")` og `order_by("-levert_tidspunkt", "-pk")`.
  - Malen har seksjonen «Historikk» etter «Lag ny quiz».
    - Under `md`: `<ul class="… md:hidden">` med kort, der hele kortet er én lenke og `sr-only`-komma skiller feltene, som på S4.
    - Fra `md`: `<table class="hidden … md:table">` med `<caption>` og tre `<th scope="col">`.
  - Datoformatet er `j. F Y \k\l. H:i` med `TIME_ZONE = "Europe/Oslo"`.
- **CSS:** `md:hidden` og `md:table` var nye, så `app.css` er bygget på nytt med `scripts/bygg-css.sh` (Tailwind 4.3.5).
- **Overraskelse:** `test_ta_pa_nytt.QuizkortTest.test_knappen_gjelder_hvert_kort_for_seg` talte «Middels, 5 spørsmål» på hele siden, og historikken la til to treff. Testen teller nå bare overskriftene på kortene (`…</h3>`), slik intensjonen var.
- **Tester:** `test_historikk.py` har 8 tester:
  - tom tilstand
  - påbegynt forsøk og øving vises ikke
  - dato i Oslo-tid, quiz, poengsum og lenke i både tabell og kort
  - caption og `th`
  - skilletegn på kortet
  - nyeste først
  - andre quizer på notatet tas med, men ikke forsøk på andre notater
  - samme antall spørringer for 1 og 3 forsøk
- **Status før review:** ruff er rent, `makemigrations --check` er rent og 527 tester er grønne (1 hoppet over).
- **Etter review:**
  - Raden henter quizen fra `quizer`, som alt er hentet til kortene. Dermed er det ingen ekstra join eller `Count` i historikkspørringen, og nivå og antall er garantert de samme som på kortet.
  - Datoen er `<th scope="row">`.
  - To nye tester: radoverskriften, og to forsøk med likt tidspunkt.
  - Tomtilstandstestene sjekker også at kortlisten mangler.
  - CSS er bygget på nytt for `font-normal`.
  - 529 tester er grønne (1 hoppet over).

## Review Triage Log

B = Blind Hunter. Pass 1, 26.11. Funngulv 4 (ca. 11 kB).

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | Quiz-kolonnen teller alle spørsmålene i quizen, mens poengsummen bruker `okt.antall` uten meldte spørsmål | low | Ekte forskjell, men valgt med vilje i frozen intent: samme tekst som quizkortet, slik at raden kan kobles til kortet. Poengsummen er den samme som på S11 | avvist |
| B2 | Quizen hentes to ganger, med `Count` over en join | low | Bekreftet. `quizer` har alt nivå og `antall_sporsmal`. Enkel rettelse som også garanterer lik tekst | patch |
| B3 | Ingen grense eller sidedeling på historikken | low | FR-26 og spec-en sier alle leverte forsøk. En student har sjelden mange forsøk per notat | avvist |
| B4 | Datoen er ingen radoverskrift | low | Bekreftet. `<th scope="row">` gir kontekst for skjermleser i tabellen | patch |
| B5 | Rekkefølgen ved likt tidspunkt er ikke testet | low | Bekreftet. `-pk` kunne fjernes uten at noen test feilet | patch |
| B6 | Tomtilstandstestene sjekker bare tabellen, ikke kortlisten | low | Bekreftet. Én linje per test | patch |
| B7 | Ingen test for andre brukeres leverte forsøk | false | Utvalget er `egne(Okt, bruker)` og `notat=objekt`, og `notat` er hentet med `hent_egen`. En annen brukers økt kan ikke peke på et notat brukeren eier, så testen ville ikke kunne feile | avvist |
| B8 | Datoformatet og quizteksten står to ganger i malen | low | Kosmetisk. To linjer i samme seksjon, og testene sjekker begge variantene | avvist |
| B9 | Rettelsen i `test_ta_pa_nytt` avhenger av markup (`</h3>`) | low | Endres overskriften, feiler testen tydelig. Ingen stille feil | avvist |
