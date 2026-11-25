"""
Lager de fem testdokumentene i `testdokumenter/` (FR-9, FR-12).

Innholdet er korte forelesningsnotater om webutvikling, skrevet av gruppa G82
(CC BY 4.0, se `testdokumenter/KILDER.md`). Kjør fra prosjektroten:

    uv run --with reportlab==5.1.1 --with pillow==13.0.0 scripts/lag_testdokumenter.py

`--with` gjør at verktøyene bare trengs her, og `uv.lock` endres ikke.
Filene lages likt hver gang (faste datoer, fast tilfeldig frø), så hashene i
mock-svarene fra story 2.2 holder så lenge innholdet og versjonene er de samme.
Endres en fil, må mock-svarene lages på nytt.
"""

import io
import random
import textwrap
import zipfile
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

import docx
import reportlab
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab import rl_config
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

MAPPE = Path(__file__).resolve().parent.parent / "testdokumenter"
FORFATTER = "Gruppe G82"
FAST_DATO = (2026, 11, 25, 12, 0, 0)

# ---------------------------------------------------------------------------
# Innhold. Enkel markering: «# » er tittel, «## » er overskrift, «- » er punkt,
# «---» er sideskift, tom linje skiller avsnitt.
# ---------------------------------------------------------------------------

HTML_NOTAT = """
# HTML: struktur og semantikk
Webutvikling, forelesning 2. Notater skrevet av gruppe G82.

## 1. Hva er HTML?
HTML står for HyperText Markup Language. Det er språket som beskriver strukturen
i en nettside: hva som er overskrifter, avsnitt, lenker, bilder og skjemaer.
HTML er ikke et programmeringsspråk, men et markeringsspråk. Det sier hva
innholdet er, ikke hvordan det skal se ut eller hvordan siden skal oppføre seg.

Tim Berners-Lee laget den første versjonen av HTML ved CERN rundt 1991, sammen
med HTTP og den første nettleseren. Tidlig HTML hadde bare noen få elementer,
som overskrifter, avsnitt og lenker. Senere kom tabeller, skjemaer og bilder.

I dag utvikles HTML som en levende standard, HTML Living Standard, som
vedlikeholdes av WHATWG. Det betyr at det ikke lenger kommer store
versjonsnummer. Standarden oppdateres fortløpende når nettleserne blir enige om
nye funksjoner. Når folk sier HTML5, mener de som regel denne moderne HTML-en.

En nettside består vanligvis av tre lag: HTML for struktur, CSS for
presentasjon og JavaScript for oppførsel. Å holde disse lagene adskilt gjør
koden enklere å vedlikeholde, og gjør det lettere å endre utseendet uten å røre
innholdet.
---
## 2. Dokumentstrukturen
Alle HTML-dokumenter har den samme grunnstrukturen. Den første linjen er
dokumenttypen, <!DOCTYPE html>. Den forteller nettleseren at siden skal tolkes
etter moderne standard og ikke i den gamle «quirks mode».

Deretter kommer rotelementet <html>. Det bør ha attributtet lang, for eksempel
lang="nb" for norsk bokmål. Språket brukes blant annet av skjermlesere til å
velge riktig uttale, og av nettleseren til orddeling og stavekontroll.

Inne i <html> ligger to deler. Elementet <head> inneholder informasjon om
dokumentet som ikke vises direkte på siden: tegnsettet med <meta charset="utf-8">,
viewport-innstillingen for mobil, tittelen i <title> og lenker til stilark med
<link>. Tittelen vises i fanen i nettleseren og i søkeresultater, så den bør
beskrive siden kort og presist.

Elementet <body> inneholder alt som vises på siden. Det er her overskrifter,
tekst, bilder, lenker og skjemaer hører hjemme. Et dokument har nøyaktig ett
<head> og ett <body>.

Tegnsettet bør alltid være UTF-8. Da kan siden vise æ, ø og å, og tegn fra
andre språk, uten problemer. Meta-elementet for tegnsett bør stå tidlig i
<head>, fordi nettleseren må vite tegnsettet før den leser resten.
---
## 3. Elementer, tagger og attributter
Et HTML-element består som regel av en starttagg, innhold og en sluttagg. I
<p>Hei</p> er <p> starttaggen, Hei er innholdet og </p> er sluttaggen.
Sluttaggen har en skråstrek foran navnet.

Noen elementer er tomme og har ingen sluttagg, fordi de ikke kan ha innhold.
Eksempler er <img> for bilder, <br> for linjeskift, <hr> for tematisk skille,
<input> for skjemafelt og <meta>. I eldre XHTML skrev man <br />, men i HTML er
skråstreken valgfri.

Elementer kan nøstes inni hverandre, men de må lukkes i motsatt rekkefølge av
den de ble åpnet i. <p><strong>Viktig</strong></p> er riktig, mens
<p><strong>Viktig</p></strong> er feil nøsting.

Attributter gir ekstra informasjon om et element og skrives i starttaggen som
navn="verdi". Attributtet id gir elementet et unikt navn på siden, og samme id
skal bare brukes én gang. Attributtet class kan brukes på mange elementer og
brukes ofte til å velge elementer i CSS. Noen attributter er boolske, som
required og disabled. Der er det nok at attributtet står der.

Tagg-navn er ikke følsomme for store og små bokstaver, men det er vanlig å
skrive dem med små bokstaver.
---
## 4. Overskrifter og tekst
HTML har seks nivåer av overskrifter, fra <h1> til <h6>. <h1> er den viktigste
og beskriver hele siden. Det er vanlig å ha én <h1> per side. Underoverskrifter
får <h2>, deres underoverskrifter <h3>, og så videre. Man bør ikke hoppe over
nivåer, for eksempel fra <h2> rett til <h4>.

Overskriftene danner en innholdsfortegnelse for siden. Mange skjermleserbrukere
hopper mellom overskriftene for å få oversikt. Derfor skal man aldri velge
overskriftsnivå ut fra hvor stor teksten blir. Størrelsen styres med CSS.

Vanlig brødtekst skrives i avsnitt med <p>. Nettleseren legger litt luft over
og under hvert avsnitt. Flere mellomrom og linjeskift i kildekoden slås sammen
til ett mellomrom når siden vises.

For å fremheve tekst finnes <em> og <strong>. <em> betyr trykk eller betoning,
og vises vanligvis i kursiv. <strong> betyr at teksten er spesielt viktig, og
vises vanligvis i fet skrift. Elementene <i> og <b> gir kursiv og fet uten
denne betydningen, og brukes for eksempel til fremmedord eller nøkkelord.

Andre nyttige tekstelementer er <blockquote> for lengre sitater, <code> for kode
i løpende tekst, <pre> for forhåndsformatert tekst der mellomrom beholdes, og
<abbr> for forkortelser.
---
## 5. Lenker og stier
Lenker lages med elementet <a>, som står for anchor. Attributtet href sier hvor
lenken går. Teksten mellom taggene er det brukeren klikker på. Lenketeksten bør
beskrive målet. «Les mer om skjemaer» er bedre enn «klikk her», fordi den gir
mening også når den leses alene, slik skjermlesere ofte gjør.

En absolutt URL inneholder hele adressen med protokoll og domene, for eksempel
https://www.example.com/om.html. En relativ sti er relativ til siden lenken står
på. Stien om.html peker til en fil i samme mappe. Stien ../index.html går én
mappe opp. En sti som begynner med skråstrek, som /kontakt/, er relativ til
roten av nettstedet.

En lenke kan også peke til et sted på samme side. Da bruker man et fragment med
emneknagg, for eksempel href="#skjemaer". Målet er elementet med id="skjemaer".

Lenker med mailto: åpner e-postprogrammet, og lenker med tel: kan ringe et
nummer på mobil.

Attributtet target="_blank" åpner lenken i en ny fane. Det bør brukes sparsomt,
fordi det kan forvirre brukeren og tar fra brukeren valget. Hvis det brukes, bør
det stå i lenketeksten at lenken åpnes i en ny fane.
---
## 6. Bilder og media
Bilder settes inn med det tomme elementet <img>. Attributtet src sier hvor
bildefilen ligger, og attributtet alt gir en tekstlig erstatning for bildet.
Alt-teksten leses opp av skjermlesere og vises hvis bildet ikke kan lastes.

Alt-teksten skal beskrive hva bildet formidler i sammenhengen, ikke bare hva det
er. Et rent dekorativt bilde skal ha tom alt-tekst, alt="", slik at
skjermlesere hopper over det. Mangler alt helt, leser mange skjermlesere opp
filnavnet i stedet.

Det er lurt å sette width og height på bilder. Da kan nettleseren sette av
riktig plass før bildet er lastet, og siden hopper ikke når bildet dukker opp.

Elementet <figure> brukes for innhold som et bilde, et diagram eller et
kodeeksempel som henvises til fra teksten. Med <figcaption> får figuren en
bildetekst.

Video og lyd settes inn med <video> og <audio>. Attributtet controls viser
nettleserens egne knapper for avspilling og volum. Med elementet <source> kan
man tilby flere filformater, og nettleseren velger det første den støtter.
Video med tale bør ha teksting, som legges til med elementet <track>.
---
## 7. Lister og tabeller
HTML har tre typer lister. En punktliste lages med <ul>, unordered list, og
brukes når rekkefølgen ikke betyr noe. En nummerert liste lages med <ol>,
ordered list, og brukes når rekkefølgen betyr noe, som i en oppskrift. Hvert
punkt i begge listetypene er et <li>-element. Lister kan nøstes ved å legge en
ny liste inni et <li>.

Den tredje typen er beskrivelseslisten <dl>. Den består av par med begrep i <dt>
og beskrivelse i <dd>, og passer for ordlister.

Tabeller lages med <table> og skal bare brukes til data i rader og kolonner,
ikke til å lage sideoppsett. En rad er <tr>, og en celle er <td>.
Overskriftsceller lages med <th>. Attributtet scope="col" eller scope="row"
sier om overskriften gjelder en kolonne eller en rad, slik at skjermlesere kan
lese opp riktig overskrift sammen med hver celle.

Radene kan grupperes i <thead>, <tbody> og <tfoot>. Elementet <caption> gir
tabellen en tittel og skal stå rett etter starttaggen til <table>.

Celler kan slås sammen med colspan og rowspan, men kompliserte tabeller er
vanskelige å lese med skjermleser. Ofte er det bedre å dele dem i flere enkle
tabeller.
---
## 8. Skjemaer
Skjemaer lar brukeren sende data til en tjener. Elementet <form> har
attributtet action, som sier hvor dataene sendes, og method, som er GET eller
POST. Med GET legges dataene i adressen som en spørrestreng, og det passer for
søk. Med POST sendes dataene i selve forespørselen, og det brukes når noe skal
lagres eller endres.

Det vanligste skjemafeltet er <input>. Attributtet type bestemmer hva slags
felt det er: text, email, password, number, date, checkbox, radio og file er
noen eksempler. Riktig type gir bedre tastatur på mobil og innebygd sjekk i
nettleseren. Lengre tekst skrives i <textarea>, og nedtrekkslister lages med
<select> og <option>.

Hvert felt skal ha en ledetekst med <label>. Attributtet for på etiketten
kobles til feltets id. Da leser skjermleseren opp etiketten, og et klikk på
etiketten flytter fokus til feltet. Plassholdertekst i placeholder er ikke en
erstatning for en etikett.

Radioknapper og avkrysningsbokser som hører sammen, grupperes med <fieldset>,
og gruppen får en overskrift med <legend>. Attributtet required gjør feltet
påkrevd, og nettleseren sjekker det før skjemaet sendes. Sjekken i nettleseren
er likevel bare en hjelp. Tjeneren må alltid sjekke dataene på nytt.

Skjemaet sendes med <button type="submit">.
---
## 9. Semantiske elementer
Semantisk HTML betyr å velge elementer etter hva innholdet er. Moderne HTML har
egne elementer for de vanlige delene av en side. <header> er toppen av siden
eller av en seksjon. <nav> inneholder hovednavigasjonen. <main> er hovedinnholdet
og skal bare finnes én gang per side. <footer> er bunnen, ofte med kontaktinfo.

<article> brukes for innhold som gir mening alene, som et blogginnlegg eller en
nyhetssak. <section> er en tematisk del av et dokument, og bør som regel ha en
overskrift. <aside> er innhold som bare er løst knyttet til resten, som en
faktaboks.

Elementene <div> og <span> har ingen betydning i seg selv. <div> er et blokkelement
og <span> et linjeelement. De brukes når ingen semantiske elementer passer,
for eksempel bare for å kunne style en del av siden.

Semantikk er viktig av flere grunner. Skjermlesere bruker landemerkene <header>,
<nav>, <main> og <footer> til å hoppe rett til en del av siden. Søkemotorer
forstår innholdet bedre. Og koden blir lettere å lese for andre utviklere. En
knapp skal derfor være en <button> og ikke en <div> med klikkhendelse, fordi
<button> kan nås med tastaturet og annonseres riktig.
---
## 10. Validering og god praksis
Nettlesere er tilgivende. De prøver å vise siden selv om HTML-en har feil, som
manglende sluttagger eller feil nøsting. Hver nettleser kan likevel rette feilen
på sin egen måte, så resultatet blir uforutsigbart. Derfor bør man validere
koden, for eksempel med W3Cs validator på validator.w3.org.

Kommentarer skrives mellom <!-- og -->. De vises ikke på siden, men alle kan se
dem i kildekoden. Hemmeligheter som passord skal derfor aldri stå i kommentarer.

Noen enkle regler gir god HTML:
- Bruk innrykk, slik at nøstingen blir synlig.
- Skriv tagger og attributter med små bokstaver, og sett verdier i anførselstegn.
- Velg elementer etter betydning, ikke utseende.
- Gi alle bilder en passende alt-tekst, og alle skjemafelt en etikett.
- Sett lang på <html> og UTF-8 som tegnsett.
- Hold struktur, presentasjon og oppførsel adskilt i HTML, CSS og JavaScript.

Til slutt: test siden med tastaturet alene. Kan du nå alle lenker og knapper
med Tab, og ser du hvor fokuset er? Da har du kommet langt.
"""

