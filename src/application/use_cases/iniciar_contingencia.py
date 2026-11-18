"""Inicia emisión fuera de línea si falla el SIN."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from src.infrastructure.db.models import EventoSignificativo
from src.infrastructure.siat.stub_client import StubSiatClient

EVENTOS_OFFLINE_AUTO = {1, 2, 3, 4}
EVENTOS_CAFC = {5, 6, 7}


@dataclass
class ContingenciaEstado:
    activa: bool
    evento: EventoSignificativo | None
    cufd_contingencia: str


def iniciar_contingencia(
    *,
    empresa_id: int,
    codigo_motivo: int,
    cufd_contingencia: str,
    descripcion: str = "",
    client: StubSiatClient | None = None,
) -> ContingenciaEstado:
    if codigo_motivo in EVENTOS_CAFC:
        evento = EventoSignificativo.objects.create(
            empresa_id=empresa_id,
            codigo_motivo=codigo_motivo,
            descripcion=descripcion or "Evento 5–7: requiere CAFC/Portal (manual)",
            fecha_inicio=datetime.now(timezone.utc),
            cufd_contingencia=cufd_contingencia,
        )
        return ContingenciaEstado(
            activa=True, evento=evento, cufd_contingencia=cufd_contingencia
        )

    if codigo_motivo not in EVENTOS_OFFLINE_AUTO:
        raise ValueError(f"Motivo de evento no soportado: {codigo_motivo}")

    evento = EventoSignificativo.objects.create(
        empresa_id=empresa_id,
        codigo_motivo=codigo_motivo,
        descripcion=descripcion or f"Contingencia automática evento {codigo_motivo}",
        fecha_inicio=datetime.now(timezone.utc),
        cufd_contingencia=cufd_contingencia,
    )
    return ContingenciaEstado(
        activa=True, evento=evento, cufd_contingencia=cufd_contingencia
    )


def detectar_failover(
    *,
    empresa_id: int,
    cufd_vigente: str,
    client: StubSiatClient,
    codigo_motivo: int = 1,
) -> ContingenciaEstado | None:
    """Si no hay comunicación, abre contingencia."""
    result = client.verificar_comunicacion("facturacion")
    if result.ok:
        return None
    return iniciar_contingencia(
        empresa_id=empresa_id,
        codigo_motivo=codigo_motivo,
        cufd_contingencia=cufd_vigente,
        client=client,
    )
