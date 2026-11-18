from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from src.application.use_cases.armar_xml_compra_venta import armar_xml_compra_venta
from src.infrastructure.siat.xml_builder import DetalleXml, FacturaXmlInput
from src.infrastructure.siat.xsd_validator import XSD_DOWNLOAD_URL, xsd_path, validate_xml


def _sample_input(**overrides) -> FacturaXmlInput:
    data = FacturaXmlInput(
        nit_emisor="123456789",
        razon_social_emisor="Demo SA",
        municipio="La Paz",
        telefono="70000000",
        numero_factura=1,
        cuf="ABC",
        cufd="CUFD",
        codigo_sucursal=0,
        direccion="Av. Test",
        codigo_punto_venta=0,
        fecha_emision="2020-02-15T08:40:12.215",
        nombre_razon_social="Cliente Demo",
        codigo_tipo_documento_identidad=5,
        numero_documento="1234567",
        complemento="",
        codigo_cliente="C1",
        codigo_metodo_pago=1,
        monto_total=Decimal("100.00"),
        monto_total_sujeto_iva=Decimal("100.00"),
        codigo_moneda=1,
        tipo_cambio=Decimal("1"),
        monto_total_moneda=Decimal("100.00"),
        leyenda="Leyenda demo",
        usuario="CAJEROA",
        detalles=[
            DetalleXml(
                actividad_economica="620100",
                codigo_producto_sin="83141",
                codigo_producto="P1",
                descripcion="Servicio",
                cantidad=Decimal("1"),
                unidad_medida=58,
                precio_unitario=Decimal("100"),
                descuento=Decimal("0"),
                subtotal=Decimal("100"),
            )
        ],
    )
    for k, v in overrides.items():
        setattr(data, k, v)
    return data


@pytest.mark.django_db
def test_xml_valida_contra_xsd(settings):
    official = xsd_path()
    if not official.is_file() or official.stat().st_size == 0:
        pytest.skip(f"XSD oficial ausente. Descargar: {XSD_DOWNLOAD_URL}")
    result = armar_xml_compra_venta(_sample_input())
    assert result.validation is not None
    assert result.validation.ok, result.validation.errors


@pytest.mark.django_db
def test_xml_invalido_reporta_errores(settings, tmp_path):
    fixture = Path(__file__).resolve().parent.parent / "fixtures" / "minimal_compra_venta.xsd"
    target = tmp_path / "compra_venta.xsd"
    target.write_bytes(fixture.read_bytes())
    settings.SIAT_SCHEMAS_DIR = tmp_path

    xml = build_invalid_xml()
    result = validate_xml(xml)
    assert result.ok is False
    assert result.errors


def build_invalid_xml() -> bytes:
    # Missing required nitEmisor content / empty required field via wrong root.
    return b"<facturaComputarizadaCompraVenta><cabecera></cabecera></facturaComputarizadaCompraVenta>"


@pytest.mark.django_db
def test_sin_xsd_no_inventa_esquema(settings, tmp_path):
    settings.SIAT_SCHEMAS_DIR = tmp_path
    result = armar_xml_compra_venta(_sample_input())
    assert result.xsd_missing is True
    assert "siatinfo" in result.xsd_message