CSS_LYSBILDER = """
# CSS-layout: flexbox og grid
Webutvikling, forelesning 4

Gruppe G82
---
## Boksmodellen
- Hvert element er en boks: innhold, padding, border og margin
- padding er luft innenfor kanten, margin er luft utenfor
- Standard: width gjelder bare innholdet
- box-sizing: border-box tar med padding og border i width
---
## display
- block: ny linje, tar hele bredden (div, p, h1)
- inline: flyter i teksten, width virker ikke (span, a, em)
- inline-block: i teksten, men med width og height
- none: elementet vises ikke og tar ingen plass
---
## Flexbox: grunnbegreper
- display: flex settes på forelderen, flex-beholderen
- Barna blir flex-elementer
- Hovedakse og kryssakse
- flex-direction: row (standard) eller column
---
## Flexbox: justering
- justify-content: fordeler langs hovedaksen
- Verdier: flex-start, center, space-between, space-around
- align-items: plasserer langs kryssaksen
- gap: mellomrom mellom elementene
- flex-wrap: wrap lar elementene gå over flere linjer
---
## Flexbox: størrelse
- flex-grow: hvor mye et element vokser av ledig plass
- flex-shrink: hvor mye det krymper når plassen er for liten
- flex-basis: startstørrelsen før vekst og krymping
- flex: 1 betyr at alle deler ledig plass likt
---
## Grid: grunnbegreper
- display: grid gir et rutenett i to dimensjoner
- grid-template-columns: 200px 1fr 2fr
- fr er en brøkdel av den ledige plassen
- repeat(3, 1fr) gir tre like kolonner
---
## Grid: plassering
- grid-column: 1 / 3 strekker et element over to kolonner
- grid-template-areas gir navn til områder
- minmax(200px, 1fr): aldri smalere enn 200px
- repeat(auto-fit, minmax(200px, 1fr)) tilpasser antall kolonner
---
## Flexbox eller grid?
- Flexbox: én dimensjon, en rad eller en kolonne
- Grid: to dimensjoner, rader og kolonner samtidig
- Flexbox for innhold som bestemmer størrelsen, som en meny
- Grid for sideoppsett
- De kan godt kombineres
---
## Responsiv design
- Mobil først: lag for liten skjerm, utvid for stor
- Media query: @media (min-width: 600px) { ... }
- Relative enheter: rem, em, %, vw og vh
- Husk viewport-meta i head
---
## Oppsummering
- Boksmodellen og box-sizing styrer størrelser
- Flexbox for én akse, grid for to
- fr, minmax og auto-fit gjør grid fleksibelt
- Media queries tilpasser oppsettet til skjermen
"""

