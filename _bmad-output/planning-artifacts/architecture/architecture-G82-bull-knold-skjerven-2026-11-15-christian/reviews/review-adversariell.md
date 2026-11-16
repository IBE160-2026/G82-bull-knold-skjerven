---
type: architecture-review
mode: adversariell
target: ../ARCHITECTURE-SPINE.md
prd: ../../../prds/prd-G82-bull-knold-skjerven-2026-11-11/prd.md
created: '2026-11-15'
---

# Adversariell review av arkitektur-spinen – FåreQuiz v1

## Metode

For hvert funn lager jeg to enheter ett nivå ned (stories eller moduler som ulike utviklere eller AI-agenter bygger). Begge følger hver AD bokstavelig, men de bygger likevel noe som ikke passer sammen. Hvert slikt par er et hull i spinen, og jeg foreslår en ny eller strammere AD (Rule) som lukker det.

Jeg har sett bort fra funn som ikke realistisk vil skje i en lokal Django-app med tre studenter og én bruker om gangen (se «Forkastet» nederst). Det som er igjen, er ting som skjer når én person bruker appen normalt: dobbeltklikker, laster siden på nytt, har to faner åpne eller bruker tilbakeknappen.

Viktig fakta om kjøremiljøet: `runserver` er flertrådet som standard, og SQLite i Django bruker `BEGIN DEFERRED`. To forespørsler fra samme bruker kan derfor kjøre samtidig og lese samme tilstand før en av dem skriver.

## Verdict

Spinen er solid på eierskap, KI-grensen og feilbankregelen. Men den sier ikke **hva en øvingsøkt inneholder**, **hvem som eier lagring av svar underveis** eller **hvordan levering og genereringssteg beskyttes mot å kjøre to ganger**. Det er der to riktige implementasjoner vil kollidere. Fire funn bør lukkes før stories skrives (F1–F4). De andre kan lukkes med korte tillegg.

## Oversikt

| # | Alvorlighet | Hull | Berører |
| --- | --- | --- | --- |
| F1 | Kritisk | Hvilke spørsmål en øvingsøkt inneholder, og hva som skjer når feilbanken endres mens økten er påbegynt | AD-2, AD-6, AD-7, FR-22, FR-23 |
| F2 | Høy | Lagring av svar underveis har ingen eier: duplikate `Svar`, svar på levert økt, alternativ fra feil spørsmål | AD-1, AD-7, AD-13, FR-17–FR-19 |
| F3 | Høy | Dobbel levering og transaksjonsgrensen ved levering og start av økt | AD-2, AD-6, FR-18, FR-21, FR-23 |
| F4 | Høy | Genereringskjeden kjøres to ganger (siden lastes på nytt, to faner), uklart hva som lagres mellom stegene, jobber som aldri blir ferdige | AD-9, AD-10, FR-14, FR-15 |
| F5 | Høy | Testmodus: SHA-256 av hva, og hvordan `forhandslagret` kommer fram til `Quiz` | AD-11, AD-12, FR-27 |
| F6 | Middels | KI-kall inne i en databasetransaksjon låser SQLite | AD-2, AD-9, konvensjoner |
| F7 | Middels | `Okt` har to veier til eieren, men AD-8 krever én vei per modell | AD-6, AD-8 |
| F8 | Middels | Hvor fasiten vises, og hvordan «lært i denne økten» og «lagt i feilbanken» telles | AD-2, FR-19, FR-23, UX |
| F9 | Middels | Hvordan rekkefølgen lagres på `Okt`, posisjon i URL-en og Fortsett-lenken | AD-7, AD-13, konvensjoner |
| F10 | Middels | `slett_emne` sletter i feil rekkefølge, og emnet kan slettes mens en generering pågår | AD-9, AD-14, FR-6 |
| F11 | Middels | Seed-kommandoen: synkron generering, ekte API-kall og kjøring to ganger | AD-1, AD-9, AD-12, FR-28 |
| F12 | Middels | `Bruker` arver `username` fra `AbstractUser`, og store og små bokstaver i e-post | AD-15, FR-1, FR-2 |
| F13 | Lav | Unikt emnenavn via ModelForm uten `eier` gir IntegrityError | AD-1, FR-4, FR-5 |
| F14 | Lav | Hvordan filen lagres på `Notat`, og hvem som skriver den | AD-1, AD-14, FR-8 |

---

## F1 – Hvilke spørsmål en øvingsøkt inneholder (Kritisk)

**Berører:** AD-2, AD-6, AD-7, FR-22, FR-23

**Hullet:** AD-6 sier at en `oving` «peker på ett `Notat`». AD-7 sier at rekkefølgen på alternativene lagres når økten opprettes. Ingen AD sier om spørsmålene i økten er et øyeblikksbilde av feilbanken da økten ble startet, eller om de hentes på nytt fra feilbanken hver gang.

**Par A – øyeblikksbilde mot live spørring:**

