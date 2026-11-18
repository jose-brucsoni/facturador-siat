from django.urls import path, re_path

from src.presentation.web import views

urlpatterns = [
    # Assets Vite (assets/*, favicon, etc.) cuando Django sirve el build.
    re_path(r"^(?P<asset_path>(?:assets/|favicon\.).+)$", views.spa_asset, name="spa-asset"),
    # Catch-all SPA (React Router).
    re_path(r"^(?:.*)/?$", views.spa_index, name="spa"),
]
