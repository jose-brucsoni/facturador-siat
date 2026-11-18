from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from . import models


@admin.register(models.User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Empresa", {"fields": ("empresa", "nombre_usuario", "activo")}),
    )
    list_filter = ("empresa", "is_staff", "activo")
    list_display = ("username", "email", "empresa", "nombre_usuario", "is_staff")


@admin.register(models.Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nit", "razon_social", "modalidad", "estado")
    search_fields = ("nit", "razon_social")


class TenantAdmin(admin.ModelAdmin):
    """Admin limitado a la empresa del usuario."""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or not getattr(request.user, "empresa_id", None):
            return qs
        if hasattr(qs.model, "empresa_id"):
            return qs.filter(empresa_id=request.user.empresa_id)
        return qs


@admin.register(models.Sucursal)
class SucursalAdmin(TenantAdmin):
    list_display = ("codigo_sucursal", "direccion", "empresa", "activa")


@admin.register(models.PuntoVenta)
class PuntoVentaAdmin(admin.ModelAdmin):
    list_display = ("codigo_punto_venta", "nombre", "sucursal", "activo")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or not getattr(request.user, "empresa_id", None):
            return qs
        return qs.filter(sucursal__empresa_id=request.user.empresa_id)


@admin.register(models.Cliente)
class ClienteAdmin(TenantAdmin):
    list_display = ("codigo_cliente", "razon_social", "numero_documento", "empresa")


@admin.register(models.Producto)
class ProductoAdmin(TenantAdmin):
    list_display = ("codigo_interno", "descripcion", "precio_unitario", "empresa")


@admin.register(models.Factura)
class FacturaAdmin(TenantAdmin):
    list_display = (
        "numero_factura",
        "empresa",
        "estado_interno",
        "estado_siat",
        "cuf",
        "fecha_emision",
    )
    readonly_fields = ("cuf", "codigo_recepcion")


admin.site.register(models.FacturaDetalle)
admin.site.register(models.Role)
admin.site.register(models.CodigoOperacion)
admin.site.register(models.CatalogoSiat)
admin.site.register(models.FacturaEvidencia)
admin.site.register(models.EventoSignificativo)
admin.site.register(models.Paquete)
admin.site.register(models.ColaEnvio)
admin.site.register(models.Anulacion)
admin.site.register(models.NotaCreditoDebito)
admin.site.register(models.Auditoria)