HTTP_NOTAT = """
# HTTP: forespørsler og svar
Forelesningsnotater, webutvikling uke 6. Gruppe G82.

## Klient og tjener
HTTP (HyperText Transfer Protocol) er protokollen nettleseren og tjeneren
snakker sammen med. Klienten, ofte nettleseren, sender en forespørsel, og
tjeneren sender et svar. HTTP er tilstandsløs: hver forespørsel står alene, og
tjeneren husker ingenting mellom to forespørsler. For å huske for eksempel en
innlogging brukes informasjonskapsler (cookies). Tjeneren sender dem med
headeren Set-Cookie, og nettleseren sender dem tilbake i headeren Cookie.

## Delene i en URL
I https://www.example.com:443/sok?q=html#treff er https skjemaet, www.example.com
verten, 443 porten, /sok stien, q=html spørrestrengen og treff fragmentet.
Fragmentet sendes aldri til tjeneren. Det brukes bare i nettleseren.

## Metoder
- GET henter en ressurs og skal ikke endre noe.
- POST sender data, for eksempel fra et skjema, og lager ofte noe nytt.
- PUT erstatter en ressurs, og PATCH endrer deler av den.
- DELETE sletter en ressurs.
- HEAD er som GET, men gir bare headerne.

GET og HEAD er trygge, det vil si at de ikke endrer noe på tjeneren. GET, PUT og
DELETE er idempotente: å sende samme forespørsel flere ganger gir samme
resultat som å sende den én gang. POST er verken trygg eller idempotent.

## Statuskoder
Svaret starter med en statuskode på tre sifre. Det første sifferet sier hvilken
gruppe koden hører til.

- 1xx: informasjon.
- 2xx: vellykket. 200 OK og 201 Created.
- 3xx: omdirigering. 301 Moved Permanently, 302 Found og 304 Not Modified.
- 4xx: feil hos klienten. 400 Bad Request, 401 Unauthorized (ikke logget inn),
  403 Forbidden (ikke tilgang) og 404 Not Found.
- 5xx: feil hos tjeneren. 500 Internal Server Error og 503 Service Unavailable.

Ved omdirigering står den nye adressen i headeren Location.

## Headere
Både forespørsler og svar har headere, som er navn og verdi. Content-Type sier
hva slags innhold det er, for eksempel text/html eller application/json. Accept
sier hva klienten kan ta imot. Cache-Control styrer hvor lenge svaret kan
mellomlagres. User-Agent beskriver klienten.

## Et eksempel
En enkel forespørsel ser slik ut:

    GET /index.html HTTP/1.1
    Host: www.example.com
    Accept: text/html

Etter headerne kommer en tom linje, og deretter eventuelt en kropp. Svaret
starter med statuslinjen HTTP/1.1 200 OK, så headerne, en tom linje og selve
HTML-dokumentet.

## HTTPS
HTTPS er HTTP over TLS. Forbindelsen krypteres, slik at ingen underveis kan lese
eller endre dataene. Tjeneren viser et sertifikat som beviser at den er den den
sier den er. HTTP bruker port 80 som standard, HTTPS port 443. I dag bør alle
nettsteder bruke HTTPS.

## Versjoner
HTTP/1.1 kom i 1997 og er tekstbasert. HTTP/2 kom i 2015. Den er binær og kan
sende mange forespørsler samtidig over én forbindelse (multipleksing). HTTP/3
ble standard i 2022 og går over QUIC, som bygger på UDP i stedet for TCP.
"""

