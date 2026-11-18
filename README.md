# Facturador SIAT (demo)

Proyecto de portafolio: sistema de facturación electrónica para Bolivia alineado con el SIAT (Servicio de Impuestos Nacionales), en modalidad **Computarizada en Línea (código 2)** y documento sector **Compra-Venta (1)**.

Corre en modo **stub**: simula respuestas del SIN sin llamar a Impuestos Nacionales ni usar datos reales.

## Disclaimer

- **No** está homologado ante el SIN.
- **No** es un producto listo para producción fiscal.
- Es una demostración de arquitectura, dominio fiscal boliviano y buenas prácticas (multi-tenant, evidencias, tests).

## Qué demuestra

- Multi-empresa con aislamiento de datos (anti-IDOR)
- Emisión Compra-Venta (CUF, XML, Gzip/SHA-256, PDF con QR)
- Anulación con control de plazo
- Contingencia offline y paquetes (máx. 500)
- API REST (DRF) + UI mínima
- Cola de envíos (Django-Q2)
- Suite de pruebas con pytest

## Stack

| Pieza | Tecnología |
|-------|------------|
| Lenguaje | Python 3.12 |
| Web / API | Django LTS + Django REST Framework |
| DB demo | SQLite (Postgres vía `DATABASE_URL`) |
| SIAT | zeep (SOAP), lxml, stub inyectable |
| PDF / QR | ReportLab + qrcode |
| Cola | Django-Q2 |
| Tests | pytest + pytest-django |

## Arquitectura

Clean Architecture:

```
src/domain/           # reglas y puertos (sin Django)
src/application/      # casos de uso
src/infrastructure/   # DB, SIAT, PDF, cola
src/presentation/     # API y web
```

El conector SIAT vive solo en `src/infrastructure/siat/`.

## Arranque local

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

- Web: http://127.0.0.1:8000/login/
- Usuario demo: `demo` / `demo1234`

```bash
pytest
```

## Configuración SIAT

Variables en `.env.example` (`SIAT_*`). Con `SIAT_MODO=stub` no hace falta token ni WSDL reales. El token **nunca** debe ir al repositorio (ver [SECURITY.md](SECURITY.md)).

Opcional: colocar el XSD oficial de Compra-Venta en `schemas/compra_venta.xsd` (descarga desde siatinfo). Sin él, la validación XSD se omite en demo.

## Licencia

[MIT](LICENSE) © 2026 Jose Carlo Brucsoni
