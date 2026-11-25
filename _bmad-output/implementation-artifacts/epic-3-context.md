# Epic 3 Context: Ta quiz, se resultat og fyll feilbanken

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->
<!-- Kompilert 25.11.2026, etter at Martins design ble felles UX (23.11). -->

## Goal

Studenten tar en quiz ett spørsmål om gangen, med svar som lagres på serveren for hvert steg, kan fortsette der hen slapp (også på en annen enhet), ser over og leverer, og ser poengsummen uten fasit. Feilsvarene havner i notatets feilbank, og et spørsmål blir lært etter to riktige svar på rad. En levert quiz kan tas på nytt, som er den minste veien til «lært» hvis Epic 4 kuttes. Etter denne epicen er kjerneløpet notat → quiz → feilbank → lært ferdig. Epicen bygger `Okt`-tjenestene (`start_eller_fortsett_okt`, `lagre_svar`, `lever_okt`) og feilbankregelen (`registrer_svar`), som Epic 4 bruker uendret med `type=oving`. Kjerne: FR-17, FR-19, FR-20, FR-21, FR-23 (regelen). Bør: FR-18 (lagring underveis og fortsette). Kan kuttes: fortsette fra annen enhet (følger likevel med, fordi svarene ligger på serveren).

## Stories

- Story 3.1: Starte og svare på en quiz
- Story 3.2: Regelen for feilbanken
- Story 3.3: Levere og se resultatet
- Story 3.4: Ta en quiz på nytt
- Story 3.5: Fortsette der jeg slapp

## Requirements & Constraints

- **Svare:** ett spørsmål om gangen. Forrige og Neste lagrer svaret, også uten valgt svar, og svar kan endres før levering. Ingen tidsgrense i quizen.
- **Levere:** krever at alle spørsmål er besvart. Appen viser hvilke som mangler, og serveren avviser levering med ubesvarte spørsmål selv om knappen omgås. Dobbeltklikk og to faner gir én levering.
- **Påbegynte forsøk:** høyst ett per quiz. Å starte quizen igjen fortsetter det påbegynte. Påbegynte forsøk påvirker aldri feilbank, dekningsgrad eller historikk, og kan fortsettes fra en annen enhet.
- **Resultat:** poengsum og riktig/feil per spørsmål. Fasiten vises ikke for feil svar. Fasit og begrunnelse vises bare for spørsmål som er lært. Forsøket lagres med dato og poengsum.
- **Feilbank:** hvert feilbesvarte spørsmål legges i notatets feilbank høyst én gang ved levering. Lært etter to riktige på rad etter at spørsmålet kom i feilbanken. Feil svar nullstiller telleren, også for et lært spørsmål, som da kommer tilbake. Svar i nye forsøk og i «Øv på feil» teller likt.
- **Ta på nytt:** nytt forsøk med alternativene stokket på nytt. Gamle forsøk endres ikke.
- **Tilgang:** en annen brukers økt, resultatside eller `alternativ`-ID i POST gir «Fant ikke siden».
- **KI-merking:** «Laget av KI (<modell>). Spørsmålene kan inneholde feil.» øverst på quizsidene, også i testmodus.
- **Universell utforming (WCAG 2.2 A/AA)** og 360 px uten vannrett rulling er akseptansekriterier i hver story med grensesnitt.

## Technical Decisions

