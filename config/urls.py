"""Rutas principales del proyecto."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("src.presentation.api.urls")),
    path("", include("src.presentation.web.urls")),
]
