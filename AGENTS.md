# Facturador SIAT — Reglas del agente

Demo multi-tenant de facturación para PyMEs (Bolivia). Módulo base: Sistema Informático de Facturación orientado al SIAT (Servicio de Impuestos Nacionales).

## Objetivo

Desarrollar un facturador en modalidad **Computarizada en Línea (código 2)**, documento sector **Compra-Venta (1)**, tipo factura con derecho a crédito fiscal **(1)**. XMLDSig / modalidad Electrónica quedan fuera del MVP.

## Stack (obligatorio)

- Python **3.12** (pinneado en `pyproject.toml`)
- Django LTS + Django REST Framework
- SQLite en demo local; PostgreSQL vía `DATABASE_URL`; SQL Server solo si la URL lo indica
- zeep (SOAP), lxml (XML/XSD), signxml (interfaz lista; no firmar en MVP)
- ReportLab + qrcode (PDF/QR)
- Django-Q2 (cola de envíos)
- pytest

**No usar C# ni .NET.**

## Arquitectura

Clean Architecture:

- `src/domain/` — entidades, value objects, puertos (sin imports Django)
- `src/application/` — casos de uso
- `src/infrastructure/` — DB, SIAT (SOAP), PDF, cola
- `src/presentation/` — API DRF y UI mínima

Multi-tenant desde el día 1: toda fila de negocio lleva `empresa_id` (y sucursal/punto de venta cuando aplique). Una empresa nunca consulta datos de otra.

El conector SIAT está aislado detrás de interfaces (puertos). El resto de la app **no** conoce SOAP, WSDL, CUFD ni XSD. Único lugar que habla con el SIN: `src/infrastructure/siat/`.

## Configuración

Nada hardcodeado. Ambiente, NIT, `codigo_sistema`, modalidad, sucursal, punto de venta, WSDL/URLs, timeouts: solo settings / variables de entorno.

- Token delegado y secretos: solo entorno. Nunca en el repo, logs ni evidencias sin cifrar.
- Si falta un valor oficial: placeholder `POR_COMPLETAR` o «por verificar».
- **No inventar** URLs, WSDL, códigos RND, `codigoAmbiente` ni nombres de métodos SOAP no confirmados en siatinfo o en el reporte de autorización del SIN.
- Las URLs WSDL se copian del **reporte oficial de autorización** del SIN (por verificar hasta entonces).
- `SIAT_MODO=stub|real` (default stub en demo).

`codigoAmbiente` (por verificar): varias páginas oficiales usan 1 = Producción y 2 = Pruebas y Piloto; la de catálogos lista 1, 2 y 3. Leer de `SIAT_AMBIENTE`.

## Evidencias y auditoría

Registrar cada request/response al SIN (SOAP crudo), XML, Gzip, SHA-256, CUF, código de recepción y estados, de forma inmutable y asociados a empresa/factura.

`.env` en `.gitignore`. Usar `.env.example` sin secretos reales.

## Calidad

- Nombres de código en inglés; mensajes de negocio en español.
- Type hints. Tests pytest por caso de uso, incluido aislamiento entre empresas.
- Cola de envíos (Django-Q2) para no bloquear la caja si el SIN está lento.
- Permisos distintos: emitir, anular, revertir, configurar SIAT, ver XML.

## Superusuario de desarrollo

Crear solo por comando documentado, nunca hardcodeado:

```bash
python manage.py createsuperuser
```

## Estructura

```
facturador-siat/
  AGENTS.md
  .cursor/rules/siat.mdc
  .env.example
  src/domain|application|infrastructure|presentation
  schemas/          # XSD oficial (aportado por quien homologa; no inventar)
  tests/
```