- **`Okt` (AD-6):** én modell for forsøk og øvingsøkt. `type` ∈ {`forsok`, `oving`}, `status` ∈ {`pabegynt`, `levert`}, `opprettet`, `sist_endret`, `levert_tidspunkt`, `poengsum`, `antall`. `notat` alltid satt, `quiz` satt hvis og bare hvis `type=forsok` (`CheckConstraint`). Betinget `UniqueConstraint`: høyst én påbegynt `forsok` per quiz og én påbegynt `oving` per notat. Modellene finnes fra story 1.1.
- **`start_eller_fortsett_okt` (AD-6, AD-16):** kalles bare med POST. Henter den påbegynte økten eller lager en ny, og sender til første ubesvarte spørsmål.
- **`Okt.innhold` (AD-16):** `JSONField` `[{"sporsmal": id, "alternativer": [id, id, id]}, …]` i visningsrekkefølge, låst ved opprettelse og aldri endret. Forsøk: quizens spørsmål i quizens rekkefølge, alternativene stokket. Visning, telling av hva som mangler, levering og resultat bruker bare listen. `nr` (1-basert) brukes bare til navigering.
- **`Svar` (AD-7):** `okt`, `sporsmal`, `alternativ`, `hendelse`, med `UniqueConstraint(okt, sporsmal)`. Svar lagres og sammenlignes aldri via posisjon eller bokstav.
- **`services.okter.lagre_svar(okt, sporsmal, alternativ)` (AD-17):** eneste vei til å skrive svar. Avviser hvis økten ikke er påbegynt, spørsmålet ikke står i `okt.innhold`, eller alternativet hører til et annet spørsmål. Ellers `update_or_create` på (`okt`, `sporsmal`) og oppdatering av `sist_endret`. Forsøk på å svare i en levert økt sender til resultatsiden.
- **`services.okter.lever_okt(okt)` (AD-18):** én `transaction.atomic`. Første skriving: `filter(pk, status="pabegynt").update(status="levert", levert_tidspunkt=now())`. 0 rader → gjør ingenting mer. Deretter i samme transaksjon: sjekk at alle er besvart (rull tilbake hvis ikke), `registrer_svar` for hvert spørsmål i `okt.innhold`, lagre `Svar.hendelse`, `poengsum` og `antall`.
- **`services.feilbank.registrer_svar(sporsmal, riktig) -> Hendelse` (AD-2, AD-3):** eneste sted som oppretter eller endrer `Feilbankrad`, og kalles bare fra `lever_okt`. `Hendelse` ∈ {`lagt_i`, `nullstilt`, `opp`, `laert`, `ingen`}. Feil: `get_or_create` med teller 0 (`lagt_i`), eller nullstill teller og `laert_tidspunkt=None` på eksisterende rad (`nullstilt`). Riktig i feilbanken: teller +1 (`opp`), ved 2 settes `laert_tidspunkt` (`laert`). Ellers `ingen`. Høyst én rad per spørsmål, og rader slettes aldri. «I feilbanken» = `laert_tidspunkt IS NULL`. Tester dekker alle fem hendelsene og sekvensen feil → riktig → feil → riktig → riktig.
- **Spørsmålsidentitet (AD-5):** et spørsmål hører til én quiz. Lik tekst i to quizer er to spørsmål med hver sin feilbankrad.
- **Fasit (AD-20):** `er_riktig` og `begrunnelse` sendes aldri til quizmalen. En test sjekker at HTML-en ikke skiller ut det riktige alternativet med klasse, dataattributt eller rekkefølge. Resultatsidene leser hendelsene fra `Svar.hendelse` og regner dem aldri ut på nytt. Fasit vises bare når `fasit_synlig(sporsmal)` er sann (`laert_tidspunkt` satt). Rettingen skjer i tjenestelaget.
- **Skjemaer (AD-13):** Forrige, Neste og Lever er vanlige POST-skjemaer som virker uten JavaScript. HTMX er bare forbedring og treffer samme endepunkter. POST/redirect/GET.
- **Tilgang (AD-8):** alle ID-er fra URL og POST løses med `hent_egen`/`egne`. Veien til eieren er `notat__emne__eier` for `Okt` og `okt__notat__emne__eier` for `Svar`. `alternativ` valideres mot spørsmålet i økten.
- **Generering → quiz (AD-9):** når siste steg har lagret quizen, kaller stegviewet `start_eller_fortsett_okt` og svarer med `HX-Redirect` til `/okter/<id>/sporsmal/1/`. En annen fane som spør etter at jobben er ferdig, får samme økt.
- **URL-er:** `/okter/<id>/sporsmal/<nr>/` (S9, GET viser, POST lagrer og navigerer), `/okter/<id>/lever/` (GET viser S10, POST leverer), `/okter/<id>/resultat/` (S11). Start og «Ta på nytt» er POST fra Notatsiden eller resultatsiden.
- **Fortsett-lenke og sortering (AD-6, AD-16):** fortsett-lenken peker på første spørsmål uten svar. «Fortsett der du slapp» sorteres på `sist_endret`, nyeste først.