- **Story A (start Øv på feil, `services/okter`)** lagrer `{sporsmal_id: [alternativ_id, …]}` for alle åpne `Feilbankrad` i notatet når økten opprettes. AD-7 krever at rekkefølgen lagres ved opprettelse, så A tolker dette som at også spørsmålene ligger fast.
- **Story B (vise spørsmål og levere en øvingsøkt)** henter spørsmålene med `Feilbankrad.objects.filter(laert_tidspunkt__isnull=True, sporsmal__quiz__notat=okt.notat)`. AD-6 sier at øvingsøkten peker på notatet, ikke på spørsmål, og AD-3 definerer «i feilbanken».
- **Resultat:** Brukeren starter en øvingsøkt med 4 spørsmål og svarer på 2. I en annen fane leverer hen et forsøk med 3 nye feil. Når hen går tilbake til øvingsøkten, viser B 7 spørsmål. 3 av dem har ingen lagret rekkefølge, så de stokkes på nytt (brudd på AD-7) eller gir `KeyError`. Hen kan ikke levere før alle 7 er besvart (FR-17), og telleren viser ikke det samme som A.

**Par B – spørsmål som blir lært mens økten er påbegynt:**

- **Story C (levering)** kaller `registrer_svar` for hvert `Svar` i økten, slik AD-2 sier.
- **Story D (vise spørsmål)** skjuler spørsmål som er blitt lært siden økten startet («de er jo ikke i feilbanken lenger», AD-3).
- **Resultat:** Spørsmål Q blir lært via et forsøk mens øvingsøkten er påbegynt. D skjuler Q, men C har allerede et `Svar` for Q og leverer det. Er svaret feil, åpner AD-2 raden igjen for et spørsmål brukeren aldri så i økten. Og hvis feilbanken blir helt tom, låser FR-22 knappen, mens Fortsett-boksen (UX) fortsatt viser den påbegynte økten.

**Foreslått Rule (ny AD-16 – Innholdet i en økt ligger fast fra den opprettes):**

> En `Okt` lagrer ved opprettelse en ordnet liste over spørsmålene sine, med rekkefølgen på alternativene for hvert spørsmål (se F9 for formatet). For `forsok` er det alle spørsmålene i quizen. For `oving` er det alle spørsmålene med åpen `Feilbankrad` i notatet akkurat da. Listen endres aldri etterpå. Visning, telling av hva som mangler, levering og resultat bruker bare denne listen. Ved levering kaller tjenesten `registrer_svar` for alle spørsmålene i listen, også dem som er blitt lært eller er kommet inn i feilbanken på nytt siden økten startet. AD-2 gjelder da som vanlig: et riktig svar på et spørsmål som ikke er i feilbanken, gjør ingenting, og et feil svar åpner raden igjen. En påbegynt `oving` kan fortsettes selv om feilbanken er blitt tom. Knappen «Øv på feil» låses bare når feilbanken er tom og det ikke finnes noen påbegynt `oving`.

---

## F2 – Lagring av svar underveis har ingen eier (Høy)

**Berører:** AD-1, AD-7, AD-13, FR-17, FR-18, FR-19

**Hullet:** AD-1 gir tjenestelaget eneretten til «`Svar` *ved levering*». Lagring av svar mens økten er påbegynt (Neste og Forrige, AD-13) er altså ikke regulert. Ingen AD krever at det finnes høyst ett `Svar` per spørsmål i en økt, at en levert økt ikke kan endres, eller at alternativet hører til spørsmålet.

**Par A – opprette mot oppdatere:**

- **Story A (Neste og Forrige, `studier/views.py`)** gjør `Svar.objects.create(okt=…, sporsmal=…, alternativ=…)` hver gang skjemaet sendes inn. AD-1 tillater dette fordi det ikke skjer ved levering, og AD-13 sier at svaret lagres før man går videre.
- **Story B (levering, `services/okter`)** går gjennom `okt.svar_set.all()` og kaller `registrer_svar` for hvert svar (AD-2).
- **Resultat:** En bruker endrer svaret sitt på Q (FR-17), og det finnes nå to `Svar` for Q. B kaller `registrer_svar` to ganger. To riktige svar gir telleren +2, og Q blir «lært» etter ett eneste riktig svar (brudd på FR-23). Poengsummen kan også bli 11 av 10.

**Par B – svar på en levert økt:**

- **Story C (resultat og historikk)** regner poengsummen ut fra `Svar` hver gang og lagrer ingenting, i samme ånd som AD-4.
- **Story A** sjekker ikke `okt.status`, fordi ingen AD sier at den skal.
- **Resultat:** Brukeren trykker tilbake fra resultatsiden og trykker Neste på et spørsmål. `Svar` endres på et levert forsøk. Poengsummen i historikken endres i ettertid, og dekningsgraden (AD-4 teller riktige `Svar` i leverte økter) blir høyere uten at feilbanken er oppdatert.

**Par C – alternativ fra et annet spørsmål:**