WCAG_NOTAT = """
# Universell utforming av nettsider
Webutvikling, forelesning 7. Notater skrevet av gruppe G82.

## Hva og hvorfor
Universell utforming betyr at en løsning kan brukes av så mange som mulig, uten
at den må tilpasses den enkelte. På nett handler det om at personer med nedsatt
syn, hørsel, motorikk eller kognisjon skal kunne bruke siden på lik linje med
andre. Mange har nytte av det: en som bruker mobil i sterkt sollys, en med
brukket arm eller en som leser på et annet språk enn morsmålet.

I Norge er universell utforming av IKT lovpålagt gjennom likestillings- og
diskrimineringsloven og forskriften om universell utforming av IKT-løsninger.
Tilsynet med forskriften ligger hos Digitaliseringsdirektoratet (Digdir).

## WCAG
Kravene bygger på WCAG, Web Content Accessibility Guidelines, fra W3C. WCAG 2.2
kom i 2023. Retningslinjene har tre nivåer: A, AA og AAA. A er minimumskravene,
og AA er nivået lovverket i Norge og EU viser til. AAA er det strengeste nivået
og kreves sjelden for hele nettsteder.

## De fire prinsippene
WCAG er bygget på fire prinsipper, ofte forkortet POUR:

- Mulig å oppfatte: informasjon skal kunne oppfattes med minst én sans, for eksempel med tekstalternativ til bilder og teksting av video.
- Mulig å betjene: alt skal kunne brukes med tastatur, og brukeren skal ha nok tid.
- Forståelig: tekst og betjening skal være forutsigbar og lett å forstå.
- Robust: innholdet skal fungere med ulike nettlesere og hjelpemidler, som skjermlesere.

## Vanlige krav i praksis
- Bilder som formidler noe, skal ha en alt-tekst (suksesskriterium 1.1.1).
- Kontrasten mellom tekst og bakgrunn skal være minst 4,5:1 for vanlig tekst og 3:1 for stor tekst (1.4.3).
- Farge skal ikke være eneste måte å vise informasjon på, for eksempel en feil i et skjema (1.4.1).
- All funksjonalitet skal kunne brukes med tastaturet (2.1.1), og fokus skal være synlig (2.4.7).
- Skjemafelt skal ha ledetekster (3.3.2), og feil skal beskrives i tekst (3.3.1).
- Siden skal ha en beskrivende tittel (2.4.2) og riktig språk i lang-attributtet (3.1.1).
- Klikkflater skal være minst 24 x 24 CSS-piksler (2.5.8, nytt i WCAG 2.2).

## Skjermlesere og ARIA
En skjermleser leser opp innholdet på siden med syntetisk tale eller viser det
på en leselist i punktskrift. Eksempler er NVDA og JAWS på Windows og VoiceOver
på Mac og iPhone. Skjermleseren bruker strukturen i HTML-en: overskrifter,
landemerker, lister og etiketter.

ARIA (Accessible Rich Internet Applications) er attributter som gir ekstra
informasjon til hjelpemidler, som aria-label, aria-describedby og aria-live.
Den første regelen for ARIA er å la være å bruke det når et vanlig HTML-element
gjør jobben. En <button> er alltid bedre enn en <div> med role="button".

## Testing
Automatiske verktøy som WAVE, axe og Lighthouse finner bare en del av feilene,
anslagsvis 30 til 40 prosent. Manuell testing er derfor nødvendig. Prøv å bruke
siden bare med tastaturet, zoom til 200 prosent, og test med en skjermleser.
Det beste er å teste med ekte brukere.
"""