## UX & Interaction Patterns

- **S9 Ta quiz:** KI-merket øverst, så «Spørsmål N av M» med reiserute (fåret i ballongen med `aria-hidden` og flagg i enden). Spørsmålet står på et flashcard (maks 560 px, `question`-typografi) som `<legend>` i en `<fieldset>`. Tre `option-card` som radioknapper i `<label>`, minst 44 px, i rekkefølgen fra `Okt.innhold`, med lagret svar valgt. Valgt alternativ: 2 px `accent-strong`-kant, `surface-muted` og fylt radioknapp (form, ikke bare farge). Hover: `card-hover`, brun kant, løft 1 px. Piltastene velger. `lang="{{ quiz.sprak }}"` på spørsmål og alternativer når språket ikke er norsk. `<title>` «Spørsmål N av M – <notat> – FåreQuiz». Brødsmulestien og «‹ Tilbake» peker på notatet.
- **Navigasjon i S9:** fokus flyttes til spørsmålet etter Forrige/Neste. Neste på siste spørsmål går til S10. Mislykket lagring: «Svaret ble ikke lagret. Sjekk nettet og prøv igjen.» ved knappen, og studenten blir på spørsmålet. Under `md` er knappene like brede som skjermen og står nederst i innholdet (ikke fast i bunnen). Fra `md` står de på én linje.
- **S10 Se over og lever:** ett nummer per spørsmål merket «Besvart» eller «Ikke besvart», hvert en lenke («Spørsmål 4 – ikke besvart»). «Lever» har `aria-disabled` med synlig tekst «Du har ikke svart på spørsmål 4 og 7.». Avvist levering viser S10 igjen med samme tekst i `role="alert"`.
- **S11 Resultat:** «7 av 10 riktige» i `score` (`tabular-nums`) med `role="status"`. Én rad per spørsmål med spørsmålstekst, valgt svar og ✓ «Riktig» eller ✕ «Feil» i `success`/`error`, ikonet med `aria-hidden`. «N spørsmål er lagt i feilbanken.» når N > 0. Fasiten vises ikke. Knappen «Øv på feil» kommer i story 4.1.
- **Quizkort på S7:** påbegynt forsøk vises som «Påbegynt – spørsmål 5 av 10» med knappen «Fortsett». Ellers «Ta quiz» eller «Ta på nytt». (Story 3.1 kaller knappen «Ta quizen». Avklar teksten, UX-designet bruker «Ta quiz».)
- **«Fortsett der du slapp» på S3:** boks øverst med én rad per påbegynt økt, nyeste først: «Middels, 10 spørsmål», «Webutvikling · HTML-forelesning · spørsmål 5 av 10» og knappen «Fortsett quizen», som lenker til første ubesvarte spørsmål. Vises ikke uten påbegynte økter.
- **Tone:** norsk bokmål, du-form, kort og saklig, uten utropstegn, emojier og feiring. Riktig og feil sies rett ut.

## Cross-Story Dependencies

- Epic 3 krever ferdige quizer fra Epic 2 (2.4), Notatsiden S7 (2.3/2.6), sidemalen (1.3) og `hent_egen`/`egne` (1.1). Alle modellene finnes fra story 1.1.
- 3.1 eier `start_eller_fortsett_okt`, `lagre_svar`, S9 og endringen i stegviewet fra 2.4 (åpne quizen på spørsmål 1 i stedet for Notatsiden).
- 3.2 er bare tjenestelag og tester, og kan bygges parallelt med 3.1. 3.3 trenger både 3.1 (svar) og 3.2 (`registrer_svar` i `lever_okt`).
- 3.4 bygger på 3.3 (leverte forsøk og resultatside). 3.5 bygger på 3.1 (påbegynte økter) og quizkortene på S7.
- Epic 4 gjenbruker S9, S10, `lever_okt` og resultatradene med `type=oving`, og legger «Øv på feil»-knappen på S11. Øvingsøkter skal også vises i «Fortsett der du slapp» (3.5).
- Epic 5 bruker `Svar` i leverte økter og åpne feilbankrader til dekningsgraden, og leverte forsøk til historikken. `seed_testdata` (Epic 6) bruker `lagre_svar` og `lever_okt`.