- **Story A** henter alternativet med `hent_egen(Alternativ, pk, bruker)` (AD-8). Eierkjeden er i orden.
- **Resultat:** Et POST-kall med `alternativ` fra et annet av brukerens spørsmål godtas. Det kan også skje helt uten vond vilje, når en gammel fane sender inn et skjema etter at rekkefølgen er endret. Om svaret er «riktig», avgjøres da av `er_riktig` på et alternativ som ikke hører til spørsmålet.

**Foreslått Rule (strammet AD-1 og ny AD-17 – Svar har én eier):**

> AD-1, ny tekst: «Bare funksjoner i `studier/services/` oppretter, endrer eller sletter `Svar`, også mens økten er påbegynt.»
>
> AD-17: `services.okter.lagre_svar(okt, sporsmal, alternativ)` er den eneste måten å skrive et svar på. Funksjonen (1) avviser hvis `okt.status != pabegynt`, (2) avviser hvis `sporsmal` ikke er i økten (AD-16) eller `alternativ.sporsmal_id != sporsmal.id`, og (3) bruker `update_or_create` på (`okt`, `sporsmal`). `Svar` har `UniqueConstraint(okt, sporsmal)`. Når en økt er levert, endres ingen av svarene i den. Poengsummen lagres på `Okt` (`poengsum`, `antall`) i samme transaksjon som leveringen og regnes aldri ut på nytt. Forsøker en bruker å endre en levert økt, sendes hen videre til resultatsiden.

---

## F3 – Dobbel levering og transaksjonsgrensen (Høy)

**Berører:** AD-2, AD-6, FR-18, FR-21, FR-23

**Hullet:** AD-2 legger `registrer_svar`-kallene i én `transaction.atomic`, men sier ikke at endringen av status til `levert` hører med i samme transaksjon. Ingen AD sier hvordan levering skal sikres mot å skje to ganger. Den betingede unike constrainten i AD-6 gjelder bare påbegynte økter, ikke leverte.

**Par A – sjekk først, så skriv:**

- **Story A (`lever_okt`)** gjør: `if okt.status == "pabegynt": with atomic(): for svar: registrer_svar(...)`, og deretter `okt.status = "levert"; okt.save()`. Dette følger AD-2 bokstavelig: kallene ligger i én transaksjon.
- **Story B (Lever-knapp med HTMX, AD-13)** legger `hx-post` på knappen uten `hx-disabled-elt`. Brukeren dobbeltklikker, eller har resultatsiden og quizen åpen i to faner.
- **Resultat:** To forespørsler leser `pabegynt` før noen av dem har skrevet. Begge kaller `registrer_svar`. Et riktig svar på et spørsmål i feilbanken gir telleren +2, og spørsmålet blir lært med ett svar. To feil svar på et nytt spørsmål gir to `create` på `Feilbankrad` og `IntegrityError` mot AD-3, altså en 500-feil. Med SQLite og `BEGIN DEFERRED` kan den andre forespørselen også få «database is locked» når den prøver å oppgradere fra lese- til skrivelås.

**Par B – start av økt:**

- **Story C («Ta quiz»)** oppretter `Okt` med `Okt.objects.create(...)` og stoler på AD-6-constrainten.
- **Story D (Fortsett-boksen og notatsiden)** har to lenker til samme quiz åpne i to faner, eller «Ta quiz» er en lenke (GET) som nettleseren henter på forhånd.
- **Resultat:** Den andre `create` gir `IntegrityError` og en 500-feil i stedet for at brukeren fortsetter det påbegynte forsøket, slik FR-18 krever.

**Foreslått Rule (ny AD-18 – Statusoverganger er betingede oppdateringer):**

> `lever_okt(okt)` kjører alt i én `transaction.atomic`. Første setning er `Okt.objects.filter(pk=okt.pk, status="pabegynt").update(status="levert", levert_tidspunkt=now())`. Endres 0 rader, er økten allerede levert. Da returnerer funksjonen uten å gjøre noe, og viewet sender brukeren videre til resultatsiden. Deretter, i samme transaksjon: sjekk av at alle spørsmål er besvart (avbryter og ruller tilbake hvis ikke), `registrer_svar` for hvert spørsmål og lagring av poengsum. `registrer_svar` bruker `get_or_create` på `Feilbankrad`.
>
> `start_eller_fortsett_okt(...)` er en POST-handling. Den bruker `get_or_create` innenfor `atomic`, fanger opp `IntegrityError` og henter da den påbegynte økten.
>
> I `settings.py` settes `DATABASES["default"]["OPTIONS"] = {"transaction_mode": "IMMEDIATE", "timeout": 20}` (Django 5.1+), slik at skrivende transaksjoner tar låsen med en gang i stedet for å feile ved oppgradering. Lever-knappen har `hx-disabled-elt="this"`, men det er bare for brukeropplevelsen. Det er den betingede oppdateringen som er beskyttelsen.

---

## F4 – Genereringskjeden kjøres to ganger (Høy)

**Berører:** AD-9, AD-10, FR-14, FR-15

