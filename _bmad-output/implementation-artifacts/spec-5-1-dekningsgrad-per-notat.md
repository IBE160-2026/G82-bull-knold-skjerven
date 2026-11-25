---
title: 'Story 5.1: Dekningsgrad per notat'
type: 'feature'
created: '2026-11-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 1
baseline_commit: 'f40dc86a71c2a5926b2027379a9d726d07712a66'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Studenten ser ikke hvor mye av et notat hen kan. S7 har ingen dekningsgrad, og `services.dekningsgrad` finnes ikke (FR-24, AD-4, UX-DR8, UX-DR23, TF-6).

**Approach:** Lag `studier/services/dekningsgrad.py` som eneste sted dekningsgraden regnes ut, og vis totalen med reiserute og nivåene øverst på S7. Ingenting lagres.

## Boundaries & Constraints

**Always:**
- **Dekket spørsmål (AD-4):** minst ett `Svar` med riktig alternativ i en `Okt` med `status=levert` (forsøk eller øving), og ingen `Feilbankrad` med `laert_tidspunkt IS NULL`.
- **Tjeneste:** `for_notat(notat)` gir totalen som `float` mellom 0 og 1 uten avrunding, og for hvert nivå i `Vanskelighetsgrad` andelen (`float`), eller `None` når nivået ikke har noen quiz.
  - Total = 0,2 × lett + 0,3 × middels + 0,5 × vanskelig, der `None` teller som 0.
  - Vektene er konstanter i modulen.
  - Nevneren er alle spørsmålene på nivået i notatets quizer.
  - Antall spørringer avhenger ikke av antall spørsmål.
- **S7, øverst** under h1 og over «Øv på feil» (UX-DR23): en seksjon med h2 «Dekningsgrad».
  - Totalen som tekst, for eksempel «35 %», avrundet til hele prosent i malen.
  - **Avrunding (avgjort av Magnus 25.11):** gjelder totalen, nivåene og bredden på reiseruten.
    - Nærmeste hele prosent, med ,5 opp (12,5 % gir 13 %).
    - Aldri 100 % før verdien er nøyaktig 1, da vises 99 %.
    - Aldri 0 % når verdien er over 0, da vises 1 %.
  - Reiseruten fra S9 (fyll, fåret og flagget) med `aria-hidden`, fordi prosenten står som tekst.
  - Under: «Lett», «Middels» og «Vanskelig», hver med «N %» eller «Ingen quiz».
  - Deretter «Vanskelige spørsmål teller mest (50 %).» og hjelpeteksten (avgjort av Magnus 25.11): «Dekningsgraden kan gå ned når du lager en ny quiz, fordi de nye spørsmålene ikke er besvart ennå. Uten quiz på vanskelig kommer du ikke over 50 %.»
  - Et notat uten quiz viser 0 % og «Ingen quiz» på alle tre.
- Reiseruten flyttes til en partial som S9 og S7 bruker. S9 skal gi samme HTML som før.
- Ingen ny modell, migrering eller lagret verdi. Ingen JavaScript.

**Never:**
- Ikke dekningsgrad per emne, S3 eller S4 (5.2). Ikke historikk (5.3).
- Ikke filtrering av meldte spørsmål (4.3 er ikke bygget). Ingen annen implementasjon av «dekket».

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| FR-24-eksempel | lett 2/2 dekket, middels 1/2, ingen vanskelig quiz | total nøyaktig 0,35, vanskelig `None`. S7 «35 %» og «Ingen quiz» | N/A |
| Ny quiz | ny middels-quiz uten svar | middels-andelen og totalen går ned | N/A |
| Uten vanskelig | lett og middels 100 % | total 0,5, aldri over | N/A |
| Påbegynt | riktig svar bare i påbegynt økt | ikke dekket | N/A |
| Åpen rad | riktig levert svar, men åpen feilbankrad | ikke dekket | N/A |
| Lagt i feilbanken etterpå | dekket, så feil i nytt levert forsøk | ikke dekket lenger | N/A |
| Lært i øving | rad lært i levert øving | dekket | N/A |
| Uten quiz | notat uten quizer | total 0, alle nivåer `None`. S7 «0 %» | N/A |
| Andre notater | riktige svar i et annet notat | påvirker ikke | N/A |
| Avrunding | 1/3 → «33 %», 1/8 → «13 %», 0,9967 → «99 %», 0,004 → «1 %», 1 → «100 %», 0 → «0 %» | som vist, også for nivåene | N/A |

