"""
URL configuration for employee_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="Employee Management API",
        default_version="v1",
    ),
    public=True,
    permission_classes=[AllowAny],  # allow everyone
    authentication_classes=[],  # no auth needed to view swagger
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Employee/Department endpoints
    path(
        "api/employees/", include("employees.urls")
    ),  # handles /api/employees/ and /api/employees/departments/
    # Attendance endpoints
    path("api/attendance/", include("attendance.urls")),  # handles /api/attendance/
    # Performance endpoints
    path("api/performance/", include("performance.urls")),  # handles /api/performance/
    # Token‐auth endpoint:
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
    # Swagger UI (no authentication required to view docs):
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api/reports/", include("reports.urls")),
]
