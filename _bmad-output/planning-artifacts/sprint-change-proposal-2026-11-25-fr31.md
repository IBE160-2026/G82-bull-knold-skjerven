---
title: 'Endringsforslag: FR-31 melde et spørsmål som feil'
status: 'godkjent'
created: '2026-11-25'
author: 'Magnus (med Claude)'
gjelder: 'PRD, ARCHITECTURE-SPINE (AD-2, AD-3, AD-4, AD-16) og story 4.3'
---

# Endringsforslag: FR-31 melde et spørsmål som feil

## 1. Hvorfor

Faglæreren påpekte i [tilbakemelding-prd.md](prds/prd-G82-bull-knold-skjerven-2026-11-11/tilbakemelding-prd.md) (§ 4.1) at en student kan sitte fast med et spørsmål der KI-en har laget feil fasit:

- Svarer studenten riktig, havner spørsmålet i feilbanken.
- Eneste vei ut er da å velge det gale svaret to ganger på rad.
- Fasiten vises aldri, så studenten kan ikke se hvorfor.

Story 4.3 skal løse dette. Den kan ikke startes før FR-31 står i PRD-en og regelen står i arkitekturen. Per 25.11 står den ingen av stedene.

Forslaget under bygger på faglærerens tekst og på akseptansekriteriene i story 4.3. Gruppa trenger bare å godkjenne beslutningene i kapittel 2 eller endre dem. Teksten i kapittel 3 og 4 kan da limes inn som den er.

## 2. Beslutninger gruppa må ta

Anbefalingen står først i hvert punkt.

| # | Spørsmål | Anbefaling | Alternativ |
|---|----------|------------|------------|
| B1 | Hvor kan et spørsmål meldes? | På resultatrader med ✕ «Feil» på S11 og S12. Det er tilfellet faglæreren beskriver. | Også på rader med ✓ «Riktig», for uklare spørsmål studenten gjettet riktig på. |
| B2 | Hva skjer med feilbanken? | Spørsmålet regnes ikke som i feilbanken, og «Øv på feil (N)» teller det ikke. `Feilbankrad` beholdes (AD-3). | Slette raden. Det bryter AD-3. |
| B3 | Hva skjer med dekningsgraden? | Spørsmålet telles verken i telleren eller nevneren. Et nivå der alle spørsmålene er meldt, teller som et nivå uten quiz (0 %, «Ingen quiz»). | Nivået viser 0 % med egen tekst, for eksempel «Alle spørsmålene er meldt». |
| B4 | Nye økter? | Spørsmålet kommer ikke med i `Okt.innhold` for nye forsøk eller øvingsøkter. En quiz der alle spørsmålene er meldt, kan ikke startes: knappen er låst med teksten «Alle spørsmålene er meldt som feil». | Tillate en tom økt. Det gir en side uten spørsmål. |
| B5 | Påbegynte økter der spørsmålet alt står? | Innholdet er låst (AD-16), så spørsmålet vises og må besvares som før. Ved levering gir `registrer_svar` `ingen` for et meldt spørsmål. Poengsummen telles som før. | Ta spørsmålet ut av poengsummen. Da må `lever_okt` og resultatsidene endres. |
| B6 | Vises fasiten etter melding? | Nei. Et meldt spørsmål er ikke lært (FR-23). | Vise fasiten og begrunnelsen, så studenten ser hva KI-en mente. Faglæreren nevner en begrunnelse, men knytter den til lærte spørsmål. |
| B7 | Kan meldingen angres? | Nei, ikke i v1. Bekreftelsessiden sier det. | En «Angre»-knapp. Det gir en ny URL, nye tester og en ny tilstand i dekningsgraden. |
| B8 | Hva lagres? | `Sporsmal.meldt_tidspunkt`. Feltet finnes fra story 1.1, så ingen migrering trengs. I tillegg en logglinje med spørsmål-ID, quiz-ID og modell, så gruppa kan bruke meldingene i 6.4 (KI-kvalitet). Ingen fritekst. | Et fritekstfelt for hva som er feil. Det krever en ny modell eller et nytt felt og en migrering. |

Meldingen gjelder bare brukerens eget spørsmål, fordi et `Sporsmal` hører til én quiz hos én bruker (AD-5). Andre brukere påvirkes ikke.