</frozen-after-approval>

## Code Map

- `studier/services/dekningsgrad.py` (ny) -- `for_notat`. Annoter spørsmålene i `Sporsmal.objects.filter(quiz__notat=notat)` med `Exists(Svar …, okt__status=levert, alternativ__er_riktig=True)` og `~Exists(Feilbankrad …, laert_tidspunkt__isnull=True)`, og tell per `quiz__vanskelighetsgrad`. Nivåer uten quiz finnes med `notat.quizer.values_list("vanskelighetsgrad")`.
- `studier/services/feilbank.py` -- definisjonen av en åpen rad (`laert_tidspunkt IS NULL`), som `apne_rader`. Ikke endre den.
- `studier/views.py:242` `notat` -- legg `dekning` i konteksten. Notatet er alt hentet med `hent_egen`.
- `studier/templatetags/dekning.py` (ny, med `__init__.py`) -- filteret `hel_prosent` som avrunder etter regelen over (`Decimal` med `ROUND_HALF_UP`, deretter grensene for 0 og 100). AD-4 sier at avrundingen bare skjer i malen, så den hører ikke hjemme i tjenesten eller viewet. Ikke bruk `widthratio` til dekningsgraden: den bruker Pythons `round()`, som runder ,5 til partall.
- `templates/studier/notat.html` -- ny seksjon før `ov-overskrift`-seksjonen, med samme kortstil (`rounded-lg border … shadow-md`). Totalen og nivåene: `{{ verdi|hel_prosent }} %`, og reiseruten får samme tall.
- `templates/studier/sporsmal.html:26-30` -- reiseruten, som flyttes til `templates/partials/reiserute.html` med parameteren `prosent`. S9 bruker `{% widthratio nr antall 100 as prosent %}`.
- `static/css/input.css:65-102` -- `.reiserute` og `.reiserute-faar`. Bygg `app.css` på nytt bare hvis nye klasser trengs: installer `tailwindcss` og `@tailwindcss/cli` 4.3.5 midlertidig med `npm i --no-save --no-package-lock`, kjør `npx @tailwindcss/cli -i static/css/input.css -o static/css/app.css --minify`, og fjern `node_modules`.
- Tester: mønstrene i `studier/tests/test_okter.py` (`OktTestCase`, `_quiz`) og `test_oving.py`. `Okt`, `Svar` og `Feilbankrad` kan lages direkte.

## Tasks & Acceptance

**Execution:**
- [x] `studier/services/dekningsgrad.py` -- tjenesten. Docstringen sier at meldte spørsmål telles til story 4.3 legger til `ikke_meldt()` her.
- [x] `studier/templatetags/__init__.py`, `studier/templatetags/dekning.py` -- `hel_prosent`.
- [x] `templates/partials/reiserute.html`, `templates/studier/sporsmal.html` -- partialen, og S9 bruker den.
- [x] `studier/views.py`, `templates/studier/notat.html` -- seksjonen på S7.
- [x] `studier/tests/test_dekningsgrad.py` -- én test per rad i matrisen. I tillegg:
  - antall spørringer er det samme for 1 og 3 quizer;
  - flere riktige svar på samme spørsmål (to forsøk og en øving) telles én gang, så andelen er 1,0;
  - `hel_prosent` direkte for verdiene i avrundingsraden;
  - S7-HTML med en verdi som må avrundes (lett 1 av 3: «7 %» totalt og «33 %» for Lett);
  - S7 viser «0 %» (ikke «Ingen quiz») for et nivå med quiz, men uten svar;
  - «Ingen quiz» og `aria-hidden` på ruten.

