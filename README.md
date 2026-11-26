# G82 — Pusher 30

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

## Hva appen gjør

FåreQuiz lager flervalgsquizer fra dine egne notater. Du laster opp et notat som PDF, DOCX eller TXT, velger nivå og antall spørsmål, og KI lager quizen. Spørsmål du svarer feil på, havner i en feilbank der du øver til de er lært, og du ser hvor godt du dekker hvert notat og emne.

## Hva som trengs

- git
- Python 3.14
- [uv](https://docs.astral.sh/uv/), eller pip

Med uv trenger du ikke installere Python selv. `uv sync` henter Python 3.14 hvis den mangler.

## Kom i gang

Klon repoet og gå inn i mappa:

    git clone https://github.com/IBE160-2026/G82-bull-knold-skjerven.git
    cd G82-bull-knold-skjerven

Kjør resten av kommandoene i denne mappa.

**Med uv:**

    uv sync
    uv run python manage.py migrate
    uv run python manage.py seed_testdata
    uv run python manage.py runserver

**Med pip:** lag og aktiver et virtuelt miljø først.

    py -3.14 -m venv .venv          # Windows
    .venv\Scripts\activate          # Windows
    python3.14 -m venv .venv        # macOS og Linux
    source .venv/bin/activate       # macOS og Linux
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py seed_testdata
    python manage.py runserver

Nekter PowerShell å kjøre `.venv\Scripts\activate`, kjører du `Set-ExecutionPolicy -Scope Process RemoteSigned` først.

Åpne så `http://127.0.0.1:8000/` i nettleseren.

## Testbruker

`seed_testdata` lager en testbruker med emnet «Webutvikling», tre notater fra `testdokumenter/`, quizer på alle tre nivåer, leverte forsøk, en feilbank med lærte og ikke lærte spørsmål og et påbegynt forsøk.

Logg inn med:

- E-post: `sensor@farequiz.no`
- Passord: `sensor123`

E-posten og passordet står også på innloggingssiden i testmodus. Kommandoen kjører alltid i testmodus og kaller ikke KI-tjenesten. Du kan kjøre den flere ganger. Da slettes testbrukerens emner, og dataene lages på nytt.

Vil du prøve opplasting selv, kan du bruke filene i `testdokumenter/`.

## Testmodus

Testmodus er på når `ANTHROPIC_API_KEY` er tom, slik den er uten `.env`, eller når `TESTMODUS=1`. Da kalles ikke KI-tjenesten, og du trenger ingen API-nøkkel. Banneret øverst på alle sider viser dette:

> Testmodus: quizene bruker mock-svar, ingen KI kalles.

Det betyr at quizene hentes fra forhåndslagrede svar i `ki/mock/`, laget av KI fra de fem filene i `testdokumenter/`. Laster du opp en egen fil som ikke er et testdokument, får du quizen fra et standard testdokument, og quizsiden har en merknad om det.

## Ekte modell

For å lage quizer med ekte KI trenger du en API-nøkkel fra Anthropic.

1. Kopier `.env.example` til `.env`:

       copy .env.example .env          # Windows
       cp .env.example .env            # macOS og Linux

2. Åpne `.env`, legg inn nøkkelen i `ANTHROPIC_API_KEY` og sett `TESTMODUS=0`.
3. Standardmodellen er `claude-sonnet-5-5`. Vil du bruke en annen modell, bytter du `KI_MODELL`.
4. Start `runserver` på nytt. Banneret er borte når testmodus er av.

`.env` er ignorert av git. Ikke commit den.

## Mobil på samme nett

Du kan åpne appen på mobilen hvis den er på samme nett som maskinen. Dette er ikke hosting, appen kjører fortsatt bare på maskinen din. Bruk det bare på et nett du stoler på, fordi `DEBUG=True` viser feilsider med detaljer.

1. Finn maskinens IP-adresse, for eksempel med `ipconfig` på Windows, `ipconfig getifaddr en0` på macOS eller `hostname -I` på Linux.
2. Legg den til i `ALLOWED_HOSTS` i `.env`, for eksempel `ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.23`. Har du ikke `.env`, kopierer du `.env.example` som over.
3. Start serveren slik at den svarer på nettet:

       uv run python manage.py runserver 0.0.0.0:8000     # med uv
       python manage.py runserver 0.0.0.0:8000            # med pip

4. Åpne `http://192.168.1.23:8000/` på mobilen, med din egen IP-adresse.

Brannmuren kan spørre om tilgang første gang.

## For gruppa

Mock-svarene som ligger i `ki/mock/` nå, er skrevet av Claude Opus 5.5 utenfor appen, ikke med appens prompt. Den som har gruppas nøkkel, kan erstatte dem med ekte genereringer:

    uv run python manage.py lag_mocksvar

Kommandoen nekter å kjøre i testmodus, så sett `ANTHROPIC_API_KEY` og `TESTMODUS=0` i `.env` først. Den skriver `ki/mock/` (filene og `manifest.json`), som så committes. Det er 30 spørsmål per dokument og nivå, og appen bruker de første N. Kjør den på nytt når et testdokument, prompten eller `PROMPT_VERSJON` endres.

Når du endrer avhengigheter, oppdaterer du `requirements.txt` slik. CI feiler hvis den ikke er i takt med `uv.lock`.

    uv export --no-hashes --frozen --no-dev -o requirements.txt

Nettlesertesten med axe (universell utforming) kjøres med `uv run playwright install chromium` én gang (på Linux `uv run playwright install --with-deps chromium`) og så `uv run python manage.py test --tag nettleser`. Vanlig `manage.py test` hopper over den.

## Medlemmer

- Christian R Bull
- Martin Skjerven
- Magnus Gjerstad

Changelog: Fjernet Henrik L Knold ettersom han fortsatt ikke har gitt en lyd fra seg :/
