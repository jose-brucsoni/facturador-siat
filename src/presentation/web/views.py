from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import ensure_csrf_cookie


def _dist_dir() -> Path:
    return Path(getattr(settings, "FRONTEND_DIST", settings.BASE_DIR / "frontend" / "dist"))


@ensure_csrf_cookie
def spa_index(request: HttpRequest) -> HttpResponse:
    """Sirve el index.html de la SPA (Vite build)."""
    index = _dist_dir() / "index.html"
    if not index.exists():
        return HttpResponse(
            "<!doctype html><html lang='es'><body style='font-family:sans-serif;padding:2rem'>"
            "<h1>Frontend no construido</h1>"
            "<p>Ejecuta <code>cd frontend && npm install && npm run build</code> "
            "o usa <code>npm run dev</code> en el puerto 5173 durante el desarrollo.</p>"
            "</body></html>",
            content_type="text/html; charset=utf-8",
            status=503,
        )
    return FileResponse(index.open("rb"), content_type="text/html; charset=utf-8")


def spa_asset(request: HttpRequest, asset_path: str) -> HttpResponse:
    """Sirve assets del build (js/css/svg) desde frontend/dist."""
    dist = _dist_dir()
    target = (dist / asset_path).resolve()
    if not str(target).startswith(str(dist.resolve())) or not target.is_file():
        return HttpResponseNotFound("Asset no encontrado")
    return FileResponse(target.open("rb"))
