"""Envío de notificaciones (correo de demo)."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class ConsoleNotifier:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        attachments: list[tuple[str, bytes]] | None = None,
    ) -> None:
        self.sent.append(
            {
                "to": to,
                "subject": subject,
                "body": body,
                "attachments": [name for name, _ in (attachments or [])],
            }
        )
        logger.info("Email demo a %s: %s", to, subject)
