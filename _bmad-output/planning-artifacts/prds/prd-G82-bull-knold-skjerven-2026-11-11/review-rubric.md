# Kvalitetssjekk av PRD (11.11.2026)

## Samlet vurdering
PRD-en er klar til å brukes for UX, arkitektur og stories. Kravene har testbare konsekvenser, og læringssløyfen (quiz → feilbank → lært → dekningsgrad) er den røde tråden. Svakest står testdokumentene: FR-9, SM-2 og SM-4 avhenger av et sett som ikke er definert.

| Dimensjon | Vurdering |
|---|---|
| Beslutningsklar | God. Beslutningene og det som er valgt bort, står eksplisitt (kap. 7.2, addendum). |
| Innhold fremfor fasade | God. Én persona (Tore) og sensor, og begge driver krav. NFR-ene har konkrete grenser. |
| Strategisk sammenheng | God. Motmålene beskytter tesen om en «stram sløyfe». |
| Tydelig ferdig | God. Alle FR-er har minst én testbar konsekvens. |
| Ærlig omfang | God. Ikke-mål og videre arbeid er tydelige. 3 åpne spørsmål, ingen blokkerer. |
| Nyttig videre | God. Ordlisten brukes konsekvent, og ID-ene er sammenhengende (FR-1–30, UJ-1–5, SM-1–6, SM-C1–3). |
| Riktig form | God. Brukerreiser passer et produkt med mye UX. |

## Funn
- **høy** Testdokumentene er ikke definert (§3, FR-9, SM-2, SM-4). *Forslag:* fastsette et minimumssett. → Gruppa avgjør.
- **middels** Det står ikke om en quiz kan slettes (§4.4). → Gruppa avgjør.
- **lav** «Studenten» og «brukeren» brukes om hverandre (§1–2 mot §4). *Rettet:* forklart i ordlisten.
- **lav** I FR-22 ble ordet «forsøk» brukt om en økt med «Øv på feil», som er i strid med ordlisten. *Rettet.*
- **lav** FR-27 og FR-29 var uklare om når testmodus er på. *Rettet:* testmodus er på når flagget er på eller nøkkelen mangler.
- **lav** SM-2 sa ikke hvem som vurderer kvaliteten. *Rettet:* gruppa vurderer manuelt.

## Avstemming mot kildene
- **Brief v2:** Alt er dekket, eller er bevisst endret 11.11 (sammendrag, begrepsliste og detaljnivå er ute).
- **Faglærers tilbakemelding:** Kriterium 7 om ryddighet i repoet er lagt til i addendum. Kriterium 4 om design hører til neste steg (`bmad-ux`).