JS_NOTAT = """
JavaScript and the DOM
Web development, lecture 5. Notes written by group G82.

1. What is the DOM?
The Document Object Model (DOM) is the browser's representation of an HTML
page as a tree of objects. Every element, attribute and piece of text becomes a
node in the tree. The document object is the root, and document.documentElement
is the <html> element. JavaScript can read and change the tree, and the browser
updates the page on screen right away.

The DOM is not the same as the HTML source. If the HTML contains errors, the
browser fixes them when it builds the tree. And when a script changes the DOM,
the source file stays the same. To see the current DOM, open the Elements panel
in the browser's developer tools.

2. Loading scripts
Scripts are added with the <script> element. A script in <head> runs before the
body has been parsed, so it cannot find elements that do not exist yet. The
attribute defer tells the browser to download the script in parallel and run it
after the whole document has been parsed, in the order the scripts appear. The
attribute async also downloads in parallel, but runs the script as soon as it
is ready, in any order. Scripts with type="module" are deferred by default.

3. Finding elements
document.getElementById("menu") returns the element with that id, or null.
document.querySelector(".card") returns the first element that matches a CSS
selector, and document.querySelectorAll("li") returns all matches as a static
NodeList. The older getElementsByClassName returns a live HTMLCollection that
updates when the document changes. querySelector and querySelectorAll are the
most flexible, because they accept any CSS selector.

4. Changing content
textContent gets or sets the text of an element. innerHTML gets or sets the
HTML inside it. innerHTML is risky with user input: if a user can put
<script> or <img onerror=...> into the string, the code may run. This is called
cross-site scripting (XSS). Use textContent for text from users.

Attributes are changed with setAttribute and read with getAttribute. Classes
are best handled with classList: classList.add, classList.remove,
classList.toggle and classList.contains. Inline styles can be set through the
style property, for example element.style.display = "none", but it is usually
cleaner to toggle a class and keep the styling in CSS.

5. Creating and removing elements
document.createElement("li") creates a new element that is not yet part of the
page. It is added with append, prepend, before or after (or the older
appendChild). element.remove() takes an element out of the tree. Each change
to the DOM can make the browser recalculate the layout, so when adding many
elements it is faster to build them in a DocumentFragment and insert the
fragment once.

6. Events
addEventListener("click", handler) runs the handler function every time the
event happens. Common events are click, input, change, submit, keydown and
DOMContentLoaded. The handler receives an event object. event.target is the
element where the event started, and event.currentTarget is the element the
listener is attached to. event.preventDefault() stops the browser's default
action, such as following a link or submitting a form.

Events bubble: after an event fires on an element, it travels up through the
parents to the document. Event delegation uses this. Instead of adding a
listener to every list item, add one listener to the list and check
event.target. This also works for items added later. event.stopPropagation()
stops the bubbling, but it should be used with care.

7. Forms
The submit event fires on the <form>, not on the button. Calling
preventDefault in the handler lets a script send the data with fetch instead of
reloading the page. new FormData(form) collects all fields that have a name
attribute. The input event fires on every keystroke, while change fires when
the user leaves the field after changing it.

8. Accessibility
Use real <button> elements for things that can be clicked. They can be reached
with the Tab key and activated with Enter and Space without extra code. When a
script updates part of the page, screen readers may not notice. A region with
aria-live="polite" makes the screen reader announce the change when the user is
idle. After showing an error, move focus to it with element.focus() so keyboard
users know what happened.

9. Summary
The DOM is a live tree. Find nodes with querySelector, change them with
textContent and classList, react to the user with addEventListener, and use
event delegation for lists. Avoid innerHTML with user input.
"""


