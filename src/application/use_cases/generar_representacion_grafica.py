from __future__ import annotations

from src.domain.tenancy import assert_same_empresa
from src.infrastructure.db.models import Auditoria, Factura, FacturaEvidencia
from src.infrastructure.pdf.invoice_pdf import generate_invoice_pdf
from src.infrastructure.pdf.qr import build_qr_url


def generar_representacion_grafica(
    *, empresa_id: int, factura_id: int, actor_id: int | None = None
) -> bytes:
    factura = Factura.objects.select_related(
        "empresa", "cliente", "sucursal"
    ).get(pk=factura_id)
    assert_same_empresa(factura.empresa_id, empresa_id)

    leyenda = factura.leyenda or "Leyenda Ley 453"
    if factura.offline_flag or factura.codigo_emision == 2:
        leyenda = f"{leyenda} | Emisión fuera de línea"

    pdf = generate_invoice_pdf(
        nit=factura.empresa.nit,
        razon_social=factura.empresa.razon_social,
        numero=factura.numero_factura or 0,
        cuf=factura.cuf,
        cufd=factura.cufd,
        fecha=str(factura.fecha_emision or ""),
        sucursal=str(factura.sucursal.codigo_sucursal),
        cliente=factura.cliente.razon_social,
        monto_total=str(factura.monto_total),
        monto_iva=str(factura.monto_total_sujeto_iva),
        leyenda=leyenda,
        offline=factura.offline_flag or factura.codigo_emision == 2,
        detalle_lines=[
            f"{d.codigo_producto} {d.descripcion} x{d.cantidad} = {d.subtotal}"
            for d in factura.detalles.all()
        ],
    )
    FacturaEvidencia.objects.create(
        empresa_id=empresa_id,
        factura=factura,
        tipo="pdf",
        metadata={
            "qr_url": build_qr_url(
                nit=factura.empresa.nit,
                cuf=factura.cuf,
                numero=factura.numero_factura or 0,
                tamano=1 if factura.offline_flag else 2,
            ),
            "bytes_len": len(pdf),
        },
    )
    Auditoria.objects.create(
        empresa_id=empresa_id,
        actor_id=actor_id,
        accion="generar_pdf",
        entidad="Factura",
        entidad_id=str(factura.pk),
        detalle={},
    )
    return pdf
