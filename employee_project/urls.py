from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# 1) Import DRF ViewSets
from employees.views import EmployeeViewSet, DepartmentViewSet
from attendance.views import AttendanceViewSet
from performance.views import PerformanceViewSet

# 2) Import ALL JSON‐returning report APIViews
from reports.views import (
    AveragePerformanceByDepartmentView,
    MonthlyAttendanceRateByDepartmentView,
    MonthlyAttendanceChartView,
    EmployeesPerDepartmentAPIView,           # ← newly added
    MonthlyAttendanceOverviewAPIView,         # ← newly added
)

# 3) Import template‐rendering endpoints
from reports.views import (
    attendance_chart_view,
    performance_chart_view,
    employees_per_department_view,
    monthly_attendance_overview_view,
)

# 4) Create & populate the DRF router
router = DefaultRouter()
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"attendance", AttendanceViewSet, basename="attendance")
router.register(r"performance", PerformanceViewSet, basename="performance")

# 5) drf_yasg SchemaView setup
schema_view = get_schema_view(
    openapi.Info(
        title="Employee Management API",
        default_version="v1",
        description="Employees, Departments, Attendance, Performance, and Reports",
        contact=openapi.Contact(email="support@yourcompany.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# 6) Final urlpatterns
urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # ViewSets (Employees / Departments / Attendance / Performance)
    path("api/", include(router.urls)),

    # ───────── JSON‐returning Report endpoints ─────────
    path(
        "api/reports/average-performance/",
        AveragePerformanceByDepartmentView.as_view(),
        name="average-performance-by-department",
    ),
    path(
        "api/reports/monthly-attendance-rate/",
        MonthlyAttendanceRateByDepartmentView.as_view(),
        name="monthly-attendance-rate-by-department",
    ),
    path(
        "api/reports/monthly-attendance-chart/",
        MonthlyAttendanceChartView.as_view(),
        name="monthly-attendance-chart-api",
    ),
    # ─────── Newly added APIViews for Swagger ───────
    path(
        "api/reports/employees-per-department/",
        EmployeesPerDepartmentAPIView.as_view(),
        name="employees-per-department-api",
    ),
    path(
        "api/reports/monthly-attendance-overview/",
        MonthlyAttendanceOverviewAPIView.as_view(),
        name="monthly-attendance-overview-api",
    ),

    # ───────── template‐rendered report pages ─────────
    path(
        "reports/attendance-chart/",
        attendance_chart_view,
        name="attendance-chart",
    ),
    path(
        "reports/performance-chart/",
        performance_chart_view,
        name="performance-chart",
    ),
    path(
        "reports/employees-per-department/",
        employees_per_department_view,
        name="employees-per-department",
    ),
    path(
        "reports/monthly-attendance-overview/",
        monthly_attendance_overview_view,
        name="monthly-attendance-overview",
    ),

    # ───────── Swagger / OpenAPI ─────────
    path(
        "api/swagger<str:format>",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "api/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "api/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