# ---------------------------------------------------------------------------
# Hjelpere
# ---------------------------------------------------------------------------


def blokker(kilde):
    """Deler markert tekst i (art, tekst).

    Art er tittel, overskrift, punkt, kode, avsnitt eller side. En linje med fire
    mellomroms innrykk er kode. En linje med to mellomroms innrykk etter et punkt
    hører til punktet.
    """
    resultat = []
    avsnitt = []

    def lukk():
        if avsnitt:
            resultat.append(("avsnitt", " ".join(avsnitt)))
            avsnitt.clear()

    for raa in textwrap.dedent(kilde).strip().splitlines():
        linje = raa.strip()
        if not linje:
            lukk()
        elif raa.startswith("    "):
            lukk()
            resultat.append(("kode", linje))
        elif raa.startswith("  ") and resultat and resultat[-1][0] == "punkt":
            resultat[-1] = ("punkt", resultat[-1][1] + " " + linje)
        elif linje == "---":
            lukk()
            resultat.append(("side", ""))
        elif linje.startswith("## "):
            lukk()
            resultat.append(("overskrift", linje[3:]))
        elif linje.startswith("# "):
            lukk()
            resultat.append(("tittel", linje[2:]))
        elif linje.startswith("- "):
            lukk()
            resultat.append(("punkt", linje[2:]))
        else:
            avsnitt.append(linje)
    lukk()
    return resultat


