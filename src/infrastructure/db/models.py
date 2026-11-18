"""Modelos de datos del facturador."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class Empresa(models.Model):
    nit = models.CharField(max_length=20, unique=True)
    razon_social = models.CharField(max_length=255)
    municipio = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    modalidad = models.PositiveSmallIntegerField(default=2)
    codigo_sistema = models.CharField(max_length=100, blank=True, default="")
    ambiente = models.CharField(max_length=20, blank=True, default="POR_COMPLETAR")
    estado = models.CharField(max_length=20, default="activa")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self) -> str:
        return f"{self.razon_social} ({self.nit})"


class Sucursal(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="sucursales")
    codigo_sucursal = models.PositiveIntegerField(help_text="0 = Casa Matriz")
    direccion = models.CharField(max_length=255)
    municipio = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"
        unique_together = [("empresa", "codigo_sucursal")]

    def __str__(self) -> str:
        return f"Sucursal {self.codigo_sucursal} — {self.empresa_id}"


class PuntoVenta(models.Model):
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name="puntos_venta")
    codigo_punto_venta = models.PositiveIntegerField()
    tipo = models.CharField(max_length=50, blank=True, default="")
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True, default="")
    fecha_alta = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Punto de venta"
        verbose_name_plural = "Puntos de venta"
        unique_together = [("sucursal", "codigo_punto_venta")]

    @property
    def empresa_id(self) -> int:
        return self.sucursal.empresa_id

    def __str__(self) -> str:
        return f"PV {self.codigo_punto_venta} — {self.nombre}"


class User(AbstractUser):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name="usuarios",
        null=True,
        blank=True,
    )
    nombre_usuario = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Nombre corto del cajero en la factura.",
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


class Role(models.Model):
    class Permission(models.TextChoices):
        EMITIR = "emitir", "Emitir"
        ANULAR = "anular", "Anular"
        REVERTIR = "revertir", "Revertir"
        VER_XML = "ver_xml", "Ver XML"
        CONFIGURAR_SIAT = "configurar_siat", "Configurar SIAT"

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="roles")
    name = models.CharField(max_length=50)
    permissions = models.JSONField(default=list)

    class Meta:
        unique_together = [("empresa", "name")]

    def __str__(self) -> str:
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles")

    class Meta:
        unique_together = [("user", "role")]


class Cliente(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="clientes")
    codigo_cliente = models.CharField(max_length=50)
    tipo_documento_identidad = models.PositiveSmallIntegerField()
    numero_documento = models.CharField(max_length=30)
    complemento = models.CharField(max_length=10, blank=True, default="")
    razon_social = models.CharField(max_length=255)
    email = models.EmailField(blank=True, default="")
    nit_validado = models.BooleanField(default=False)

    class Meta:
        unique_together = [("empresa", "codigo_cliente")]
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self) -> str:
        return f"{self.razon_social} ({self.codigo_cliente})"


class Producto(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="productos")
    codigo_interno = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)
    actividad_economica = models.CharField(max_length=20)
    codigo_producto_sin = models.CharField(max_length=30)
    unidad_medida = models.PositiveSmallIntegerField()
    precio_unitario = models.DecimalField(max_digits=18, decimal_places=5)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = [("empresa", "codigo_interno")]
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self) -> str:
        return f"{self.codigo_interno} — {self.descripcion}"


class InvoiceCounter(models.Model):
    """Contador del número de factura por punto de venta."""

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    punto_venta = models.ForeignKey(PuntoVenta, on_delete=models.CASCADE)
    last_number = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [("empresa", "sucursal", "punto_venta")]

    @classmethod
    def allocate(cls, empresa_id: int, sucursal_id: int, punto_venta_id: int) -> int:
        """Obtiene el siguiente número de factura."""
        with transaction.atomic():
            counter, _ = cls.objects.select_for_update().get_or_create(
                empresa_id=empresa_id,
                sucursal_id=sucursal_id,
                punto_venta_id=punto_venta_id,
                defaults={"last_number": 0},
            )
            counter.last_number = int(counter.last_number) + 1
            counter.save(update_fields=["last_number"])
            return int(counter.last_number)


class Factura(models.Model):
    class EstadoInterno(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        LISTA_ENVIO = "lista_envio", "Lista para envío"
        ENVIADA = "enviada", "Enviada"
        VALIDADA = "validada", "Validada"
        OBSERVADA = "observada", "Observada"
        ANULADA = "anulada", "Anulada"
        OFFLINE = "offline", "Fuera de línea"

    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="facturas")
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name="facturas")
    punto_venta = models.ForeignKey(PuntoVenta, on_delete=models.PROTECT, related_name="facturas")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="facturas"
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="facturas")
    numero_factura = models.PositiveIntegerField(null=True, blank=True)
    cuf = models.CharField(max_length=100, blank=True, default="")
    cufd = models.CharField(max_length=100, blank=True, default="")
    fecha_emision = models.DateTimeField(null=True, blank=True)
    codigo_documento_sector = models.PositiveSmallIntegerField(default=1)
    tipo_factura = models.PositiveSmallIntegerField(default=1)
    codigo_emision = models.PositiveSmallIntegerField(default=1)
    monto_total = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"))
    monto_total_sujeto_iva = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0")
    )
    descuentos = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"))
    moneda = models.PositiveSmallIntegerField(default=1)
    tipo_cambio = models.DecimalField(max_digits=18, decimal_places=5, default=Decimal("1"))
    leyenda = models.CharField(max_length=500, blank=True, default="")
    estado_interno = models.CharField(
        max_length=30, choices=EstadoInterno.choices, default=EstadoInterno.BORRADOR
    )
    estado_siat = models.CharField(max_length=20, blank=True, default="")
    codigo_recepcion = models.CharField(max_length=100, blank=True, default="")
    codigo_excepcion = models.PositiveSmallIntegerField(default=0)
    offline_flag = models.BooleanField(default=False)
    errores_siat = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        indexes = [
            models.Index(fields=["empresa", "numero_factura"]),
            models.Index(fields=["empresa", "cuf"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "sucursal", "punto_venta", "numero_factura"],
                name="uniq_factura_numero_por_pv",
                condition=models.Q(numero_factura__isnull=False),
            )
        ]

    def clean(self) -> None:
        if self.estado_interno != self.EstadoInterno.BORRADOR:
            if not all([self.empresa_id, self.sucursal_id, self.punto_venta_id]):
                raise ValidationError(
                    "Una emisión requiere empresa, sucursal y punto de venta."
                )

    def __str__(self) -> str:
        return f"Factura {self.numero_factura or 'borrador'} ({self.empresa_id})"


class FacturaDetalle(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="detalles")
    actividad_economica = models.CharField(max_length=20)
    codigo_producto_sin = models.CharField(max_length=30)
    codigo_producto = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=18, decimal_places=5)
    unidad_medida = models.PositiveSmallIntegerField()
    precio_unitario = models.DecimalField(max_digits=18, decimal_places=5)
    descuento = models.DecimalField(max_digits=18, decimal_places=5, default=Decimal("0"))
    subtotal = models.DecimalField(max_digits=18, decimal_places=5)
    # Solo máscara de tarjeta, nunca el número completo.
    numero_tarjeta_mascara = models.CharField(max_length=20, blank=True, default="")

    class Meta:
        verbose_name = "Detalle de factura"
        verbose_name_plural = "Detalles de factura"


class CodigoOperacion(models.Model):
    class Tipo(models.TextChoices):
        CUIS = "cuis", "CUIS"
        CUFD = "cufd", "CUFD"

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="codigos_operacion")
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, null=True, blank=True)
    punto_venta = models.ForeignKey(PuntoVenta, on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    valor = models.CharField(max_length=100)
    codigo_control = models.CharField(max_length=100, blank=True, default="")
    vigencia_desde = models.DateTimeField(null=True, blank=True)
    vigencia_hasta = models.DateTimeField(null=True, blank=True)
    raw_request = models.TextField(blank=True, default="")
    raw_response = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Código de operación"
        verbose_name_plural = "Códigos de operación"


class TokenSiat(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="tokens_siat")
    token_cifrado = models.TextField()
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"TokenSiat(empresa={self.empresa_id}, activo={self.activo})"


class CatalogoSiat(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="catalogos")
    tipo = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=500, blank=True, default="")
    json_extra = models.JSONField(default=dict, blank=True)
    fecha = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("empresa", "tipo", "codigo")]


class FacturaEvidencia(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="evidencias")
    factura = models.ForeignKey(
        Factura, on_delete=models.CASCADE, related_name="evidencias", null=True, blank=True
    )
    tipo = models.CharField(max_length=50)
    xml = models.TextField(blank=True, default="")
    xml_gzip = models.BinaryField(null=True, blank=True)
    hash_sha256 = models.CharField(max_length=64, blank=True, default="")
    soap_request = models.TextField(blank=True, default="")
    soap_response = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class EventoSignificativo(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="eventos")
    codigo_motivo = models.PositiveSmallIntegerField()
    descripcion = models.CharField(max_length=255, blank=True, default="")
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    cufd_contingencia = models.CharField(max_length=100, blank=True, default="")
    cufd_envio = models.CharField(max_length=100, blank=True, default="")
    registrado_siat = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Paquete(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="paquetes")
    evento = models.ForeignKey(
        EventoSignificativo, on_delete=models.SET_NULL, null=True, blank=True
    )
    codigo_recepcion = models.CharField(max_length=100, blank=True, default="")
    estado_siat = models.CharField(max_length=20, blank=True, default="")
    hash_sha256 = models.CharField(max_length=64, blank=True, default="")
    contenido_gzip = models.BinaryField(null=True, blank=True)
    cantidad_facturas = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class ColaEnvio(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        PROCESANDO = "procesando", "Procesando"
        OK = "ok", "OK"
        ERROR = "error", "Error"

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="cola_envios")
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="cola_envios")
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    intentos = models.PositiveIntegerField(default=0)
    ultimo_error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Anulacion(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="anulaciones")
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="anulaciones")
    motivo_codigo = models.CharField(max_length=20)
    motivo_descripcion = models.CharField(max_length=255, blank=True, default="")
    estado_siat = models.CharField(max_length=20, blank=True, default="")
    codigo_recepcion = models.CharField(max_length=100, blank=True, default="")
    notificado_comprador = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )


class NotaCreditoDebito(models.Model):
    """Nota crédito-débito (pendiente)."""

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="notas_cd")
    factura_origen = models.ForeignKey(
        Factura, on_delete=models.PROTECT, related_name="notas_cd"
    )
    numero = models.PositiveIntegerField(null=True, blank=True)
    cuf = models.CharField(max_length=100, blank=True, default="")
    estado_interno = models.CharField(max_length=30, default="no_implementado")
    created_at = models.DateTimeField(auto_now_add=True)


class Auditoria(models.Model):
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="auditorias", null=True, blank=True
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    accion = models.CharField(max_length=100)
    entidad = models.CharField(max_length=50)
    entidad_id = models.CharField(max_length=50, blank=True, default="")
    detalle = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
