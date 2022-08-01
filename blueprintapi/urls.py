"""blueprintapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.authtoken import views as rest_views

from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="RapidATO API",
        default_version="v1",
        description="Welcome to the world of RapidATO",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", views.index, name="index"),
    path("admin/", admin.site.urls),
    path('api-token-auth/', rest_views.obtain_auth_token),
    path("api/catalogs/", include("catalogs.urls")),
    path("api/components/", include("components.urls")),
    path("api/projects/", include("projects.urls")),
    path("api/users/", include("users.urls")),
    path("api/healthcheck/", views.healthcheck, name="healthcheck"),
    path("api-auth/", include("rest_framework.urls")),
    re_path(
        r"^doc(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "doc/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]