def deterministisk_zip(raa):
    """Skriver zip-filen på nytt med fast dato, slik at hashen blir den samme."""
    inn = zipfile.ZipFile(io.BytesIO(raa))
    ut_buffer = io.BytesIO()
    with zipfile.ZipFile(ut_buffer, "w", zipfile.ZIP_DEFLATED) as ut:
        for info in inn.infolist():
            ny = zipfile.ZipInfo(info.filename, date_time=FAST_DATO[:6])
            ny.compress_type = zipfile.ZIP_DEFLATED
            ny.create_system = 3  # Fast «Unix», ellers avhenger bytene av OS-et.
            ny.external_attr = 0o644 << 16
            ut.writestr(ny, inn.read(info.filename))
    return ut_buffer.getvalue()


# ---------------------------------------------------------------------------
# Tekst-PDF og lysbilde-PDF (reportlab)
# ---------------------------------------------------------------------------


def lag_pdf(sti, kilde, tittel, sidestorrelse, stiler):
    rl_config.invariant = 1  # Fast dato og dokument-ID.
    dokument = SimpleDocTemplate(
        str(sti),
        pagesize=sidestorrelse,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.2 * cm,
        title=tittel,
        author=FORFATTER,
        creator=FORFATTER,
    )
    flyt = []
    for art, tekst in blokker(kilde):
        if art == "side":
            flyt.append(PageBreak())
        elif art == "punkt":
            flyt.append(Paragraph(escape(tekst), stiler["punkt"], bulletText="•"))
        else:
            flyt.append(Paragraph(escape(tekst), stiler.get(art, stiler["avsnitt"])))
            if art == "tittel":
                flyt.append(Spacer(1, 0.3 * cm))
    dokument.build(flyt)


def lag_tekst_pdf(sti):
    stiler = {
        "tittel": ParagraphStyle(
            "tittel", fontName="Helvetica-Bold", fontSize=20, leading=26
        ),
        "overskrift": ParagraphStyle(
            "overskrift",
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=20,
            spaceAfter=10,
        ),
        "avsnitt": ParagraphStyle(
            "avsnitt", fontName="Times-Roman", fontSize=12, leading=17, spaceAfter=9
        ),
        "punkt": ParagraphStyle(
            "punkt",
            fontName="Times-Roman",
            fontSize=12,
            bulletFontSize=12,
            leading=17,
            leftIndent=18,
            spaceAfter=4,
        ),
    }
    lag_pdf(sti, HTML_NOTAT, "HTML: struktur og semantikk", A4, stiler)


def lag_lysbilde_pdf(sti):
    stiler = {
        "tittel": ParagraphStyle(
            "tittel",
            fontName="Helvetica-Bold",
            fontSize=40,
            leading=48,
            spaceBefore=120,
        ),
        "overskrift": ParagraphStyle(
            "overskrift",
            fontName="Helvetica-Bold",
            fontSize=32,
            leading=38,
            spaceAfter=24,
        ),
        "avsnitt": ParagraphStyle(
            "avsnitt", fontName="Helvetica", fontSize=22, leading=30
        ),
        "punkt": ParagraphStyle(
            "punkt",
            fontName="Helvetica",
            fontSize=22,
            bulletFontSize=22,
            leading=30,
            leftIndent=30,
            bulletIndent=6,
            spaceAfter=10,
        ),
    }
    lag_pdf(sti, CSS_LYSBILDER, "CSS-layout: flexbox og grid", landscape(A4), stiler)


# ---------------------------------------------------------------------------
# Skannet PDF (Pillow): sidene tegnes som bilder, uten tekstlag.
# ---------------------------------------------------------------------------

DPI = 150
SIDE = (1240, 1754)  # A4 ved 150 dpi.
MARG = 130


def bryt_linjer(tekst, font, bredde, tegner):
    linjer, linje = [], ""
    for ord_ in tekst.split():
        forsok = f"{linje} {ord_}".strip()
        if tegner.textlength(forsok, font=font) <= bredde:
            linje = forsok
        else:
            if linje:
                linjer.append(linje)
            linje = ord_
    if linje:
        linjer.append(linje)
    return linjer


