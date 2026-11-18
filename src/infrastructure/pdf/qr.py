"""Genera la URL y la imagen del código QR."""

from __future__ import annotations

from io import BytesIO
from urllib.parse import urlencode

import qrcode
from django.conf import settings


def build_qr_url(
    *,
    nit: str,
    cuf: str,
    numero: int,
    tamano: int = 1,
    base_url: str | None = None,
) -> str:
    """Arma la URL de consulta de la factura."""
    base = base_url or getattr(
        settings,
        "SIAT_QR_BASE_URL",
        "https://pilotosiat.impuestos.gob.bo/consulta/QR",
    )
    query = urlencode({"nit": nit, "cuf": cuf, "numero": numero, "t": tamano})
    return f"{base}?{query}"


def render_qr_png(url: str, box_size: int = 8) -> bytes:
    img = qrcode.make(url, box_size=box_size, border=2)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
