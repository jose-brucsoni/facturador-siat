from django.urls import include, path

urlpatterns = [
    path("v1/", include("src.presentation.api.v1.urls")),
]
