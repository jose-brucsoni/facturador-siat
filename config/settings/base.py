"""Configuración base de Django."""

from __future__ import annotations

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    SIAT_MODALIDAD=(int, 2),
    SIAT_TIMEOUT_SECONDS=(int, 30),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="unsafe-dev-only-change-me")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_q",
    "src.infrastructure.db",
    "src.presentation.api",
    "src.presentation.web",
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

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "src" / "presentation" / "web" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Base de datos (SQLite en demo; Postgres vía DATABASE_URL).
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-bo"
TIME_ZONE = "America/La_Paz"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "db.User"
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

Q_CLUSTER = {
    "name": "facturador-siat",
    "workers": 2,
    "timeout": 90,
    "retry": 120,
    "queue_limit": 500,
    "bulk": 10,
    "orm": "default",
}

# Parámetros del SIN (solo desde entorno).
SIAT_MODO = env("SIAT_MODO", default="stub")
SIAT_AMBIENTE = env("SIAT_AMBIENTE", default="POR_COMPLETAR")
SIAT_NIT = env("SIAT_NIT", default="POR_COMPLETAR")
SIAT_CODIGO_SISTEMA = env("SIAT_CODIGO_SISTEMA", default="POR_COMPLETAR")
SIAT_MODALIDAD = env("SIAT_MODALIDAD")
SIAT_CODIGO_SUCURSAL = env("SIAT_CODIGO_SUCURSAL", default="POR_COMPLETAR")
SIAT_CODIGO_PUNTO_VENTA = env("SIAT_CODIGO_PUNTO_VENTA", default="POR_COMPLETAR")
SIAT_TOKEN = env("SIAT_TOKEN", default="POR_COMPLETAR")
SIAT_WSDL_CODIGOS = env("SIAT_WSDL_CODIGOS", default="POR_COMPLETAR")
SIAT_WSDL_SINCRONIZACION = env("SIAT_WSDL_SINCRONIZACION", default="POR_COMPLETAR")
SIAT_WSDL_OPERACIONES = env("SIAT_WSDL_OPERACIONES", default="POR_COMPLETAR")
SIAT_WSDL_FACTURACION = env("SIAT_WSDL_FACTURACION", default="POR_COMPLETAR")
SIAT_QR_BASE_URL = env(
    "SIAT_QR_BASE_URL",
    default="https://pilotosiat.impuestos.gob.bo/consulta/QR",
)
SIAT_TIMEOUT_SECONDS = env("SIAT_TIMEOUT_SECONDS")
SIAT_SCHEMAS_DIR = BASE_DIR / "schemas"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "mask_siat_token": {
            "()": "src.infrastructure.siat.logging_filters.MaskSiatTokenFilter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["mask_siat_token"],
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