## 3. Tekst til PRD-en

Settes inn i § 4.6 etter FR-23:

> #### FR-31: Melde et spørsmål som feil eller uklart
> En bruker kan melde et spørsmål som feil eller uklart fra resultatet av et forsøk eller en øvingsøkt. Meldingen lagres med tidspunkt og kan ikke angres. Realiserer UJ-2.
> - Et meldt spørsmål er ikke i feilbanken og kommer ikke med i nye forsøk eller øvingsøkter.
> - Et meldt spørsmål telles ikke i dekningsgraden, verken som dekket eller i nevneren.
> - Fasiten vises fortsatt ikke.
> - Står spørsmålet i en påbegynt økt, vises det der som før, men svaret påvirker ikke feilbanken.

I tillegg:

- Prioritetstabellen: FR-31 står som «kan kuttes», som story 4.3.
- § 4.7 FR-24: «Meldte spørsmål telles ikke (FR-31).»
- Ordlisten: «**Meldt spørsmål:** Et spørsmål brukeren har meldt som feil eller uklart. Det er ute av feilbanken, dekningsgraden og nye økter.»

## 4. Tekst til arkitekturen (ARCHITECTURE-SPINE.md)

- **AD-2:** under «Ellers: `ingen`»: «Et meldt spørsmål (`meldt_tidspunkt` satt) gir alltid `ingen`, og raden endres ikke.» Legg FR-31 til i Binds.
- **AD-3:** etter regelen: «Et meldt spørsmål er ikke i feilbanken, uansett raden. Raden slettes ikke.» Legg FR-31 til i Binds.
- **AD-4:** i definisjonen av dekket: «Meldte spørsmål telles verken som dekket eller i nevneren. Et nivå der alle spørsmålene er meldt, teller som et nivå uten quiz.» Legg FR-31 til i Binds.
- **AD-16:** under Forsøk og Øvingsøkt: «uten meldte spørsmål». Ny linje: «En quiz uten spørsmål som ikke er meldt, kan ikke startes.» Legg FR-31 til i Binds.
- **Ny regel under AD-1 eller i AD-3:** «`Sporsmal.objects.ikke_meldt()` er eneste filter for meldte spørsmål. Det brukes i `apne_rader`, `_lag_innhold`, `_lag_oving_innhold` og `services.dekningsgrad`. Bare `services.sporsmal.meld_sporsmal(sporsmal)` skriver `meldt_tidspunkt`.»
- **URL-er:** `GET /okter/<id>/meld/<nr>/` viser bekreftelsessiden, og `POST` på samme URL melder spørsmålet og sender tilbake til resultatet. Økten og nummeret gir tilgangskontrollen (`hent_egen(Okt, …)`) og spørsmålet fra `Okt.innhold`, så ingen spørsmål-ID står i URL-en.

## 5. Hva det betyr for koden som finnes

Alle stedene er små endringer i kode som er bygget fra før:

- `studier/services/feilbank.py`:
  - `registrer_svar` får en vakt for meldte spørsmål.
  - `apne_rader` bruker `ikke_meldt()`.
- `studier/services/okter.py`: `_lag_innhold` og `_lag_oving_innhold` bruker `ikke_meldt()`, og start av en quiz uten slike spørsmål gir `None`.
- `studier/services/dekningsgrad.py` (story 5.1, bygges nå): spørsmålsutvalget bruker `ikke_meldt()`.
- S7: quizkortet viser låst knapp når alle spørsmålene er meldt (B4).
- S11/S12: «Meld som feil eller uklart» på ✕-rader, og «Meldt som feil» på rader som er meldt.

Story 4.3 i [epics-christian.md](epics-christian.md) stemmer med forslaget. Når gruppa har bestemt seg, trengs bare en setning om B4 og B7.

## 6. Godkjenning

Godkjent av gruppa (Christian, Martin og Magnus) i fellesmøte 25.11.2026, med anbefalingene i B1–B8 uendret. Kapittel 3 er lagt inn i PRD-en og kapittel 4 i arkitekturen samme dag.

## 7. Neste steg

1. Christian, Martin og Magnus godkjenner eller endrer B1–B8.
2. Kapittel 3 og 4 limes inn i PRD-en og arkitekturen, og forslaget får status `godkjent`.
3. Story 4.3 bygges med `bmad-build`.