def tegn_sider(kilde):
    # Bitstream Vera følger med reportlab og har æ, ø og å (Pillows standardfont har ikke det).
    fontmappe = Path(reportlab.__file__).parent / "fonts"
    fonter = {
        "tittel": ImageFont.truetype(fontmappe / "VeraBd.ttf", 40),
        "overskrift": ImageFont.truetype(fontmappe / "VeraBd.ttf", 29),
        "avsnitt": ImageFont.truetype(fontmappe / "Vera.ttf", 24),
    }
    sider = []
    side = tegner = None
    y = 0

    def ny_side():
        nonlocal side, tegner, y
        side = Image.new("L", SIDE, 255)
        tegner = ImageDraw.Draw(side)
        sider.append(side)
        y = MARG

    ny_side()
    bredde = SIDE[0] - 2 * MARG
    for art, tekst in blokker(kilde):
        if art == "side":
            ny_side()
            continue
        font = fonter.get(art, fonter["avsnitt"])
        innrykk = {"punkt": 34, "kode": 40}.get(art, 0)
        if art == "punkt":
            tekst = "-  " + tekst
        linjer = bryt_linjer(tekst, font, bredde - innrykk, tegner)
        hoyde = font.size + 12
        if art == "overskrift":
            y += 18
        if y + hoyde * min(len(linjer), 3) > SIDE[1] - MARG:
            ny_side()
        for nr, linje in enumerate(linjer):
            if y + hoyde > SIDE[1] - MARG:
                ny_side()
            # Punktet selv står i margen, resten av linjene rykkes inn.
            x = MARG if art == "punkt" and nr == 0 else MARG + innrykk
            tegner.text((x, y), linje, font=font, fill=25)
            y += hoyde
        y += {"punkt": 6, "kode": 0}.get(art, 16)
    return sider


def skann(side, tilfeldig):
    """Gjør en ren side om til noe som ligner en skanning: skrått, grått og støy."""
    vinkel = tilfeldig.uniform(-1.4, 1.4)
    side = side.rotate(vinkel, resample=Image.Resampling.BICUBIC, fillcolor=255)
    side = side.filter(ImageFilter.GaussianBlur(0.7))
    # Grått papir i stedet for helt hvitt.
    side = side.point(lambda v: min(v, 236))
    piksler = side.load()
    bredde, hoyde = side.size
    # Mørk kant fra skannerlokket langs venstre side.
    for x in range(14):
        for y in range(hoyde):
            piksler[x, y] = min(piksler[x, y], 70 + x * 8)
    # Støy: små prikker spredt over siden.
    for _ in range(9000):
        x, y = tilfeldig.randrange(bredde), tilfeldig.randrange(hoyde)
        piksler[x, y] = tilfeldig.randrange(90, 200)
    return side


def lag_skannet_pdf(sti):
    tilfeldig = random.Random(82)
    sider = [skann(s, tilfeldig) for s in tegn_sider(HTTP_NOTAT)]
    sider[0].save(
        sti,
        "PDF",
        save_all=True,
        append_images=sider[1:],
        resolution=DPI,
        quality=70,
        title="HTTP: forespørsler og svar (skannet)",
        author=FORFATTER,
        creator=FORFATTER,
        producer=FORFATTER,
        creationDate=None,
        modDate=None,
    )


# ---------------------------------------------------------------------------
# DOCX (python-docx) og TXT
# ---------------------------------------------------------------------------


def lag_docx(sti):
    dokument = docx.Document()
    for art, tekst in blokker(WCAG_NOTAT):
        if art == "tittel":
            dokument.add_heading(tekst, level=0)
        elif art == "overskrift":
            dokument.add_heading(tekst, level=1)
        elif art == "punkt":
            dokument.add_paragraph(tekst, style="List Bullet")
        else:
            dokument.add_paragraph(tekst)
    egenskaper = dokument.core_properties
    egenskaper.author = FORFATTER
    egenskaper.last_modified_by = FORFATTER
    egenskaper.title = "Universell utforming av nettsider"
    egenskaper.created = egenskaper.modified = datetime(*FAST_DATO)
    egenskaper.revision = 1
    buffer = io.BytesIO()
    dokument.save(buffer)
    sti.write_bytes(deterministisk_zip(buffer.getvalue()))


def lag_txt(sti):
    tekst = textwrap.dedent(JS_NOTAT).strip() + "\n"
    sti.write_bytes(tekst.encode("utf-8"))


DOKUMENTER = {
    "html-struktur-og-semantikk.pdf": lag_tekst_pdf,
    "css-layout-lysbilder.pdf": lag_lysbilde_pdf,
    "http-skannet.pdf": lag_skannet_pdf,
    "universell-utforming.docx": lag_docx,
    "javascript-og-dom.txt": lag_txt,
}


def main():
    MAPPE.mkdir(exist_ok=True)
    for navn, lag in DOKUMENTER.items():
        sti = MAPPE / navn
        lag(sti)
        print(f"{navn}: {sti.stat().st_size} byte")


if __name__ == "__main__":
    main()
