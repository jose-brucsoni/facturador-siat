"""Emite una factura Compra-Venta."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.application.use_cases.armar_xml_compra_venta import armar_xml_compra_venta
from src.application.use_cases.generar_cuf import generar_cuf_factura
from src.domain.siat_ports import SiatAuthContext, SinComunicacionError
from src.domain.tenancy import TenantIsolationError, assert_same_empresa
from src.infrastructure.db.models import (
    Auditoria,
    Cliente,
    CodigoOperacion,
    ColaEnvio,
    Factura,
    FacturaDetalle,
    FacturaEvidencia,
    InvoiceCounter,
    Producto,
)
from src.infrastructure.queue.tasks import enqueue_envio_factura, process_envio_factura
from src.infrastructure.siat.config import SiatSettings, POR_COMPLETAR
from src.infrastructure.siat.evidence import save_soap_evidence
from src.infrastructure.siat.recepcion import recepcion_factura
from src.infrastructure.siat.stub_client import StubSiatClient
from src.infrastructure.siat.xml_builder import DetalleXml, FacturaXmlInput

LA_PAZ = ZoneInfo("America/La_Paz")


class EmisionValidationError(Exception):
    pass


@dataclass
class EmisionResult:
    factura: Factura
    encolado: bool
    offline: bool = False


def _validar_emision(
    *,
    empresa_nit: str,
    cliente: Cliente,
    productos: list[Producto],
    monto_total: Decimal,
) -> None:
    if not cliente.numero_documento or not str(cliente.numero_documento).strip():
        raise EmisionValidationError("Nominatividad: número de documento requerido.")
    if monto_total <= 0:
        raise EmisionValidationError(
            "El monto total no puede ser 0."
        )
    if cliente.numero_documento == empresa_nit:
        raise EmisionValidationError("No se puede facturar al mismo NIT emisor.")
    for p in productos:
        if not p.codigo_producto_sin:
            raise EmisionValidationError(
                f"Producto {p.codigo_interno} sin código SIN homologado."
            )
        if not str(cliente.numero_documento).isdigit() and cliente.tipo_documento_identidad in (
            1,
            5,
        ):
            raise EmisionValidationError("C.I./NIT deben ser numéricos.")


def _cufd_vigente(empresa_id: int) -> CodigoOperacion:
    cufd = (
        CodigoOperacion.objects.filter(
            empresa_id=empresa_id, tipo=CodigoOperacion.Tipo.CUFD
        )
        .order_by("-created_at")
        .first()
    )
    if not cufd:
        raise EmisionValidationError("No hay CUFD vigente. Obtenga CUFD antes de emitir.")
    return cufd


def emitir_factura(
    *,
    empresa_id: int,
    sucursal_id: int,
    punto_venta_id: int,
    usuario_id: int,
    cliente_id: int,
    lineas: list[dict],
    codigo_sucursal: int = 0,
    codigo_punto_venta: int = 0,
    nit_emisor: str = "123456789",
    razon_social_emisor: str = "Demo",
    municipio: str = "La Paz",
    telefono: str = "",
    direccion: str = "",
    usuario_xml: str = "DEMO",
    leyenda: str = "Leyenda demo Ley 453",
    codigo_excepcion: int = 0,
    forzar_offline: bool = False,
    client: StubSiatClient | None = None,
    sync: bool = True,
    settings: SiatSettings | None = None,
) -> EmisionResult:
    settings = settings or SiatSettings.from_django()
    client = client or StubSiatClient()
    cliente = Cliente.objects.get(pk=cliente_id)
    assert_same_empresa(cliente.empresa_id, empresa_id)

    productos: list[Producto] = []
    detalles_model: list[tuple[Producto, Decimal, Decimal]] = []
    monto = Decimal("0")
    for linea in lineas:
        producto = Producto.objects.get(pk=linea["producto_id"])
        assert_same_empresa(producto.empresa_id, empresa_id)
        cantidad = Decimal(str(linea["cantidad"]))
        descuento = Decimal(str(linea.get("descuento", 0)))
        subtotal = cantidad * producto.precio_unitario - descuento
        productos.append(producto)
        detalles_model.append((producto, cantidad, descuento))
        monto += subtotal

    _validar_emision(
        empresa_nit=nit_emisor,
        cliente=cliente,
        productos=productos,
        monto_total=monto,
    )

    offline = forzar_offline
    if not offline:
        try:
            if not client.verificar_comunicacion("facturacion").ok:
                offline = True
        except SinComunicacionError:
            offline = True

    cufd = _cufd_vigente(empresa_id)
    numero = InvoiceCounter.allocate(empresa_id, sucursal_id, punto_venta_id)
    now = datetime.now(LA_PAZ)
    fecha_str = now.strftime("%Y%m%d%H%M%S") + f"{int(now.microsecond / 1000):03d}"
    tipo_emision = 2 if offline else 1
    excepcion = 1 if offline and cliente.tipo_documento_identidad == 5 else codigo_excepcion

    cuf = generar_cuf_factura(
        nit=int(nit_emisor),
        fecha_hora=fecha_str,
        sucursal=codigo_sucursal,
        modalidad=settings.modalidad,
        tipo_emision=tipo_emision,
        tipo_factura=1,
        documento_sector=1,
        numero_factura=numero,
        punto_venta=codigo_punto_venta,
        codigo_control=cufd.codigo_control,
    )

    factura = Factura.objects.create(
        empresa_id=empresa_id,
        sucursal_id=sucursal_id,
        punto_venta_id=punto_venta_id,
        usuario_id=usuario_id,
        cliente_id=cliente_id,
        numero_factura=numero,
        cuf=cuf,
        cufd=cufd.valor,
        fecha_emision=now,
        codigo_documento_sector=1,
        tipo_factura=1,
        codigo_emision=tipo_emision,
        monto_total=monto,
        monto_total_sujeto_iva=monto,
        moneda=1,
        tipo_cambio=Decimal("1"),
        leyenda=leyenda,
        estado_interno=(
            Factura.EstadoInterno.OFFLINE if offline else Factura.EstadoInterno.LISTA_ENVIO
        ),
        codigo_excepcion=excepcion,
        offline_flag=offline,
    )
    for producto, cantidad, descuento in detalles_model:
        FacturaDetalle.objects.create(
            factura=factura,
            actividad_economica=producto.actividad_economica,
            codigo_producto_sin=producto.codigo_producto_sin,
            codigo_producto=producto.codigo_interno,
            descripcion=producto.descripcion,
            cantidad=cantidad,
            unidad_medida=producto.unidad_medida,
            precio_unitario=producto.precio_unitario,
            descuento=descuento,
            subtotal=cantidad * producto.precio_unitario - descuento,
        )

    xml_input = FacturaXmlInput(
        nit_emisor=nit_emisor,
        razon_social_emisor=razon_social_emisor,
        municipio=municipio,
        telefono=telefono,
        numero_factura=numero,
        cuf=cuf,
        cufd=cufd.valor,
        codigo_sucursal=codigo_sucursal,
        direccion=direccion,
        codigo_punto_venta=codigo_punto_venta,
        fecha_emision=now.isoformat(timespec="milliseconds"),
        nombre_razon_social=cliente.razon_social,
        codigo_tipo_documento_identidad=cliente.tipo_documento_identidad,
        numero_documento=cliente.numero_documento,
        complemento=cliente.complemento,
        codigo_cliente=cliente.codigo_cliente,
        codigo_metodo_pago=1,
        monto_total=monto,
        monto_total_sujeto_iva=monto,
        codigo_moneda=1,
        tipo_cambio=Decimal("1"),
        monto_total_moneda=monto,
        leyenda=leyenda,
        usuario=usuario_xml,
        codigo_excepcion=excepcion,
        codigo_emision=tipo_emision,
        detalles=[
            DetalleXml(
                actividad_economica=p.actividad_economica,
                codigo_producto_sin=p.codigo_producto_sin,
                codigo_producto=p.codigo_interno,
                descripcion=p.descripcion,
                cantidad=cant,
                unidad_medida=p.unidad_medida,
                precio_unitario=p.precio_unitario,
                descuento=desc,
                subtotal=cant * p.precio_unitario - desc,
            )
            for p, cant, desc in detalles_model
        ],
    )
    built = armar_xml_compra_venta(xml_input, validate=True)
    FacturaEvidencia.objects.create(
        empresa_id=empresa_id,
        factura=factura,
        tipo="xml_emision",
        xml=built.xml_bytes.decode("utf-8"),
        xml_gzip=built.compressed.gzip_bytes,
        hash_sha256=built.compressed.sha256_hex,
        metadata={"xsd_missing": built.xsd_missing},
    )

    Auditoria.objects.create(
        empresa_id=empresa_id,
        actor_id=usuario_id,
        accion="emitir_factura",
        entidad="Factura",
        entidad_id=str(factura.pk),
        detalle={"offline": offline, "numero": numero},
    )

    if offline:
        return EmisionResult(factura=factura, encolado=False, offline=True)

    ColaEnvio.objects.create(empresa_id=empresa_id, factura=factura)
    if sync:
        process_envio_factura(factura.id, client=client, settings=settings)
    else:
        enqueue_envio_factura(factura.id)
    factura.refresh_from_db()
    return EmisionResult(factura=factura, encolado=True, offline=False)


def procesar_envio_encolado(
    factura_id: int,
    *,
    client: StubSiatClient | None = None,
    settings: SiatSettings | None = None,
) -> Factura:
    settings = settings or SiatSettings.from_django()
    client = client or StubSiatClient()
    factura = Factura.objects.select_related("empresa").get(pk=factura_id)
    evidencia = factura.evidencias.filter(tipo="xml_emision").order_by("-id").first()
    ctx = SiatAuthContext(
        token=settings.token if settings.token != POR_COMPLETAR else "stub",
        codigo_ambiente=settings.ambiente,
        codigo_sistema=settings.codigo_sistema,
        nit=settings.nit if settings.nit != POR_COMPLETAR else factura.empresa.nit,
        codigo_modalidad=settings.modalidad,
        cuis=None,
    )
    payload = {
        "archivo": evidencia.xml_gzip if evidencia else b"",
        "hashArchivo": evidencia.hash_sha256 if evidencia else "",
        "cuf": factura.cuf,
    }
    result = recepcion_factura(client, ctx, payload)
    exchange = result.get("exchange")
    if exchange:
        save_soap_evidence(
            empresa_id=factura.empresa_id,
            factura_id=factura.id,
            exchange=exchange,
            token=settings.token,
            tipo="recepcion",
        )
    codigo = int(result.get("codigoEstado", 0))
    factura.estado_siat = str(codigo)
    factura.codigo_recepcion = result.get("codigoRecepcion", "") or ""
    if codigo == 908:
        factura.estado_interno = Factura.EstadoInterno.VALIDADA
        factura.errores_siat = []
    elif codigo == 904:
        factura.estado_interno = Factura.EstadoInterno.OBSERVADA
        factura.errores_siat = result.get("mensajesList", [])
    else:
        factura.estado_interno = Factura.EstadoInterno.ENVIADA
        factura.errores_siat = result.get("mensajesList", [])
    factura.save()
    ColaEnvio.objects.filter(factura=factura).update(estado=ColaEnvio.Estado.OK)
    Auditoria.objects.create(
        empresa_id=factura.empresa_id,
        accion="resultado_recepcion",
        entidad="Factura",
        entidad_id=str(factura.pk),
        detalle={"codigoEstado": codigo},
    )
    return factura