**Acceptance Criteria:**
- Gitt et notat der dekningsgraden er 0,35, når S7 vises, så står «35 %» som tekst, «Ingen quiz» ved Vanskelig og «Vanskelige spørsmål teller mest (50 %).».
- Gitt et levert forsøk, når S7 vises igjen, så er dekningsgraden oppdatert, og ingen tabell eller kolonne er endret.
- Gitt S9, når siden vises, så er reiseruten den samme som før, og testene for S9 er grønne uten endringer.

## Implementation Notes

- **Implementert av en underagent i to runder.** Den første versjonen brukte `widthratio` og ble rullet tilbake etter review-runde 1, da Magnus valgte en annen regel for avrunding (se Spec Change Log). Review-runde 2 ga 7 rettelser.
- **Tjenesten:** `for_notat` gir `Dekning(total, nivaer)` (`NamedTuple`) med 2 spørringer. Vektene står i `VEKTER`. Docstringen sier at meldte spørsmål telles til 4.3 legger til `ikke_meldt()`.
- **`hel_prosent`** (`studier/templatetags/dekning.py`) avrunder verdien til 9 desimaler før ,5 rundes opp, så flyttallsfeil som 0,22499999999999998 gir 23 %.
- **Partialen** `partials/reiserute.html` gir byte-lik HTML på S9. Det er kontrollert for 10 kombinasjoner av posisjon og antall.
- **CSS:** bare klasser som alt fantes i `app.css`, så den er ikke bygd på nytt.
- **Verifisert:** ruff, `makemigrations --check` og 476 tester grønne, 1 hoppet over. Ikke kjørt i nettleser.

## Spec Change Log

- **25.11, review pass 1 (intent_gap E1/E2/E3/B1):** `widthratio` rundet 0,9967 til «100 %», 0,004 til «0 %», og ,5 til partall. Magnus avgjorde regelen: ,5 opp, aldri 100 % før 1, og aldri 0 % over 0. Endret: regelen i frosset blokk, en rad i matrisen, filteret `hel_prosent` i Code Map, og oppgavene med testene fra V1, B4, B6 og B8. Unngår at S7 viser «ferdig» når spørsmål ikke er dekket. KEEP fra første utkast:
  - tjenesten med `alias(Exists…)`, `values("quiz__vanskelighetsgrad")` og `Count(filter=Q(riktig=True, apen=False))`, med 2 spørringer;
  - `_dekning(notat)` i views med nivåene som liste med `navn` og `andel`;
  - kortet som `<section>` med `<dl class="flex flex-wrap gap-4">`;
  - partialen `partials/reiserute.html` uten avsluttende linjeskift, slik at S9 gir samme HTML;
  - bare klasser som alt finnes i `app.css`.

## Review Triage Log

B = Blind Hunter, E = Edge Case Hunter, V = Verification Gap. Pass 1, 25.11.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| E1 | En total mellom 0,995 og 1 vises som «100 %» med full rute, selv om spørsmål ikke er dekket | medium | Bekreftet: `widthratio` runder til nærmeste. Eksempel: lett 59 av 60 (to quizer), resten fullt, gir 0,9967. Spec-en sier bare «avrundet til hele prosent» | intent_gap (med E2, E3, B1, V-annet) |
| E2 | En total over 0 men under 0,005 vises som «0 %» | low | Bekreftet, krever over 100 spørsmål på lett. Samme regel som E1 | intent_gap (med E1) |
| E3 | Nivåer på x,5 % rundes til partall (12,5 gir 12, 37,5 gir 38), og 199/200 gir 100 % | low | Bekreftet: Pythons `round()` | intent_gap (med E1) |
| B1 | Avrundingen kan gi 100 % og 0 % | medium | Samme som E1 | intent_gap (med E1) |
| V-annet | `widthratio` runder ,5 til partall | low | Samme som E3 | intent_gap (med E1) |
| V1 | Ingen S7-test med en verdi som må avrundes | medium | Bekreftet (filed gap) | patch |
| B2 | Ingen test for avrunding av prosent som ikke er hele tall | medium | Samme som V1 | patch (med V1) |
| B3 | Vekten 50 % står som tekst i malen | low | Vektene er bestemt i FR-24 og endres ikke uten ny PRD. En ny kontekstverdi gir mer kode enn den sparer | avvist |
| B4 | Ingen S7-test for «0 %» på et nivå med quiz, men uten svar | medium | Bekreftet: bare `None`-siden («Ingen quiz») vises i testene | patch |
| B5 | Grenen for en quiz uten spørsmål er ikke testet | low | En quiz har alltid minst 5 spørsmål (valideringen i 2.1). Grenen hindrer bare deling med 0 | avvist |
| B6 | Ingen test for at flere riktige svar på samme spørsmål telles én gang | low | `Exists` teller én gang i dag. En test er en direkte tilføyelse og verner mot en join-omskriving | patch |
| B7 | Flyttallstestene bruker eksakt likhet | low | Spec-en krever nøyaktig 0,35, og summen har fast rekkefølge (`Vanskelighetsgrad`). Ingen feil i dag | avvist |
| B8 | Docstringen sier ikke at meldte spørsmål telles til 4.3 er bygget | low | Bekreftet. Direkte rettelse: én setning | patch |
| B9 | Partialen er avhengig av at fila ikke slutter med linjeskift | low | Et ekstra linjeskift gir bare mellomrom i HTML-en og endrer ikke visningen | avvist |
| B10 | Testhjelperen `_quiz` dupliserer oppsett | low | Bygger gyldige quizer direkte, fordi `generer_synkront` krever minst 5 spørsmål. Liten nytte av å flytte den | avvist |

