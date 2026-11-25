"""
Feiltekster og andre meldinger til brukeren. Én kilde for tekstene.

Norsk bokmål, du-form, kort og saklig, uten utropstegn (EXPERIENCE.md).
"""

# Konto og innlogging (FR-1, FR-2).
EPOST_FINNES = "Det finnes allerede en konto med denne e-posten."
UGYLDIG_EPOST = "Skriv inn en gyldig e-postadresse."
FOR_KORT_PASSORD = "Passordet må ha minst 8 tegn."
FEIL_INNLOGGING = "Feil e-post eller passord."
OKT_UTLOPT = "Du er logget ut. Logg inn igjen for å fortsette."

# Emner (FR-4).
NAVN_TOMT = "Navnet kan ikke være tomt."
NAVN_TATT = "Du har allerede et emne med dette navnet."
NAVN_FOR_LANGT = "Navnet kan være høyst 100 tegn."

# Opplasting av notat (FR-8).
VELG_FIL = "Velg en fil først."
FIL_FOR_STOR = "Filen er over 5 MB. Velg en mindre fil."
FIL_FEIL_FORMAT = "Formatet støttes ikke. Bruk PDF, DOCX eller TXT."
FIL_TOM = "Filen er tom. Velg en annen fil."
OPPLASTING_AVBRUTT = "Opplastingen ble avbrutt. Filen er ikke lagret. Last opp på nytt."

# Lage quiz (FR-11–FR-14).
ANTALL_UGYLDIG = "Velg et antall fra 5 til 30."
# Feil under generering, én tekst per feilkode fra `ki` (FR-13, FR-15, AD-10).
GENERERING_FEIL = {
    "timeout": "Genereringen tok for lang tid. Filen er lagret, så du kan prøve igjen.",
    "format": "Klarte ikke å lage en gyldig quiz. Prøv igjen, eller velg færre spørsmål.",
    "api_feil": "KI-tjenesten svarte ikke. Prøv igjen.",
    "for_lite_innhold": (
        "Filen har for lite tekst til å lage en quiz. "
        "Last opp et notat med mer innhold."
    ),
    "for_stor": (
        "Filen er for stor til at KI-tjenesten kan lese den. "
        "Del opp notatet og last opp delene hver for seg."
    ),
    "api_nokkel": (
        "KI-tjenesten godtok ikke API-nøkkelen. "
        "Sjekk nøkkelen i .env, eller slå på testmodus."
    ),
}
FIL_ER_LAGRET = "Filen er lagret, så du trenger ikke laste den opp på nytt."
NOTAT_FINNES_IKKE = "Notatet finnes ikke lenger, så quizen ble ikke laget."
INGEN_SERVERKONTAKT = "Fikk ikke kontakt med serveren. Last inn siden på nytt."


def generering_feilet(kode):
    """Teksten for feilkoden. Tom eller ukjent kode gir teksten for `api_feil`."""
    return GENERERING_FEIL.get(kode or "", GENERERING_FEIL["api_feil"])
