from __future__ import annotations

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from src.application.use_cases.emitir_factura import emitir_factura
from src.application.use_cases.generar_representacion_grafica import (
    generar_representacion_grafica,
)
from src.application.use_cases.listar_facturas import listar_facturas
from src.application.use_cases.obtener_cufd import obtener_cufd
from src.application.use_cases.obtener_cuis import obtener_cuis
from src.infrastructure.db.models import Cliente, Producto, PuntoVenta, Sucursal
from src.infrastructure.siat.config import POR_COMPLETAR, SiatSettings
from src.infrastructure.siat.stub_client import StubSiatClient


@require_http_methods(["GET", "POST"])
def login_page(request: HttpRequest) -> HttpResponse:
    error = ""
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user:
            login(request, user)
            return redirect("web-home")
        error = "Credenciales inválidas"
    return render(request, "web/login.html", {"error": error})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("web-login")


@login_required
def home(request: HttpRequest) -> HttpResponse:
    if not request.user.empresa_id:
        return HttpResponseForbidden("Usuario sin empresa")
    facturas = listar_facturas(empresa_id=request.user.empresa_id)[:20]
    return render(
        request,
        "web/home.html",
        {
            "facturas": facturas,
            "clientes": Cliente.objects.filter(empresa_id=request.user.empresa_id),
            "productos": Producto.objects.filter(empresa_id=request.user.empresa_id),
        },
    )


@login_required
@require_http_methods(["POST"])
def emitir_web(request: HttpRequest) -> HttpResponse:
    empresa = request.user.empresa
    if not empresa.codigos_operacion.filter(tipo="cufd").exists():
        obtener_cuis(empresa_id=empresa.id, client=StubSiatClient())
        obtener_cufd(empresa_id=empresa.id, client=StubSiatClient())
    sucursal = Sucursal.objects.filter(empresa=empresa).first()
    pv = PuntoVenta.objects.filter(sucursal=sucursal).first()
    stub = StubSiatClient()
    stub.emision_codigo = 908
    result = emitir_factura(
        empresa_id=empresa.id,
        sucursal_id=sucursal.id,
        punto_venta_id=pv.id,
        usuario_id=request.user.id,
        cliente_id=int(request.POST["cliente_id"]),
        lineas=[{"producto_id": int(request.POST["producto_id"]), "cantidad": 1}],
        nit_emisor=empresa.nit,
        razon_social_emisor=empresa.razon_social,
        usuario_xml=request.user.nombre_usuario or request.user.username,
        client=stub,
    )
    return redirect("web-factura", pk=result.factura.id)


@login_required
def factura_detalle(request: HttpRequest, pk: int) -> HttpResponse:
    factura = listar_facturas(empresa_id=request.user.empresa_id).filter(pk=pk).first()
    if not factura:
        return HttpResponseForbidden("No encontrado")
    return render(request, "web/factura.html", {"factura": factura})


@login_required
def factura_pdf(request: HttpRequest, pk: int) -> HttpResponse:
    try:
        pdf = generar_representacion_grafica(
            empresa_id=request.user.empresa_id, factura_id=pk, actor_id=request.user.id
        )
    except Exception:  # noqa: BLE001
        return HttpResponseForbidden("No encontrado")
    return HttpResponse(pdf, content_type="application/pdf")


@login_required
def config_page(request: HttpRequest) -> HttpResponse:
    cfg = SiatSettings.from_django()
    items = {
        "SIAT_MODO": cfg.modo,
        "SIAT_AMBIENTE": cfg.ambiente,
        "SIAT_NIT": cfg.nit,
        "SIAT_CODIGO_SISTEMA": cfg.codigo_sistema,
        "SIAT_WSDL_CODIGOS": cfg.wsdl_codigos,
        "SIAT_TOKEN": "configurado"
        if cfg.token and cfg.token != POR_COMPLETAR
        else "faltante",
    }
    return render(request, "web/config.html", {"items": items})
