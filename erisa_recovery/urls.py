from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # Mount claims with an explicit namespace
    path("", include(("backend.urls", "claims"), namespace="claims")),
]
