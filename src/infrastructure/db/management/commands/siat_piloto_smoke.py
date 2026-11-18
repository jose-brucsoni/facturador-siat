"""Prueba rápida de configuración para el piloto."""

from __future__ import annotations

import os

from django.core.management.base import BaseCommand, CommandError

from src.infrastructure.siat.config import POR_COMPLETAR, SiatSettings


class Command(BaseCommand):
    help = "Smoke opcional contra piloto SIAT (no usar en CI)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--subset",
            default="cuis",
            help="Subconjunto: cuis|cufd|comunicacion (no dispares 500 emisiones)",
        )

    def handle(self, *args, **options):
        if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
            raise CommandError("Negado: no ejecutar siat_piloto_smoke en CI.")

        cfg = SiatSettings.from_django()
        if cfg.modo != "real":
            raise CommandError("SIAT_MODO debe ser 'real' para smoke de piloto.")
        if cfg.wsdl_codigos == POR_COMPLETAR or cfg.token == POR_COMPLETAR:
            raise CommandError(
                "Falta WSDL/token. Pégalos desde el reporte oficial (no inventar)."
            )

        subset = options["subset"]
        self.stdout.write(
            self.style.WARNING(
                f"Smoke '{subset}' listo. Token: configurado (no se imprime)."
            )
        )
        self.stdout.write("OK — configuración mínima presente. Ejecuta casos del checklist.")