**Hullet:** AD-9 sier at steg-endepunktet «utfører det steget statusen tilsier», men ikke hva som hindrer to samtidige kall på samme steg. AD-9 sier heller ikke hva som lagres mellom stegene (jobbfeltene har `raatt_svar`, men ikke filinnholdet), og ikke hva som skjer med en jobb som aldri fullføres.

**Par A – siden lastes på nytt mens generering pågår:**

- **Story A (notatsiden)** viser steglinjen med `hx-trigger="load"` mot `/jobber/<id>/steg/` når notatet har en aktiv jobb. Det er rimelig, siden AD-9 sier at fragmentet utløser neste kall.
- **Story B (steg-endepunktet)** leser `jobb.status == "lager"`, kaller `ki.generer(...)` (30–90 s) og lagrer `raatt_svar`.
- **Resultat:** Brukeren venter i 40 sekunder og trykker F5. Det er svært vanlig. Den nye siden starter en ny kjede mot samme jobb mens det første kallet fortsatt kjører i en annen tråd. Det blir to KI-kall (dobbel kostnad), to `sjekker`-steg og to lagrede `Quiz` fra samme jobb. Steget `sjekker → lager` kan også øke `forsok_nr` to ganger, slik at jobben får tre generinger i stedet for høyst to (FR-13).

**Par B – hva som lagres mellom stegene:**

- **Story C (steget `leser`)** kaller `ki.les_fil(sti)`, legger innholdet i `request.session["innhold"]` og setter status til `lager`.
- **Story D (steget `lager`)** kaller `ki.les_fil(sti)` på nytt fordi jobben ikke har noe felt for innhold. Da gjør `leser` ingenting.
- **Resultat:** I C ligger flere MB PDF-data i en sesjon i SQLite. Feilen `for_lite_innhold` blir enten oppdaget i `leser` (C) eller først i `sjekk` (D). Steglinjen og feilkodene viser da forskjellige ting avhengig av hvem som bygde hvilket steg.

**Par C – en jobb som aldri blir ferdig:**

- **Story E (låsing av knappen)** bruker AD-9-definisjonen: aktiv jobb = status ikke `ferdig` eller `feilet`, og `startet` under 120 s siden.
- **Story F (notatsiden)** viser steglinjen for den siste jobben som ikke har status `ferdig` eller `feilet`.
- **Resultat:** Brukeren lukker fanen midt i genereringen. Etter 120 s er knappen låst opp (E), men siden viser fortsatt «Lager spørsmål…» for en jobb med status `lager` som ingen noen gang vil sette til `feilet` (F). «Prøv igjen» (FR-15) vises aldri, fordi jobben aldri får `feilkode=timeout`.

**Foreslått Rule (strammet AD-9):**

> (1) Hvert steg tar jobben med en betinget oppdatering: `Genereringsjobb.objects.filter(pk=…, status=S, i_gang=False).update(i_gang=True)`. Endres 0 rader, gjør steg-endepunktet ingenting. Det returnerer fragmentet for gjeldende status med `hx-trigger="load delay:2s"`, slik at siden spør igjen. `i_gang` settes tilbake til False når steget er ferdig.
>
> (2) `Quiz` har `jobb = OneToOneField(Genereringsjobb)`, så én jobb gir høyst én quiz.
>
> (3) Steget `leser` validerer bare filen (`ki.les_fil` kan heve `for_lite_innhold`). Steget `lager` kaller `les_fil` på nytt og deretter `generer`. Ingenting fra filinnholdet lagres i sesjonen eller på jobben. Bare `raatt_svar` går videre til `sjekker`.
>
> (4) `services.generering.aktiv_jobb(notat)` er den eneste definisjonen av en aktiv jobb. Både låsing, notatsiden og steg-endepunktet bruker den. Et steg-kall, eller en visning av notatsiden, på en jobb som ikke er `ferdig` eller `feilet` og som har `startet` for over 120 s siden, setter `status=feilet, feilkode=timeout` (lat utløp) og viser «Prøv igjen».
>
> (5) «Lag quiz» oppretter jobben i en transaksjon som først sjekker `aktiv_jobb(notat)`. Bruker du `transaction_mode=IMMEDIATE` (F3), hindrer det at to faner oppretter hver sin jobb.

---

## F5 – Testmodus: SHA-256 av hva, og hvordan `forhandslagret` kommer fram (Høy)

**Berører:** AD-11, AD-12, FR-27, NFR-7

**Hullet:** AD-12 sier at testdokumentet «velges ut fra filens SHA-256». Men signaturen i AD-11 er `generer(innhold, vanskelighetsgrad, antall, timeout)`, og den får ikke filen. For DOCX og TXT er `innhold` uttrukket tekst. AD-12 sier også at `forhandslagret=True` «lagres på `Quiz`», men ingen returtype bærer flagget fra `generer` via `raatt_svar` og `sjekk` fram til tjenesten som lagrer quizen.

**Par A – hva som hashes:**

