"""
Django settings for BSSREUNION project (Baraibunia Secondary School Reunion).
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# CORE / SECURITY
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-CHANGE-THIS-BEFORE-DEPLOY-bssreunion-secret-key"
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

CSRF_TRUSTED_ORIGINS = [
    h for h in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if h
]

# ---------------------------------------------------------------------------
# APPS
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "registration",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "bssreunion.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "registration.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "bssreunion.wsgi.application"

# ---------------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if os.environ.get("DB_ENGINE") == "postgres":
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "bssreunion"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }

# Neon / Vercel Postgres: if a DATABASE_URL (or POSTGRES_URL) env var is
# present, it takes priority over everything above. This is what gets set
# automatically when you connect a Neon database to the Vercel project.
_db_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
if _db_url:
    import dj_database_url
    DATABASES["default"] = dj_database_url.parse(_db_url, conn_max_age=600, ssl_require=True)

# ---------------------------------------------------------------------------
# PASSWORD VALIDATION
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# I18N
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# STATIC / MEDIA
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# EMAIL (SMTP)
# ---------------------------------------------------------------------------
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "BSSREUNION <no-reply@bssreunion.com>"
)

# ---------------------------------------------------------------------------
# SSLCOMMERZ
# ---------------------------------------------------------------------------
SSLCOMMERZ_STORE_ID = os.environ.get("SSLCOMMERZ_STORE_ID", "testbox")
SSLCOMMERZ_STORE_PASSWORD = os.environ.get("SSLCOMMERZ_STORE_PASSWORD", "qwerty")
SSLCOMMERZ_IS_SANDBOX = os.environ.get("SSLCOMMERZ_IS_SANDBOX", "True") == "True"

# Base URL of this site, used to build SSLCommerz success/fail/cancel/ipn URLs
SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "http://127.0.0.1:8000")

# ---------------------------------------------------------------------------
# EVENT / SITE SETTINGS (used in templates, PDF generator etc.)
# ---------------------------------------------------------------------------
SCHOOL_NAME = os.environ.get("SCHOOL_NAME", "Baraibunia Secondary School")
EVENT_SHORT_NAME = os.environ.get("EVENT_SHORT_NAME", "BSSREUNION")
EVENT_FULL_NAME = os.environ.get("EVENT_FULL_NAME", "BSS Reunion 2026")
EVENT_DATE_TEXT = os.environ.get("EVENT_DATE_TEXT", "To be announced")
EVENT_VENUE = os.environ.get("EVENT_VENUE", "Baraibunia Secondary School Campus")
REGISTRATION_FEE = int(os.environ.get("REGISTRATION_FEE", 500))

LOGIN_URL = "/admin-panel/login/"
LOGIN_REDIRECT_URL = "/admin-panel/dashboard/"