Pass 2, 25.11 (etter ny implementasjon):

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| E1 | ,5 rundes ned på grunn av flyttallsfeil: middels 3/4 gir 0,22499999999999998 og «22 %» | medium | Bekreftet. Bryter regelen «,5 opp». Direkte rettelse: avrund `Decimal` til 9 desimaler før ,5 opp | patch (med B1, E2) |
| E2 | Samme sak i `hel_prosent`: `str()` beholder flyttallsfeilen | medium | Samme som E1 | patch (med E1) |
| B1 | `hel_prosent` runder ,5 ned i 973 kombinasjoner | medium | Samme som E1 | patch (med E1) |
| B2 | Ingen test der en utregnet total havner på ,5 | medium | Bekreftet. Middels 3/4 → «23 %» | patch |
| V1 | Vekten for vanskelig (0,5) er aldri sjekket i en total | medium | Bekreftet (filed gap) | patch |
| B3 | Kravet `alternativ__er_riktig=True` er ikke testet alene | medium | Bekreftet: hvert feil svar lager også en åpen rad | patch |
| B7 | «Ingen quiz» sjekkes bare én gang for et notat uten quiz | low | Bekreftet. Direkte rettelse: tell tre | patch |
| E3 | `hel_prosent` kaster feil for en tallstreng | low | Filteret får bare flyttall fra tjenesten. Vakten gir mer kode uten at feilen kan nås | avvist |
| B4 | `hel_prosent` tåler ikke strenger og klemmer ikke verdier utenfor 0–1 | low | Samme som E3. Tjenesten gir alltid 0–1 | avvist |
| E4 | `KeyError` hvis `Vanskelighetsgrad` får et nytt nivå | low | Nivåene er bestemt i FR-11 og FR-24 | avvist |
| B5 | Den andre spørringen (`med_quiz`) er overflødig | low | Spec-en bestemmer at nivåer uten quiz finnes med `values_list`. Story 4.3 endrer utvalget uansett | avvist |
| B6 | Ingen test sjekker `left:` for fåret på S9 | false | `test_okter.py:375-377` sjekker både `width: 60%` og `left: 60%` (bekreftet av V) | avvist |
| B8 | Typen til `Dekning.nivaer` og at `hel_prosent` kjøres to ganger i malen | low | Kosmetisk. Samme verdi gir samme resultat | avvist |


## Verification

**Commands:**
- `uv run ruff check . && uv run ruff format --check .` -- ingen funn
- `uv run python manage.py makemigrations --check --dry-run` -- ingen endringer
- `uv run python manage.py test` -- alle grønne

**Manual checks:**
- S7 ved 360 px: ingen vannrett rulling. Fåret og flagget står innenfor ruten.
