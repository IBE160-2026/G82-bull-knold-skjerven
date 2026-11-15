---
title: "Product Brief v2 (individuelt utkast): Foredragsnotater → Sammendrag & Quiz"
status: individual-draft
author: "Martin"
created: 2026-10-28
---

## Executive Summary

En webapp der studenter laster opp forelesningsnotater og får KI-generert sammendrag, begrepsliste og quiz. Quizen gir poeng, og feilsvar havner i en feilbank til spørsmålet er rett to ganger på rad. Notater organiseres under emner studenten oppretter selv, med historikk og dekningsgrad per notat og emne. IBE160, forslag 8, gruppe G82.

## Problemet

Å lese notater på nytt før eksamen gir gjenkjenning, ikke forståelse. Aktiv gjenkalling er mer effektivt, men å lage gode quizspørsmål fra egne notater tar tid studenter sjelden har.

## Løsningen

Studenten logger inn (e-post/passord), velger et emne og laster opp et notat (PDF/DOCX/TXT). Deretter velges detaljnivå, vanskelighetsgrad og antall spørsmål. Sammendraget vises mens quizen genereres; ved timeout vises «prøv igjen». Feilsvar legges i feilbanken og fjernes etter to riktige på rad. Hvert forsøk lagres med dato/poengsum; dekningsgrad beregnes per notat og emne.

Modell: Sonnet 5.5, med strukturert validering (ett riktig svar per spørsmål) som eneste automatiske kvalitetssikring. Nøkkel i `.env`, med `.env.example`, testmodus med mock-svar, testbruker og faste testdokumenter.

## Hva gjør dette annerledes

Sammendrag og quiz genereres fra samme kilde og forståelse av stoffet, og feilsvar følges opp automatisk til de er lært — ikke bare generert én gang og glemt.

## Hvem dette er for

Studenter generelt, med åpen registrering. Kostnad holdes nede med maks antall genereringer per bruker per døgn (f.eks. 10, nullstilt ved midnatt) og et månedlig utgiftstak hos KI-leverandøren som sikkerhetsnett.

## Suksesskriterier

- **Quiz:** PDF på 10 sider gir valgt antall spørsmål, hver med nøyaktig tre alternativer og ett riktig svar.
- **Feilbank:** Feilsvart spørsmål dukker opp neste økt; to riktige på rad fjerner det; nytt feilsvar nullstiller telleren.
- **Dekningsgrad:** Beregnes korrekt per notat og aggregert per emne.
- **Innlogging:** Feil passord avvises; ingen bruker ser andres notater.
- **PDF-avvisning:** Under ca. 200 tegn/side avvises med melding; over terskelen behandles, inkl. lysbilde-PDF-er.
- **Bruksgrense:** 11. generering samme døgn avvises med beskjed om når bruker kan fortsette.
- **Kjørbarhet:** Appen kjører kjerneflyten i testmodus etter README, uten ekte API-nøkkel.

## Scope

**Inn:** Innlogging, manuelt emne, opplasting (PDF/DOCX/TXT), preferanser, sammendrag + begrepsliste + quiz, poeng, feilbank («lært» ved 2 riktige på rad), dekningsgrad, trinnvis UI, daglig bruksgrense, testmodus.

**Ut:** Kurs-FAQ-chatbot, Feide/SSO, spaced repetition, oppfølgingsrunder som eget nivå, bakgrunnsjobb utover lukket fane. **[ASSUMPTION: ZIP-opplasting av hele emner (Magnus' trinn 2) ikke avklart av meg — holdt utenfor til gruppa har bestemt]**

## Visjon

Hvis v1 fungerer godt: feilbanken videreutvikles til ekte intervall-repetisjon, og dekningsgrad per emne blir noe studenten planlegger lesing ut fra — en studieassistent for hele faget.

## Åpne spørsmål – mitt standpunkt

1. **Sonnet 5.5, kun formatnivå kvalitetssikring** (ett riktig svar validert strukturelt). Manuell verifisering mot pensum lønner seg ikke tidsmessig, og god prompt + strukturert utdata fanger det meste.
2. **Enkel feilbank, ikke intervall-repetisjon.** Feilsvar dukker opp neste økt til to riktige på rad; ekte intervaller krever dato-planlegging som er for kostbart å bygge og teste nå.
3. **Prøv, avvis kun nesten tekstløse dokumenter** (~200 tegn/side). Lysbilde-PDF-er er det vanligste studentene har; å stoppe på dem ville rammet det typiske tilfellet.
4. **Trinnvis visning, ingen bakgrunnsjobb.** Sammendrag vises mens quiz genereres, med «prøv igjen» ved timeout; lagring utover lukket fane er bare verdt det om vi uansett trenger en bakgrunnsjobb, noe som ikke er avgjort.
5. **Mellomambisiøs: emne → notat → quiz-forsøk.** Emnet opprettes manuelt (ingen ZIP nødvendig); forsøk lagres med dato/poengsum, og dekningsgrad beregnes per notat/emne, uten eget nivå for oppfølgingsrunder.
6. **Åpen for alle studenter, med to kostnadssperrer:** bruksgrense per bruker per døgn og et utgiftstak hos KI-leverandøren.
