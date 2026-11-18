# Facturador SIAT (demo stub)

Sistema Informático de Facturación multi-tenant para Bolivia — **modalidad Computarizada en Línea (2)**, sector Compra-Venta (1). En demo no se llama al SIN (`SIAT_MODO=stub`).

## Requisitos

- Python 3.12
- Para demo local: **SQLite** (incluido; no hace falta instalar nada)
- Para piloto/producción: PostgreSQL vía `DATABASE_URL`

## Arranque local

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
cp .env.example .env
# Por defecto usa SQLite (db.sqlite3). Si tienes Postgres, cambia DATABASE_URL.
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser   # opcional
python manage.py runserver
```

Demo web: http://127.0.0.1:8000/login/ — usuario `demo` / `demo1234`

## Tests

```bash
pytest
```

## Variables SIAT

Ver `.env.example`. Mientras los WSDL sean `POR_COMPLETAR`, el modo `stub` permite emitir con código 908 simulado. El token **nunca** va al repositorio.

Las URLs WSDL se copian del **reporte oficial de autorización** del SIN (por verificar hasta entonces).

## Cola

Django-Q2 (`python manage.py qcluster` en workers). En demo, el envío corre en línea si no hay worker.

## XSD oficial

Coloca el XSD de Compra-Venta descargado de siatinfo en `schemas/compra_venta.xsd`. Sin él, la validación XSD se omite con mensaje de descarga.
