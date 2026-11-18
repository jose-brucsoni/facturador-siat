from django.urls import path

from src.presentation.web import views

urlpatterns = [
    path("login/", views.login_page, name="web-login"),
    path("logout/", views.logout_view, name="web-logout"),
    path("", views.home, name="web-home"),
    path("emitir/", views.emitir_web, name="web-emitir"),
    path("facturas/<int:pk>/", views.factura_detalle, name="web-factura"),
    path("facturas/<int:pk>/pdf/", views.factura_pdf, name="web-factura-pdf"),
    path("config/", views.config_page, name="web-config"),
]