- **Story A (`ki.generer` i testmodus)** hasher `innhold`, fordi det er alt funksjonen får.
- **Story B (skriptet som lager mock-svarene)** lagrer SHA-256 av selve filen i `ki/mock/index.json`, fordi AD-12 sier «filens SHA-256».
- **Resultat:** DOCX- og TXT-testdokumentene, og PDF-ene hvis `innhold` er base64, får aldri treff. Alle testdokumentene faller tilbake til standarddokumentet med «forhåndslagret» (brudd på FR-27, kravet om at alle fem testdokumenter gir sin egen quiz).

**Par B – flagget går tapt mellom stegene:**

- **Story C (`ki`)** returnerer `(raatt, forhandslagret)` fra `generer`.
- **Story D (steget `lager`)** lagrer `raatt` i `jobb.raatt_svar`, som AD-9 sier. Det finnes ikke noe felt for flagget, og det neste steget (`sjekker`) er en ny HTTP-forespørsel.
- **Resultat:** `Quiz.forhandslagret` er alltid False. Brukeren ser ikke at innholdet er forhåndslagret (FR-27).

**Par C – merking av modellen i testmodus:**

- **Story E (lagring av quizen)** setter `Quiz.modell = ki.MODELL` (AD-11).
- **Resultat:** En mock-quiz blir merket «Laget av claude-sonnet-5-5», selv om ingen modell ble kalt. Det er misvisende KI-merking (NFR-7).

**Foreslått Rule (strammet AD-11 og AD-12):**

> `ki.les_fil(sti) -> Innhold` (dataklasse: `sha256` av filbytene, `type`, `data`). `generer(innhold: Innhold, …) -> RaattSvar` (dataklasse: `tekst`, `forhandslagret: bool`, `modell: str`, `prompt_versjon: str`). I testmodus slår `generer` opp `innhold.sha256` i `ki/mock/index.json`. `Genereringsjobb` får feltene `forhandslagret`, `modell` og `prompt_versjon`, som settes i steget `lager` og kopieres til `Quiz` i `sjekker`. I testmodus er `modell` det modellnavnet mock-svaret ble laget med (lagret i mock-filen), og malen viser «forhåndslagret» når `forhandslagret` er sann.

---

## F6 – KI-kall inne i en transaksjon låser SQLite (Middels)

**Berører:** AD-2, AD-9, konvensjonene for konfigurasjon

**Hullet:** AD-2 innfører `transaction.atomic`, men ingen AD forbyr `ATOMIC_REQUESTS=True` eller sier at KI-kall må skje utenfor en transaksjon.

**Par:**

- **Story A (settings eller grunnmur)** setter `ATOMIC_REQUESTS = True` «for sikkerhets skyld». Det bryter ikke noen AD.
- **Story B (steget `lager`)** setter `status="lager"` og kaller deretter `ki.generer` (opptil 120 s).
- **Resultat:** Statusoppdateringen tar skrivelåsen i SQLite og holder den gjennom hele KI-kallet. Alle andre skrivinger i appen, som lagring av svar og innlogging (sesjonen), får «database is locked» etter 5 s. Steglinjen i andre faner ser heller aldri statusen `lager`, fordi den ikke er committet.

**Foreslått Rule (ny AD-19 – Ingen eksterne kall inne i en transaksjon):**

> `ATOMIC_REQUESTS` er av. Ingen funksjon kaller `ki` mens en databasetransaksjon er åpen. Statusoverganger i genereringen committes før og etter KI-kallet, hver for seg. `transaction.atomic` brukes bare rundt rene databaseoperasjoner (levering, lagring av quiz, sletting av emne).

---

## F7 – `Okt` har to veier til eieren (Middels)

**Berører:** AD-6, AD-8

**Hullet:** AD-8 sier at «veien til eieren for hver modell» står i `tilgang.py`, altså én vei per modell. AD-6 lar `forsok` peke på `Quiz` og `oving` peke på `Notat`. Da har `Okt` to mulige veier, og `Svar` arver problemet.

**Par:**

- **Story A (`tilgang.py`)** registrerer `Okt: "quiz__notat__emne__eier"`, fordi historikk (AD-6) og «Ta quiz» er de første brukstilfellene.
- **Story B (Øv på feil)** oppretter `Okt(type="oving", notat=…, quiz=None)`, slik AD-6 sier.
- **Resultat:** `hent_egen(Okt, pk, bruker)` gir `Http404` for brukerens egne øvingsøkter. Hvis A i stedet legger inn en `Q(...) | Q(...)`-sjekk, får Fortsett-boksen (UX: alle påbegynte økter, nyeste først) duplikater på grunn av join, eller så legger noen til `notat` på forsøk også, mens andre fortsatt lar feltet stå tomt. Sletting via cascade fungerer i begge tilfeller, men sorteringen per notat (historikk, påbegynt på notatsiden) må skrives på to måter.

**Foreslått Rule (strammet AD-6):**

