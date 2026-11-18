"""Sin URLs configuradas no se llama a la red."""

from __future__ import annotations

import pytest

from src.application.use_cases.obtener_cuis import obtener_cuis
from src.domain.siat_ports import WsdlNotConfiguredError
from src.infrastructure.siat.config import SiatSettings
from src.infrastructure.siat.soap_client import SiatSoapClient


def _settings(**overrides) -> SiatSettings:
    base = dict(
        modo="real",
        ambiente="2",
        nit="123",
        codigo_sistema="SYS",
        modalidad=2,
        codigo_sucursal="0",
        codigo_punto_venta="0",
        token="secret-token-value-xyz",
        wsdl_codigos="POR_COMPLETAR",
        wsdl_sincronizacion="POR_COMPLETAR",
        wsdl_operaciones="POR_COMPLETAR",
        wsdl_facturacion="POR_COMPLETAR",
        qr_base_url="https://pilotosiat.impuestos.gob.bo/consulta/QR",
        timeout_seconds=5,
    )
    base.update(overrides)
    return SiatSettings(**base)


@pytest.mark.django_db
def test_wsdl_missing_no_network(empresa_a, monkeypatch):
    called = {"http": False}

    def boom(*args, **kwargs):
        called["http"] = True
        raise AssertionError("No debe haber llamada HTTP")

    monkeypatch.setattr("zeep.Client", boom)
    settings = _settings()
    with pytest.raises(WsdlNotConfiguredError, match="reporte oficial"):
        obtener_cuis(empresa_id=empresa_a.id, settings=settings, client=SiatSoapClient(settings))
    assert called["http"] is False


def test_require_wsdl_on_verificar():
    client = SiatSoapClient(_settings())
    with pytest.raises(WsdlNotConfiguredError):
        client.verificar_comunicacion("codigos")
