from django.urls import include, path
from rest_framework.routers import DefaultRouter

from src.presentation.api.v1 import views

router = DefaultRouter()
router.register("clientes", views.ClienteViewSet, basename="clientes")
router.register("productos", views.ProductoViewSet, basename="productos")
router.register("facturas", views.FacturaViewSet, basename="facturas")

urlpatterns = [
    path("login/", views.login_view, name="api-login"),
    path("emitir/", views.EmitirView.as_view(), name="api-emitir"),
    path("config/", views.config_status, name="api-config"),
    path("", include(router.urls)),
]