> `Okt.notat` er alltid satt (ikke null) for begge typer. `Okt.quiz` er satt bare for `forsok`. `CheckConstraint`: `type="forsok"` ⇔ `quiz IS NOT NULL`. Tjenesten setter `notat = quiz.notat` for forsøk. Eierveien i `tilgang.py` er `notat__emne__eier` for `Okt` og `okt__notat__emne__eier` for `Svar`. `Okt` har `opprettet`, `sist_endret` og `levert_tidspunkt` (null til den er levert). Historikken sorteres på `levert_tidspunkt`, og Fortsett-boksen på `sist_endret`.

---

## F8 – Hvor fasiten vises, og hva «lært i denne økten» betyr (Middels)

**Berører:** AD-2, AD-3, FR-19, FR-23, UX (Lært-boks, «3 spørsmål er lagt i feilbanken»)

**Hullet:** `registrer_svar(sporsmal, riktig)` returnerer ingenting. Resultatsiden vises etter en omdirigering (POST/redirect/GET), og må derfor finne ut fra databasen hvilke spørsmål som ble lært i *denne* økten og hvor mange som ble *lagt* i feilbanken. FR-23 sier i tillegg at forsøk teller med for «lært», men UX viser Lært-boksen bare på Øv-resultat.

**Par A – hva som ble lært i økten:**

- **Story A (Øv-resultat)** viser Lært-boksen for spørsmål der `feilbankrad.laert_tidspunkt >= okt.levert_tidspunkt`.
- **Story B (feilbanken)** lar et senere feil svar i et forsøk åpne raden igjen (AD-2), så `laert_tidspunkt` blir NULL.
- **Resultat:** Øv-resultatet for en gammel økt mister Lært-boksen (og fasiten) når brukeren åpner det igjen, eller viser den for en *annen* økt som ble levert samme sekund. Dekningsgraden og resultatsiden er da ikke enige om hva som skjedde.

**Par B – «lagt i feilbanken»:**

- **Story C (Resultat)** skriver «3 spørsmål er lagt i feilbanken», der 3 er antall feil svar.
- **Story D (Resultat, en annen utvikler)** teller nye `Feilbankrad` som ble opprettet, og får 2, fordi ett av spørsmålene allerede lå der og bare fikk telleren nullstilt.

**Par C – lært via forsøk:**

- **Story E (resultat for forsøk)** viser aldri fasit (FR-19).
- **Resultat:** Et spørsmål som blir lært med det andre riktige svaret i et *forsøk* (FR-23), tas ut av feilbanken uten at fasiten noen gang vises. FR-23 sier «det tas da ut av feilbanken, og fasiten vises».

**Foreslått Rule (strammet AD-2):**

> `registrer_svar(sporsmal, riktig) -> Hendelse`, der `Hendelse` ∈ {`lagt_i`, `nullstilt`, `opp`, `laert`, `ingen`}. `lever_okt` lagrer hendelsen på `Svar.hendelse`. Resultatsiden for begge økttypene viser Lært-boksen (spørsmål og fasit) for svar med `hendelse=laert`, og teksten «N spørsmål er lagt i feilbanken» teller `hendelse=lagt_i`. Fasiten vises ellers bare via én funksjon, `fasit_synlig(sporsmal)`, som er sann når `Feilbankrad.laert_tidspunkt IS NOT NULL`. Resultatsidene er et historisk bilde av hendelsene på leveringstidspunktet.

---

## F9 – Hvordan rekkefølgen lagres, posisjon i URL-en og Fortsett-lenken (Middels)

**Berører:** AD-7, AD-13, URL-konvensjonen, UX (Fortsett-boks «lenker rett til spørsmålet studenten kom til»)

**Hullet:** AD-7 sier at rekkefølgen «lagres på `Okt`», men ikke i hvilket format. AD-7 forbyr også at kode «lagrer eller sammenligner indekser», mens Neste og Forrige (AD-13) trenger en posisjon. Det er heller ikke sagt om alternativene i et *forsøk* skal stokkes. FR-22 krever stokking bare for øvingsøkter.

**Par A – formatet:**

- **Story A (opprette økt)** lagrer `rekkefolge = {"12": [40, 38, 39], "13": [...]}` (JSON-nøkler blir strenger).
- **Story B (vise spørsmål)** forventer `[[12, [40, 38, 39]], …]` og itererer i rekkefølge.
- **Resultat:** Spørsmålsrekkefølgen er udefinert i A (rekkefølgen på nøklene i en dict følger innsettingen, men går tapt hvis noen sorterer), og `int` mot `str` gir `KeyError` i B.

**Par B – posisjonen i URL-en:**

- **Story C (Neste og Forrige)** bruker `/okter/<id>/?nr=3`.
- **Story D (Fortsett-boksen)** tolker AD-7 («ingen indekser») og lenker til `/okter/<id>/sporsmal/<sporsmal_id>/`.
- **Resultat:** To URL-skjemaer for samme side, og lenken fra Fortsett-boksen treffer ikke viewet til C.

**Foreslått Rule (strammet AD-7):**

