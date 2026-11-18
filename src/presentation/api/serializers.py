from __future__ import annotations

from rest_framework import serializers

from src.infrastructure.db.models import Cliente, Factura, Producto


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = (
            "id",
            "codigo_cliente",
            "tipo_documento_identidad",
            "numero_documento",
            "complemento",
            "razon_social",
            "email",
            "nit_validado",
        )
        read_only_fields = ("id",)


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = (
            "id",
            "codigo_interno",
            "descripcion",
            "actividad_economica",
            "codigo_producto_sin",
            "unidad_medida",
            "precio_unitario",
            "activo",
        )
        read_only_fields = ("id",)


class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = (
            "id",
            "numero_factura",
            "cuf",
            "fecha_emision",
            "monto_total",
            "estado_interno",
            "estado_siat",
            "codigo_recepcion",
            "errores_siat",
            "cliente",
            "offline_flag",
        )


class EmitirSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()
    lineas = serializers.ListField(child=serializers.DictField(), min_length=1)
    sucursal_id = serializers.IntegerField()
    punto_venta_id = serializers.IntegerField()
