"""Carga datos de demostración ficticios."""

from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand

from src.infrastructure.db.models import (
    Cliente,
    Empresa,
    Producto,
    PuntoVenta,
    Role,
    Sucursal,
    User,
    UserRole,
)


class Command(BaseCommand):
    help = "Carga datos ficticios para la demo stub"

    def handle(self, *args, **options):
        empresa, _ = Empresa.objects.get_or_create(
            nit="1000001001",
            defaults={
                "razon_social": "Demo PyME Bolivia SRL",
                "municipio": "La Paz",
                "telefono": "70000000",
                "modalidad": 2,
                "ambiente": "POR_COMPLETAR",
            },
        )
        sucursal, _ = Sucursal.objects.get_or_create(
            empresa=empresa,
            codigo_sucursal=0,
            defaults={"direccion": "Av. Demo 123", "municipio": "La Paz"},
        )
        PuntoVenta.objects.get_or_create(
            sucursal=sucursal,
            codigo_punto_venta=0,
            defaults={"nombre": "Caja Demo"},
        )
        user, created = User.objects.get_or_create(
            username="demo",
            defaults={
                "empresa": empresa,
                "nombre_usuario": "DEMOUSER",
                "email": "demo@example.com",
            },
        )
        if created:
            user.set_password("demo1234")
            user.save()
        role, _ = Role.objects.get_or_create(
            empresa=empresa,
            name="cajero",
            defaults={
                "permissions": [
                    Role.Permission.EMITIR,
                    Role.Permission.ANULAR,
                    Role.Permission.VER_XML,
                ]
            },
        )
        UserRole.objects.get_or_create(user=user, role=role)
        Cliente.objects.get_or_create(
            empresa=empresa,
            codigo_cliente="C-DEMO-1",
            defaults={
                "tipo_documento_identidad": 5,
                "numero_documento": "1234567",
                "razon_social": "Cliente Demo",
                "email": "cliente@example.com",
            },
        )
        Producto.objects.get_or_create(
            empresa=empresa,
            codigo_interno="SERV-1",
            defaults={
                "descripcion": "Servicio de consultoría",
                "actividad_economica": "620100",
                "codigo_producto_sin": "83141",
                "unidad_medida": 58,
                "precio_unitario": Decimal("100.00"),
            },
        )
        self.stdout.write(self.style.SUCCESS("Seed demo listo. Usuario: demo / demo1234"))