> `Okt.innhold` er en `JSONField` med formatet `[{"sporsmal": <id>, "alternativer": [<id>, <id>, <id>]}, …]` i den rekkefølgen spørsmålene vises. Alternativene stokkes for begge økttypene. Spørsmålene står i quizens rekkefølge for `forsok` og i rekkefølgen `Feilbankrad.opprettet` for `oving`. URL-en er `/okter/<id>/sporsmal/<nr>/`, der `nr` (1-basert) er en posisjon i navigasjonen og bare slås opp via `Okt.innhold`. Forbudet i AD-7 gjelder å lagre eller sammenligne *svar* via posisjon. Fortsett-lenken peker på første spørsmål uten `Svar`, eller på det siste spørsmålet hvis alle er besvart. Det lagres ingen egen markør for hvor brukeren er.

---

## F10 – `slett_emne` sletter i feil rekkefølge, og sletting under generering (Middels)

**Berører:** AD-9, AD-14, FR-6

**Hullet:** AD-14 sier «sletter filene på disken *og deretter* emnet i én operasjon». Filsletting kan ikke rulles tilbake. Feiler databasedelen, er filene borte mens notatene står igjen, og kan aldri brukes til en ny quiz (FR-8, FR-15).

**Par A – rekkefølgen:**

- **Story A (`slett_emne`)** gjør `for n in notater: os.remove(n.fil.path)` og deretter `emne.delete()` i `atomic`, akkurat som AD-14 beskriver.
- **Story B (steget `lager`)** har åpen skrivetransaksjon eller lås (se F6) i et annet vindu.
- **Resultat:** `emne.delete()` får «database is locked» og ruller tilbake. Filene er slettet, men notatene finnes. «Lag quiz» og «Prøv igjen» feiler for alltid med en `FileNotFoundError` som ikke er en av feilkodene i AD-10, altså en 500-feil.

**Par B – emnet slettes mens en generering pågår:**

- **Story C (steget `sjekker`)** har `jobb` i minnet og lagrer `Quiz(notat=jobb.notat, …)`.
- **Story A** sletter emnet i en annen fane mens KI-kallet pågår.
- **Resultat:** Lagringen gir en FK-feil, eller `les_fil` gir `FileNotFoundError` og en 500-feil, og kjeden henger i HTMX fordi 404/500 ikke byttes inn som standard.

**Foreslått Rule (strammet AD-14):**

> `slett_emne(emne)` samler filstiene, sletter emnet med cascade i `transaction.atomic` og sletter filene i `transaction.on_commit`. Filer som mangler, ignoreres. Steg-endepunktet gir et sluttfragment (ingen ny trigger) med meldingen «Notatet finnes ikke lenger» når jobben eller notatet ikke finnes, i stedet for 404. `ki.les_fil` gjør `FileNotFoundError` om til `KIFeil("api_feil")`, slik at alle feil havner i AD-10.

---

## F11 – Seed-kommandoen og testmodus (Middels)

**Berører:** AD-1, AD-9, AD-12, FR-28, FR-30

**Hullet:** AD-1 sier at seed bruker de samme tjenestene. Men genereringstjenesten i AD-9 er bare beskrevet som HTTP-steg. AD-12 sier at «testene kjører alltid i testmodus», men sier ikke noe om seed.

**Par A – hvordan seed lager quizer:**

- **Story A (seed)** kaller `ki.generer` og `ki.sjekk` direkte og lagrer `Quiz` selv, fordi det ikke finnes en synkron tjeneste. Det bryter AD-1 («bare tjenester oppretter `Quiz`»), men utvikleren mener det er tillatt fordi seed «ikke er et view».
- **Story B (`services/generering`)** innfører regler ved lagring av quizen (nøyaktig ett riktig alternativ, `modell`, `prompt_versjon`, `jobb`).
- **Resultat:** Testbrukerens quizer mangler felt som resten av appen forventer, for eksempel `jobb` (F4), eller de får ikke de samme valideringene.

**Par B – seed med API-nøkkel:**

- **Story A** følger AD-12: «bare `ki` vet om testmodus».
- **Resultat:** Har sensor lagt inn sin egen nøkkel (FR-30) før `seed_testdata` kjøres, kaller seed det ekte API-et. Testdataene blir da ikke de samme som i README-en, og kommandoen kan bruke mange minutter eller feile. Kjøres seed to ganger, krasjer kommandoen på unik e-post.

**Foreslått Rule (ny AD-20 – Seed):**

> `services.generering.generer_synkront(notat, vanskelighetsgrad, antall) -> Quiz` kjører de samme stegfunksjonene etter hverandre, og brukes av seed og tester. Seed kjører alltid i testmodus via `ki.tving_testmodus()` (en kontekstbehandler i `ki`, så AD-12 gjelder fortsatt). Seed lager notater via samme opplastingstjeneste som brukere (`services.notater.last_opp`), med filer fra `testdokumenter/`. Seed svarer med svar som ligger fast (bestemt ut fra `er_riktig`) via `lagre_svar` og `lever_okt`. Kommandoen kan kjøres flere ganger uten feil: finnes testbrukeren, slettes emnene hens via `slett_emne` før de lages på nytt. Testbrukeren har `vilkar_godtatt` satt.

---

