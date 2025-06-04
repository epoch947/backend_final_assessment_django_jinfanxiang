from django.urls import path
from .views import (
    AveragePerformanceByDepartmentView,
    MonthlyAttendanceRateByDepartmentView
)
from .views import MonthlyAttendanceChartView

urlpatterns = [
    path('average-performance/', AveragePerformanceByDepartmentView.as_view(), name='avg_performance_dept'),
    path('monthly-attendance/', MonthlyAttendanceRateByDepartmentView.as_view(), name='monthly_attendance_dept'),
    path('monthly-attendance-chart/', MonthlyAttendanceChartView.as_view(), name='monthly_attendance_chart'),
]
