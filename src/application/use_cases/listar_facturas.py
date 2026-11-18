from __future__ import annotations

from datetime import datetime

from django.db.models import QuerySet

from src.domain.tenancy import assert_same_empresa
from src.infrastructure.db.models import Auditoria, Factura
from src.infrastructure.notifications import ConsoleNotifier


def listar_facturas(
    *,
    empresa_id: int,
    numero: int | None = None,
    cuf: str | None = None,
    cliente_id: int | None = None,
    estado_interno: str | None = None,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
) -> QuerySet[Factura]:
    qs = Factura.objects.filter(empresa_id=empresa_id).select_related("cliente")
    if numero is not None:
        qs = qs.filter(numero_factura=numero)
    if cuf:
        qs = qs.filter(cuf=cuf)
    if cliente_id is not None:
        qs = qs.filter(cliente_id=cliente_id)
    if estado_interno:
        qs = qs.filter(estado_interno=estado_interno)
    if fecha_desde:
        qs = qs.filter(fecha_emision__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha_emision__lte=fecha_hasta)
    return qs.order_by("-fecha_emision", "-id")


def reenviar_factura_comprador(
    *,
    empresa_id: int,
    factura_id: int,
    pdf_bytes: bytes,
    actor_id: int | None = None,
    notifier: ConsoleNotifier | None = None,
) -> None:
    factura = Factura.objects.select_related("cliente").get(pk=factura_id)
    assert_same_empresa(factura.empresa_id, empresa_id)
    notifier = notifier or ConsoleNotifier()
    evidencia = (
        factura.evidencias.filter(tipo="xml_emision").order_by("-id").first()
    )
    attachments: list[tuple[str, bytes]] = [
        (f"factura_{factura.numero_factura}.pdf", pdf_bytes)
    ]
    if evidencia and evidencia.xml:
        attachments.append(
            (f"factura_{factura.numero_factura}.xml", evidencia.xml.encode("utf-8"))
        )
    notifier.send_email(
        factura.cliente.email or "sin-email@example.com",
        f"Factura {factura.numero_factura}",
        f"Adjuntamos PDF y XML. CUF: {factura.cuf}",
        attachments=attachments,
    )
    Auditoria.objects.create(
        empresa_id=empresa_id,
        actor_id=actor_id,
        accion="reenvio_factura",
        entidad="Factura",
        entidad_id=str(factura.pk),
        detalle={"email": factura.cliente.email},
    )
