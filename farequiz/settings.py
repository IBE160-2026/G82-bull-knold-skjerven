"""
Innstillinger for FåreQuiz.

Verdiene leses fra miljøet og fra `.env` i prosjektroten. Uten `.env` gjelder
standardverdiene i AD-22: `DEBUG=True`, en fast og usikker utviklingsnøkkel,
`ALLOWED_HOSTS=localhost,127.0.0.1` og testmodus på (ingen API-nøkkel).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def _env_tekst(navn, standard=""):
    """Tom verdi i `.env` (for eksempel `SECRET_KEY=`) gir standardverdien."""
    verdi = os.environ.get(navn, "").strip()
    return verdi or standard


def _env_bool(navn, standard):
    verdi = _env_tekst(navn)
    if not verdi:
        return standard
    return verdi.lower() in {"1", "true", "yes", "on"}


def _env_liste(navn, standard):
    verdi = _env_tekst(navn)
    if not verdi:
        return list(standard)
    return [del_.strip() for del_ in verdi.split(",") if del_.strip()]


# USIKKER: fast nøkkel bare for lokal utvikling. Sett SECRET_KEY i .env ellers.
SECRET_KEY = _env_tekst(
    "SECRET_KEY",
    "django-insecure-farequiz-lokal-utvikling-ikke-bruk-i-produksjon",
)

DEBUG = _env_bool("DEBUG", True)

ALLOWED_HOSTS = _env_liste("ALLOWED_HOSTS", ["localhost", "127.0.0.1"])

# KI. Bare `ki` leser disse (AD-12).
ANTHROPIC_API_KEY = _env_tekst("ANTHROPIC_API_KEY")
KI_MODELL = _env_tekst("KI_MODELL", "claude-sonnet-5-5")
TESTMODUS = _env_tekst("TESTMODUS")


# Applikasjoner. Ingen django.contrib.admin (AD-14: sletting bare via slett_emne).

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "kontoer",
    "studier",
    "ki",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    "kontoer.middleware.VilkarMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "farequiz.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "farequiz.context_processors.testmodus",
            ],
        },
    },
]

WSGI_APPLICATION = "farequiz.wsgi.application"

TEST_RUNNER = "farequiz.testrunner.TestmodusRunner"


# Database. Ingen ATOMIC_REQUESTS, og ingen KI-kall i transaksjoner (AD-19).

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "ATOMIC_REQUESTS": False,
        "OPTIONS": {
            "transaction_mode": "IMMEDIATE",
            "timeout": 20,
        },
    }
}


# Brukere og passord (AD-15).

AUTH_USER_MODEL = "kontoer.Bruker"

# Bare minst 8 tegn (FR-1, beslutning 23.11). Meldingen står i feilmeldinger.py.
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
]

LOGIN_URL = "kontoer:logg_inn"

LOGIN_REDIRECT_URL = "/"

LOGOUT_REDIRECT_URL = "kontoer:logg_inn"


# Språk og tid. Lagres i UTC og vises i Europe/Oslo.

LANGUAGE_CODE = "nb"

TIME_ZONE = "Europe/Oslo"

USE_I18N = True

USE_TZ = True


# Statiske filer og opplastede filer. MEDIA_ROOT har ingen URL-rute (AD-8).

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
# Serverer også fra STATICFILES_DIRS når DEBUG=False, uten collectstatic.
WHITENOISE_USE_FINDERS = True

MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
