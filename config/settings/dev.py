"""Configuración de desarrollo."""

from .base import *  # noqa: F403

DEBUG = True

# Cookies de sesión/CSRF usables desde el origen Vite en local.
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = False
