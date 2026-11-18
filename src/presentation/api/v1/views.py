from __future__ import annotations

from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.application.use_cases.anular_factura import anular_factura
from src.application.use_cases.emitir_factura import emitir_factura
from src.application.use_cases.generar_representacion_grafica import (
    generar_representacion_grafica,
)
from src.application.use_cases.listar_facturas import listar_facturas
from src.application.use_cases.obtener_cufd import obtener_cufd
from src.application.use_cases.obtener_cuis import obtener_cuis
from src.domain.tenancy import TenantIsolationError
from src.infrastructure.db.models import Cliente, Factura, Producto, Sucursal, PuntoVenta
from src.infrastructure.db.repositories import get_for_empresa
from src.infrastructure.siat.config import POR_COMPLETAR, SiatSettings
from src.infrastructure.siat.stub_client import StubSiatClient
from src.presentation.api.permissions import HasEmpresa
from src.presentation.api.serializers import (
    ClienteSerializer,
    EmitirSerializer,
    FacturaSerializer,
    ProductoSerializer,
)


def _client():
    cfg = SiatSettings.from_django()
    if cfg.modo == "stub":
        return StubSiatClient()
    return StubSiatClient()


class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, HasEmpresa]

    def get_queryset(self):
        return Cliente.objects.filter(empresa_id=self.request.user.empresa_id)

    def perform_create(self, serializer):
        serializer.save(empresa_id=self.request.user.empresa_id)


class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, HasEmpresa]

    def get_queryset(self):
        return Producto.objects.filter(empresa_id=self.request.user.empresa_id)

    def perform_create(self, serializer):
        serializer.save(empresa_id=self.request.user.empresa_id)


class FacturaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FacturaSerializer
    permission_classes = [IsAuthenticated, HasEmpresa]

    def get_queryset(self):
        return listar_facturas(empresa_id=self.request.user.empresa_id)

    def retrieve(self, request, *args, **kwargs):
        try:
            factura = get_for_empresa(Factura, request.user.empresa_id, kwargs["pk"])
        except TenantIsolationError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(FacturaSerializer(factura).data)

    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None):
        try:
            pdf = generar_representacion_grafica(
                empresa_id=request.user.empresa_id,
                factura_id=int(pk),
                actor_id=request.user.id,
            )
        except (Factura.DoesNotExist, TenantIsolationError):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return HttpResponse(pdf, content_type="application/pdf")

    @action(detail=True, methods=["get"])
    def xml(self, request, pk=None):
        try:
            factura = get_for_empresa(Factura, request.user.empresa_id, int(pk))
        except TenantIsolationError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        evidencia = factura.evidencias.filter(tipo="xml_emision").order_by("-id").first()
        if not evidencia or not evidencia.xml:
            return Response({"detail": "XML no disponible"}, status=404)
        return HttpResponse(evidencia.xml, content_type="application/xml")

    @action(detail=True, methods=["post"])
    def anular(self, request, pk=None):
        try:
            result = anular_factura(
                empresa_id=request.user.empresa_id,
                factura_id=int(pk),
                motivo_codigo=str(request.data.get("motivo_codigo", "1")),
                motivo_descripcion=str(request.data.get("motivo_descripcion", "")),
                actor_id=request.user.id,
                client=_client(),
            )
        except TenantIsolationError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:  # noqa: BLE001
            return Response({"detail": str(exc)}, status=400)
        if result.fuera_de_plazo:
            return Response(
                {"detail": result.mensaje, "rnd": result.guia_rnd},
                status=400,
            )
        return Response({"ok": True, "mensaje": result.mensaje})


class EmitirView(APIView):
    permission_classes = [IsAuthenticated, HasEmpresa]

    def post(self, request):
        ser = EmitirSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        empresa = request.user.empresa
        try:
            Sucursal.objects.get(pk=data["sucursal_id"], empresa_id=empresa.id)
            PuntoVenta.objects.get(
                pk=data["punto_venta_id"], sucursal__empresa_id=empresa.id
            )
        except (Sucursal.DoesNotExist, PuntoVenta.DoesNotExist):
            return Response({"detail": "Sucursal/PV no encontrados"}, status=404)

        if not empresa.codigos_operacion.filter(tipo="cufd").exists():
            obtener_cuis(empresa_id=empresa.id, client=_client())
            obtener_cufd(empresa_id=empresa.id, client=_client())

        stub = _client()
        if isinstance(stub, StubSiatClient):
            stub.emision_codigo = 908

        result = emitir_factura(
            empresa_id=empresa.id,
            sucursal_id=data["sucursal_id"],
            punto_venta_id=data["punto_venta_id"],
            usuario_id=request.user.id,
            cliente_id=data["cliente_id"],
            lineas=data["lineas"],
            nit_emisor=empresa.nit,
            razon_social_emisor=empresa.razon_social,
            municipio=empresa.municipio,
            telefono=empresa.telefono,
            usuario_xml=request.user.nombre_usuario or request.user.username,
            client=stub,
            sync=True,
        )
        pdf_url = f"/api/v1/facturas/{result.factura.id}/pdf/"
        return Response(
            {
                "id": result.factura.id,
                "estado_interno": result.factura.estado_interno,
                "estado_siat": result.factura.estado_siat,
                "cuf": result.factura.cuf,
                "numero_factura": result.factura.numero_factura,
                "pdf_url": pdf_url,
                "offline": result.offline,
            },
            status=201,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasEmpresa])
def config_status(request):
    cfg = SiatSettings.from_django()
    keys = {
        "SIAT_MODO": cfg.modo,
        "SIAT_AMBIENTE": cfg.ambiente,
        "SIAT_NIT": cfg.nit,
        "SIAT_CODIGO_SISTEMA": cfg.codigo_sistema,
        "SIAT_WSDL_CODIGOS": cfg.wsdl_codigos,
        "SIAT_WSDL_SINCRONIZACION": cfg.wsdl_sincronizacion,
        "SIAT_WSDL_OPERACIONES": cfg.wsdl_operaciones,
        "SIAT_WSDL_FACTURACION": cfg.wsdl_facturacion,
        "SIAT_TOKEN": "configurado"
        if cfg.token and cfg.token != POR_COMPLETAR
        else "faltante",
    }
    return Response(
        {
            "completitud": {
                k: ("ok" if v not in (POR_COMPLETAR, "faltante") else "POR_COMPLETAR")
                for k, v in keys.items()
            },
            "valores_seguros": keys,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    from django.contrib.auth import authenticate, login

    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({"detail": "Credenciales inválidas"}, status=400)
    login(request, user)
    return Response(
        {
            "username": user.username,
            "empresa_id": user.empresa_id,
        }
    )
