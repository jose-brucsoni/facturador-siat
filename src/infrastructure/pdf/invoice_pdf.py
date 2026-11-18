"""Genera el PDF de la factura."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from src.infrastructure.pdf.qr import build_qr_url, render_qr_png


def generate_invoice_pdf(
    *,
    nit: str,
    razon_social: str,
    numero: int,
    cuf: str,
    cufd: str,
    fecha: str,
    sucursal: str,
    cliente: str,
    monto_total: str,
    monto_iva: str,
    leyenda: str,
    offline: bool = False,
    detalle_lines: list[str] | None = None,
) -> bytes:
    buffer = BytesIO()
    width, height = letter[0], letter[1] / 2
    c = canvas.Canvas(buffer, pagesize=(width, height))
    c.setPageCompression(0)

    y = height - 1.5 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1.5 * cm, y, "FACTURA")
    y -= 0.7 * cm
    c.setFont("Helvetica", 9)
    c.drawString(1.5 * cm, y, f"NIT: {nit}")
    y -= 0.5 * cm
    c.drawString(1.5 * cm, y, f"Razón Social: {razon_social}")
    y -= 0.5 * cm
    c.drawString(1.5 * cm, y, f"Número: {numero}")
    y -= 0.5 * cm
    c.drawString(1.5 * cm, y, f"Fecha: {fecha}")
    y -= 0.5 * cm
    c.drawString(1.5 * cm, y, f"Sucursal: {sucursal}")
    y -= 0.5 * cm
    c.drawString(1.5 * cm, y, f"Cliente: {cliente}")
    y -= 0.5 * cm
    c.drawString(1.5 * cm, y, f"CUF: {cuf}")
    y -= 0.5 * cm
    c.drawString(1.5 * cm, y, f"CUFD: {cufd}")
    y -= 0.7 * cm
    for line in detalle_lines or []:
        c.drawString(1.5 * cm, y, line[:90])
        y -= 0.4 * cm
    y -= 0.3 * cm
    c.drawString(1.5 * cm, y, f"Monto Total: {monto_total}")
    y -= 0.5 * cm
    c.drawString(1.5 * cm, y, f"Monto Sujeto a IVA: {monto_iva}")
    y -= 0.7 * cm
    c.setFont("Helvetica-Oblique", 8)
    text_object = c.beginText(1.5 * cm, y)
    text_object.textLines(leyenda[:240])
    c.drawText(text_object)
    if offline:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(1.5 * cm, 1.2 * cm, "OPERACIÓN FUERA DE LÍNEA")

    tamano = 1 if offline else 2
    url = build_qr_url(nit=nit, cuf=cuf, numero=numero, tamano=tamano)
    qr_png = render_qr_png(url)
    c.drawImage(
        ImageReader(BytesIO(qr_png)),
        width - 4.5 * cm,
        1.0 * cm,
        width=3.2 * cm,
        height=3.2 * cm,
        mask="auto",
    )
    c.showPage()
    c.save()
    return buffer.getvalue()
