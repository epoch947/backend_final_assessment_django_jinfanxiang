from django.urls import path
from .views import (
    AveragePerformanceByDepartmentView,
    MonthlyAttendanceRateByDepartmentView,
    MonthlyAttendanceChartView,
    attendance_chart_view,
    performance_chart_view,
    employees_per_department_view,
    monthly_attendance_overview_view,
)

urlpatterns = [
    # API endpoints (return JSON)
    path(
        "average-performance/",
        AveragePerformanceByDepartmentView.as_view(),
        name="avg_performance_dept",
    ),
    path(
        "monthly-attendance-rate/",
        MonthlyAttendanceRateByDepartmentView.as_view(),
        name="monthly_attendance_rate_by_dept",
    ),
    path(
        "monthly-attendance-chart/",
        MonthlyAttendanceChartView.as_view(),
        name="monthly_attendance_chart_api",
    ),

    # Template‐rendered pages (Django templates)
    path(
        "attendance-chart/",
        attendance_chart_view,
        name="attendance-chart",             # must match template’s reverse
    ),
    path(
        "performance-chart/",
        performance_chart_view,
        name="performance-chart",            # must match template’s reverse
    ),
    path(
        "employees-per-department/",
        employees_per_department_view,
        name="employees-per-department",     # must match template’s reverse
    ),
    path(
        "monthly-attendance-overview/",
        monthly_attendance_overview_view,
        name="monthly-attendance-overview",  # must match template’s reverse
    ),
]
