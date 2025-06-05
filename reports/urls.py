from django.urls import path
from .views import (
    AveragePerformanceByDepartmentView,
    MonthlyAttendanceRateByDepartmentView,
)
from .views import MonthlyAttendanceChartView
from .views import attendance_chart_view, performance_chart_view

urlpatterns = [
    path(
        "average-performance/",
        AveragePerformanceByDepartmentView.as_view(),
        name="avg_performance_dept",
    ),
    path(
        "monthly-attendance/",
        MonthlyAttendanceRateByDepartmentView.as_view(),
        name="monthly_attendance_dept",
    ),
    path(
        "monthly-attendance-chart/",
        MonthlyAttendanceChartView.as_view(),
        name="monthly_attendance_chart",
    ),
    path('attendance-chart/', attendance_chart_view, name='attendance-chart'),
    path('performance-chart/', performance_chart_view, name='performance-chart'),
]