## F12 – `Bruker` og `username`, og store og små bokstaver i e-post (Middels)

**Berører:** AD-15, FR-1, FR-2

**Hullet:** `AbstractUser` har feltet `username` (unikt og påkrevd). AD-15 sier at `USERNAME_FIELD` er e-post, men ikke at `username` skal fjernes eller hvem som fyller det ut. Standardmanageren `UserManager.create_user(username, email, password)` krever `username`.

**Par:**

- **Story A (registrering)** bruker en `ModelForm` med `email` og passord. `username` blir `""`.
- **Story B (seed)** kaller `Bruker.objects.create_user(email=…, password=…)`.
- **Resultat:** Den andre brukeren som registrerer seg, får `IntegrityError` på `username=""`, altså en 500-feil i stedet for feilmeldingen i FR-1. B får `TypeError` (mangler `username`). I tillegg normaliserer `normalize_email` bare domenet, så `Ola@uib.no` og `ola@uib.no` blir to kontoer, og innlogging med «feil» skrivemåte avvises med samme melding som feil passord (FR-2).

**Foreslått Rule (strammet AD-15):**

> `Bruker` setter `username = None`, `USERNAME_FIELD = "email"`, `REQUIRED_FIELDS = []` og har en egen `BrukerManager` med `create_user(email, password)` og `create_superuser(email, password)`. E-post lagres alltid med små bokstaver (`email.strip().lower()` i manageren og i skjemaene for registrering og innlogging).

---

## F13 – Unikt emnenavn via ModelForm uten `eier` (Lav)

**Berører:** AD-1, FR-4, FR-5

**Par:**

- **Story A (modeller)** legger `UniqueConstraint(fields=["eier", "navn"])` på `Emne`.
- **Story B (opprette eller gi nytt navn til emne)** bruker `EmneForm(fields=["navn"])` rett i viewet, som AD-1 tillater, og setter `eier` etter `is_valid()`.
- **Resultat:** Django hopper over valideringen av en constraint når et av feltene ikke er med i skjemaet. Et duplikat gir `IntegrityError` og en 500-feil i stedet for feilmeldingen ved feltet (FR-4, konvensjonen om feilmeldinger).

**Foreslått Rule (tillegg til AD-1):**

> Skjemaer for `Emne` får `eier` i konstruktøren og sjekker selv at navnet er unikt hos eieren i `clean_navn` (uten å skille mellom store og små bokstaver), med tekst fra `feilmeldinger.py`. Constrainten i databasen er bare en sikring i bunnen.

---

## F14 – Hvordan filen lagres på `Notat` (Lav)

**Berører:** AD-1, AD-14, FR-8, strukturfrøet (`media/notater/<bruker-id>/<uuid>.<endelse>`)

**Par:**

- **Story A (opplasting)** bruker `Notat.fil = FileField(upload_to=…)` og `form.save()` i viewet. Django skriver filen til disk, men utenfor tjenestelaget (brudd på AD-1 som ingen merker).
- **Story B (`slett_emne`, `ki.les_fil`)** forventer en `CharField sti` relativt til `MEDIA_ROOT`.
- **Resultat:** `n.sti` mot `n.fil.path`. Ingen av dem tar vare på det opprinnelige filnavnet, som notatsiden trenger for å vise notatet.

**Foreslått Rule (tillegg til AD-14):**

> `Notat` har `fil = FileField(upload_to=sti_for_notat)` (gir `notater/<eier_id>/<uuid4><endelse>`), `originalnavn`, `filtype` (`pdf` | `docx` | `txt`, bestemt ved opplasting) og `storrelse`. Notater opprettes bare av `services.notater.last_opp(emne, opplastet_fil)`, som sjekker vilkår, størrelse og format. `ki.les_fil` får `notat.fil.path`.

---

## Forkastet som teoretisk

- **Samtidige brukere som skriver til samme rad:** Data er per bruker, og appen kjøres lokalt. To faner hos samme bruker er derimot tatt med (F3, F4).
- **Endring av vanskelighetsgrad eller tekst på et spørsmål etter lagring:** Ingen funksjon i v1 endrer spørsmål.
- **Sletting av enkeltnotat eller -quiz som etterlater feilbankrader:** AD-14 forbyr det, og FR-6 og FR-10 bekrefter.
- **Testmodus slås av eller på mens appen kjører:** `.env` leses ved oppstart, og en blanding av mock-quizer og ekte quizer er ufarlig fordi `forhandslagret` og `modell` er lagret per quiz (F5).
- **Fasiten lekker ved at brukeren prøver seg fram gjennom nye forsøk på samme quiz:** Det følger av PRD-en (FR-20) og er ikke et arkitekturhull.
- **HTMX-svar som følger en omdirigering og legger en hel side inn i fragmentet:** Det er en implementasjonsdetalj som konvensjonen om `_<navn>.html`-fragmenter allerede dekker, hvis viewet sjekker `HX-Request`.
- **Spørsmål som går igjen i flere quizer og telles dobbelt:** AD-5 bestemmer dette eksplisitt.
