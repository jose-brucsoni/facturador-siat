"""Tareas en cola para enviar facturas."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def enqueue_envio_factura(factura_id: int, **kwargs: Any) -> str:
    """Encola el envío de una factura."""
    try:
        from django_q.tasks import async_task

        return async_task(
            "src.infrastructure.queue.tasks.process_envio_factura",
            factura_id,
            **kwargs,
        )
    except Exception:  # noqa: BLE001
        logger.info("Django-Q unavailable; processing factura %s inline", factura_id)
        process_envio_factura(factura_id, **kwargs)
        return "inline"


def process_envio_factura(factura_id: int, **kwargs: Any) -> None:
    from src.application.use_cases.emitir_factura import procesar_envio_encolado

    procesar_envio_encolado(factura_id, **kwargs)
