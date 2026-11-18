"""Simulador del SIN para la demo (sin red)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from src.domain.siat_ports import (
    CatalogItem,
    CatalogSyncResult,
    ComunicacionResult,
    CufdResult,
    CuisResult,
    SiatAuthContext,
    SoapExchange,
)


def _exchange(method: str, resource: str, body: str = "<ok/>") -> SoapExchange:
    return SoapExchange(
        request_xml=f"<request method='{method}'/>",
        response_xml=body,
        method=method,
        resource=resource,
    )


class StubSiatClient:
    """Cliente falso con respuestas de prueba."""

    def __init__(self, comunicacion_ok: bool = True) -> None:
        self.comunicacion_ok = comunicacion_ok
        self.calls: list[str] = []
        self.emision_codigo: int = 908
        self.anulacion_codigo: int = 905
        self.estado_codigo: int = 908
        self.paquete_recepcion_codigo: int = 901
        self.paquete_validacion_codigo: int = 908

    def verificar_comunicacion(self, resource: str = "codigos") -> ComunicacionResult:
        self.calls.append(f"verificarComunicacion:{resource}")
        if not self.comunicacion_ok:
            return ComunicacionResult(
                ok=False,
                resource=resource,
                exchange=_exchange("verificarComunicacion", resource, "<false/>"),
                detail="stub sin comunicación",
            )
        return ComunicacionResult(
            ok=True,
            resource=resource,
            exchange=_exchange("verificarComunicacion", resource, "<true/>"),
        )

    def obtener_cuis(self, ctx: SiatAuthContext) -> CuisResult:
        self.calls.append("cuis")
        now = datetime.now(timezone.utc)
        return CuisResult(
            codigo="STUB-CUIS-001",
            vigencia_hasta=now + timedelta(days=365),
            exchange=_exchange("cuis", "codigos", "<cuis>STUB-CUIS-001</cuis>"),
            mensaje_codigo=None,
        )

    def solicitar_cufd(self, ctx: SiatAuthContext) -> CufdResult:
        self.calls.append("solicitudCufd")
        now = datetime.now(timezone.utc)
        return CufdResult(
            codigo="STUB-CUFD-001",
            codigo_control="A19E23EF34124CD",
            vigencia_hasta=now + timedelta(hours=24),
            exchange=_exchange(
                "solicitudCufd",
                "codigos",
                "<cufd>STUB-CUFD-001</cufd>",
            ),
        )

    def sincronizar(self, ctx: SiatAuthContext, metodo: str) -> CatalogSyncResult:
        self.calls.append(metodo)
        catalog_map = {
            "sincronizarListaLeyendasFactura": [
                CatalogItem(
                    "leyendas",
                    "1",
                    "Ley N° 453: El proveedor de productos o servicios debe "
                    "habilitar la recepción de reclamos.",
                ),
            ],
            "sincronizarParametricaTipoFactura": [
                CatalogItem("tipo_factura", "1", "Factura con derecho a crédito fiscal"),
            ],
            "sincronizarParametricaTipoMetodoPago": [
                CatalogItem("metodo_pago", "1", "Efectivo"),
                CatalogItem("metodo_pago", "2", "Tarjeta"),
            ],
        }
        items = catalog_map.get(
            metodo, [CatalogItem(tipo=metodo, codigo="0", descripcion="stub")]
        )
        return CatalogSyncResult(
            items=items,
            exchange=_exchange(metodo, "sincronizacion"),
        )

    def recepcion_factura(self, ctx: SiatAuthContext, payload: dict[str, Any]) -> dict:
        self.calls.append("recepcionFactura")
        return {
            "transaccion": self.emision_codigo == 908,
            "codigoEstado": self.emision_codigo,
            "codigoRecepcion": "REC-STUB-001" if self.emision_codigo == 908 else "",
            "mensajesList": (
                []
                if self.emision_codigo == 908
                else [{"codigo": 1013, "descripcion": "Observación stub"}]
            ),
            "exchange": _exchange("recepcionFactura", "facturacion"),
        }

    def verificacion_estado_factura(self, ctx: SiatAuthContext, cuf: str) -> dict:
        self.calls.append("verificacionEstadoFactura")
        return {
            "codigoEstado": self.estado_codigo,
            "cuf": cuf,
            "exchange": _exchange("verificacionEstadoFactura", "facturacion"),
        }

    def anular_factura(self, ctx: SiatAuthContext, payload: dict[str, Any]) -> dict:
        self.calls.append("anulacionFactura")
        return {
            "codigoEstado": self.anulacion_codigo,
            "codigoRecepcion": "ANUL-STUB-001",
            "exchange": _exchange("anulacionFactura", "facturacion"),
        }

    def recepcion_paquete(self, ctx: SiatAuthContext, payload: dict[str, Any]) -> dict:
        self.calls.append("recepcionPaquete")
        return {
            "codigoEstado": self.paquete_recepcion_codigo,
            "codigoRecepcion": "PKG-STUB-001",
            "exchange": _exchange("recepcionPaquete", "facturacion"),
        }

    def validacion_paquete(self, ctx: SiatAuthContext, codigo_recepcion: str) -> dict:
        self.calls.append("validacionPaquete")
        return {
            "codigoEstado": self.paquete_validacion_codigo,
            "codigoRecepcion": codigo_recepcion,
            "exchange": _exchange("validacionPaquete", "facturacion"),
        }
