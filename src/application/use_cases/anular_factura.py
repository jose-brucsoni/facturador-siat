"""Anula una factura validada."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from calendar import monthrange

from src.domain.siat_ports import SiatAuthContext
from src.domain.tenancy import TenantIsolationError, assert_same_empresa
from src.infrastructure.db.models import Anulacion, Auditoria, Factura
from src.infrastructure.notifications import ConsoleNotifier
from src.infrastructure.siat.config import SiatSettings, POR_COMPLETAR
from src.infrastructure.siat.evidence import save_soap_evidence
from src.infrastructure.siat.recepcion import anular_factura as soap_anular
from src.infrastructure.siat.stub_client import StubSiatClient

RND_FUERA_DE_PLAZO = "102600000025"


class AnulacionError(Exception):
    pass


@dataclass
class AnulacionResult:
    anulacion: Anulacion | None
    fuera_de_plazo: bool = False
    guia_rnd: str = ""
    mensaje: str = ""


def plazo_anulacion(fecha_emision: date, hoy: date | None = None) -> bool:
    """Indica si aún se puede anular según el plazo."""
    hoy = hoy or date.today()
    year = fecha_emision.year + (1 if fecha_emision.month == 12 else 0)
    month = 1 if fecha_emision.month == 12 else fecha_emision.month + 1
    limite = date(year, month, min(9, monthrange(year, month)[1]))
    return hoy <= limite


def anular_factura(
    *,
    empresa_id: int,
    factura_id: int,
    motivo_codigo: str,
    motivo_descripcion: str = "",
    actor_id: int | None = None,
    client: StubSiatClient | None = None,
    notifier: ConsoleNotifier | None = None,
    settings: SiatSettings | None = None,
    hoy: date | None = None,
) -> AnulacionResult:
    settings = settings or SiatSettings.from_django()
    client = client or StubSiatClient()
    notifier = notifier or ConsoleNotifier()

    factura = Factura.objects.select_related("cliente").get(pk=factura_id)
    assert_same_empresa(factura.empresa_id, empresa_id)

    if factura.estado_interno != Factura.EstadoInterno.VALIDADA:
        raise AnulacionError("Solo se pueden anular facturas validadas (908).")

    emision = factura.fecha_emision.date() if factura.fecha_emision else date.today()
    if not plazo_anulacion(emision, hoy=hoy):
        return AnulacionResult(
            anulacion=None,
            fuera_de_plazo=True,
            guia_rnd=RND_FUERA_DE_PLAZO,
            mensaje=(
                "Anulación fuera de plazo. No se llama al SIN. "
                f"Trámite según RND {RND_FUERA_DE_PLAZO}."
            ),
        )

    ctx = SiatAuthContext(
        token=settings.token if settings.token != POR_COMPLETAR else "stub",
        codigo_ambiente=settings.ambiente,
        codigo_sistema=settings.codigo_sistema,
        nit=settings.nit if settings.nit != POR_COMPLETAR else "0",
        codigo_modalidad=settings.modalidad,
    )
    result = soap_anular(
        client,
        ctx,
        {"cuf": factura.cuf, "codigoMotivo": motivo_codigo},
    )
    codigo = int(result.get("codigoEstado", 0))
    exchange = result.get("exchange")
    if exchange:
        save_soap_evidence(
            empresa_id=empresa_id,
            factura_id=factura.id,
            exchange=exchange,
            token=settings.token,
            tipo="anulacion",
        )

    anulacion = Anulacion.objects.create(
        empresa_id=empresa_id,
        factura=factura,
        motivo_codigo=motivo_codigo,
        motivo_descripcion=motivo_descripcion,
        estado_siat=str(codigo),
        codigo_recepcion=result.get("codigoRecepcion", "") or "",
        created_by_id=actor_id,
    )
    if codigo == 905:
        factura.estado_interno = Factura.EstadoInterno.ANULADA
        factura.estado_siat = "905"
        factura.save(update_fields=["estado_interno", "estado_siat", "updated_at"])
        email = factura.cliente.email
        if email:
            notifier.send_email(
                email,
                f"Anulación factura {factura.numero_factura}",
                (
                    f"Se anuló la factura {factura.numero_factura}. "
                    f"CUF: {factura.cuf}. Motivo: {motivo_descripcion or motivo_codigo}."
                ),
            )
            anulacion.notificado_comprador = True
            anulacion.save(update_fields=["notificado_comprador"])

    Auditoria.objects.create(
        empresa_id=empresa_id,
        actor_id=actor_id,
        accion="anular_factura",
        entidad="Factura",
        entidad_id=str(factura.pk),
        detalle={"codigoEstado": codigo, "motivo": motivo_codigo},
    )
    return AnulacionResult(anulacion=anulacion, mensaje=f"Estado SIAT {codigo}")
