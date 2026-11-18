"""Regulariza facturas emitidas fuera de línea."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.application.use_cases.obtener_cufd import obtener_cufd
from src.domain.siat_ports import SiatAuthContext
from src.infrastructure.db.models import (
    EventoSignificativo,
    Factura,
    FacturaEvidencia,
    Paquete,
)
from src.infrastructure.siat.config import SiatSettings, POR_COMPLETAR
from src.infrastructure.siat.evidence import save_soap_evidence
from src.infrastructure.siat.paquetes import build_paquete_gzip, chunk_ids
from src.infrastructure.siat.stub_client import StubSiatClient


@dataclass
class RegularizacionResult:
    cufd_envio: str
    evento: EventoSignificativo
    paquetes: list[Paquete] = field(default_factory=list)
    facturas_ya_en_sin: list[int] = field(default_factory=list)


def regularizar_contingencia(
    *,
    empresa_id: int,
    evento_id: int,
    sucursal_id: int | None = None,
    punto_venta_id: int | None = None,
    client: StubSiatClient | None = None,
    settings: SiatSettings | None = None,
) -> RegularizacionResult:
    settings = settings or SiatSettings.from_django()
    client = client or StubSiatClient()
    evento = EventoSignificativo.objects.get(pk=evento_id, empresa_id=empresa_id)

    cufd = obtener_cufd(
        empresa_id=empresa_id,
        sucursal_id=sucursal_id,
        punto_venta_id=punto_venta_id,
        client=client,
        settings=settings,
    )

    evento.fecha_fin = datetime.now(timezone.utc)
    evento.cufd_envio = cufd.valor
    evento.registrado_siat = True
    evento.save()

    offline_qs = Factura.objects.filter(
        empresa_id=empresa_id,
        offline_flag=True,
        estado_interno=Factura.EstadoInterno.OFFLINE,
    ).order_by("id")

    ya_en_sin: list[int] = []
    pendientes: list[int] = []
    ctx = SiatAuthContext(
        token=settings.token if settings.token != POR_COMPLETAR else "stub",
        codigo_ambiente=settings.ambiente,
        codigo_sistema=settings.codigo_sistema,
        nit=settings.nit if settings.nit != POR_COMPLETAR else "0",
        codigo_modalidad=settings.modalidad,
    )
    for factura in offline_qs:
        if not factura.codigo_recepcion and factura.cuf:
            estado = client.verificacion_estado_factura(ctx, factura.cuf)
            if int(estado.get("codigoEstado", 0)) in (908, 901):
                factura.estado_interno = Factura.EstadoInterno.VALIDADA
                factura.estado_siat = str(estado["codigoEstado"])
                factura.offline_flag = False
                factura.save()
                ya_en_sin.append(factura.id)
                continue
        pendientes.append(factura.id)

    paquetes_creados: list[Paquete] = []
    for lote in chunk_ids(pendientes, 500):
        xmls: list[bytes] = []
        for fid in lote:
            ev = (
                FacturaEvidencia.objects.filter(factura_id=fid, tipo="xml_emision")
                .order_by("-id")
                .first()
            )
            if ev and ev.xml:
                xmls.append(ev.xml.encode("utf-8"))
        built = build_paquete_gzip(xmls)
        recv = client.recepcion_paquete(
            ctx,
            {"archivo": built.gzip_bytes, "hashArchivo": built.sha256_hex},
        )
        paquete = Paquete.objects.create(
            empresa_id=empresa_id,
            evento=evento,
            codigo_recepcion=recv.get("codigoRecepcion", ""),
            estado_siat=str(recv.get("codigoEstado", "")),
            hash_sha256=built.sha256_hex,
            contenido_gzip=built.gzip_bytes,
            cantidad_facturas=built.cantidad,
        )
        if recv.get("exchange"):
            save_soap_evidence(
                empresa_id=empresa_id,
                exchange=recv["exchange"],
                token=settings.token,
                tipo="paquete_recepcion",
            )
        val = client.validacion_paquete(ctx, paquete.codigo_recepcion)
        paquete.estado_siat = str(val.get("codigoEstado", paquete.estado_siat))
        paquete.save(update_fields=["estado_siat"])
        if val.get("exchange"):
            save_soap_evidence(
                empresa_id=empresa_id,
                exchange=val["exchange"],
                token=settings.token,
                tipo="paquete_validacion",
            )
        if int(val.get("codigoEstado", 0)) == 908:
            Factura.objects.filter(id__in=lote).update(
                estado_interno=Factura.EstadoInterno.VALIDADA,
                estado_siat="908",
                offline_flag=False,
                codigo_recepcion=paquete.codigo_recepcion,
            )
        paquetes_creados.append(paquete)

    return RegularizacionResult(
        cufd_envio=cufd.valor,
        evento=evento,
        paquetes=paquetes_creados,
        facturas_ya_en_sin=ya_en_sin,
    )
