"""Configuración para pruebas."""

from .base import *  # noqa: F403

DEBUG = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

SIAT_MODO = "stub"
SIAT_TOKEN = "POR_COMPLETAR"
SIAT_WSDL_CODIGOS = "POR_COMPLETAR"
SIAT_WSDL_SINCRONIZACION = "POR_COMPLETAR"
SIAT_WSDL_OPERACIONES = "POR_COMPLETAR"
SIAT_WSDL_FACTURACION = "POR_COMPLETAR"
