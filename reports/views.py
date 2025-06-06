from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from rest_framework import permissions, views, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.db.models import (
    OuterRef,
    Subquery,
    Value,
    Avg,
    Count,
    Q,
    IntegerField,
)
from django.db.models.functions import Coalesce

from employees.models import Department
from performance.models import Performance
from attendance.models import Attendance

from .serializers import DepartmentPerformanceSerializer, DepartmentAttendanceSerializer

from datetime import date
import calendar


class AveragePerformanceByDepartmentView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Department.objects.annotate(
            avg_rating=Avg("employees__performances__rating"),
            review_count=Count("employees__performances", distinct=True),
        ).filter(review_count__gt=0)

        data = [
            {
                "department": dept.name,
                "average_rating": round(dept.avg_rating or 0, 2),
                "num_reviews": dept.review_count,
            }
            for dept in queryset
        ]

        serializer = DepartmentPerformanceSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MonthlyAttendanceRateByDepartmentView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        year_str = request.GET.get("year")
        month_str = request.GET.get("month")

        try:
            year_int = int(year_str)
            month_int = int(month_str)
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid year or month parameter. Must be integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dept_id = request.GET.get("department_id")
        try:
            dept_id_int = int(dept_id) if dept_id is not None else None
        except ValueError:
            return Response(
                {"detail": "Invalid department_id parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        attendance_qs = Attendance.objects.filter(
            date__year=year_int,
            date__month=month_int,
            employee__department=OuterRef("pk"),
        )

        total_days_subquery = (
            attendance_qs.values("employee__department")
            .annotate(cnt=Count("id"))
            .values("cnt")
        )

        present_days_subquery = (
            attendance_qs.filter(status="present")
            .values("employee__department")
            .annotate(cnt=Count("id"))
            .values("cnt")
        )

        absent_days_subquery = (
            attendance_qs.filter(status="absent")
            .values("employee__department")
            .annotate(cnt=Count("id"))
            .values("cnt")
        )

        dept_qs = Department.objects.all()
        if dept_id_int is not None:
            dept_qs = dept_qs.filter(pk=dept_id_int)

        dept_qs = dept_qs.annotate(
            total_days=Coalesce(
                Subquery(total_days_subquery, output_field=IntegerField()), Value(0)
            ),
            days_present=Coalesce(
                Subquery(present_days_subquery, output_field=IntegerField()), Value(0)
            ),
            days_absent=Coalesce(
                Subquery(absent_days_subquery, output_field=IntegerField()), Value(0)
            ),
        ).order_by("name")

        data = []
        for dept in dept_qs:
            total = dept.total_days
            present = dept.days_present
            absent = dept.days_absent
            attendance_rate = (present / total * 100) if total else 0

            data.append(
                {
                    "department_id": dept.id,
                    "department_name": dept.name,
                    "total_days": total,
                    "days_present": present,
                    "days_absent": absent,
                    "attendance_rate": attendance_rate,
                }
            )

        return Response(data, status=status.HTTP_200_OK)


class MonthlyAttendanceChartView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        year_str = request.GET.get("year")
        month_str = request.GET.get("month")

        try:
            year = int(year_str)
            month = int(month_str)
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid year or month parameter. Expect integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        monthly_records = Attendance.objects.filter(date__year=year, date__month=month)

        total_count = monthly_records.count()
        present_count = monthly_records.filter(status="present").count()
        absent_count = monthly_records.filter(status="absent").count()

        data = {
            "year": year,
            "month": month,
            "total_records": total_count,
            "present_count": present_count,
            "absent_count": absent_count,
        }

        return Response(data, status=status.HTTP_200_OK)


@login_required
def attendance_chart_view(request):
    """
    Renders a page with a bar chart of Present vs Absent counts
    for a given year/month (default: current).
    """
    today = date.today()
    year = request.GET.get("year", today.year)
    month = request.GET.get("month", today.month)
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        year = today.year
        month = today.month

    qs = Attendance.objects.filter(date__year=year, date__month=month)

    totals = qs.aggregate(
        present_count=Count("id", filter=Q(status="present")),
        absent_count=Count("id", filter=Q(status="absent")),
    )

    present_count = totals.get("present_count") or 0
    absent_count = totals.get("absent_count") or 0

    context = {
        "year": year,
        "month": month,
        "chart_labels": ["present", "absent"],
        "chart_data": [present_count, absent_count],
    }
    return render(request, "reports/attendance_chart.html", context)


@login_required
def performance_chart_view(request):
    """
    Renders a page with a line chart of average performance scores
    between a user‐selected start and end month/year (inclusive).
    If no range is provided, defaults to the last 6 months.
    """
    today = date.today()
    start_year_str = request.GET.get("start_year")
    start_month_str = request.GET.get("start_month")
    end_year_str = request.GET.get("end_year")
    end_month_str = request.GET.get("end_month")

    def parse_int(s, default):
        try:
            return int(s)
        except (TypeError, ValueError):
            return default

    end_year = parse_int(end_year_str, today.year)
    end_month = parse_int(end_month_str, today.month)

    if start_year_str and start_month_str:
        start_year = parse_int(start_year_str, today.year)
        start_month = parse_int(start_month_str, today.month)
    else:
        total_months_end = end_year * 12 + (end_month - 1)
        total_months_start = total_months_end - 5
        start_year = total_months_start // 12
        start_month = (total_months_start % 12) + 1

    def build_year_month_list(s_year, s_month, e_year, e_month):
        ym_list = []
        start_index = s_year * 12 + (s_month - 1)
        end_index = e_year * 12 + (e_month - 1)
        if end_index < start_index:
            start_index, end_index = end_index, start_index
        for idx in range(start_index, end_index + 1):
            y = idx // 12
            m = (idx % 12) + 1
            ym_list.append((y, m))
        return ym_list

    year_month_pairs = build_year_month_list(
        start_year, start_month, end_year, end_month
    )

    labels = []
    data_values = []
    for y, m in year_month_pairs:
        avg_obj = Performance.objects.filter(
            review_date__year=y, review_date__month=m
        ).aggregate(avg_score=Avg("rating"))
        avg_score = avg_obj.get("avg_score") or 0.0
        labels.append(f"{m}/{y}")
        data_values.append(round(avg_score, 1))

    context = {
        "chart_labels": labels,
        "chart_data": data_values,
        "start_year": start_year,
        "start_month": start_month,
        "end_year": end_year,
        "end_month": end_month,
    }
    return render(request, "reports/performance_chart.html", context)


@login_required
def employees_per_department_view(request):
    """
    Renders a pie chart that shows, for each Department, how many Employees it has.
    """
    qs = Department.objects.annotate(emp_count=Count("employees"))

    labels = [dept.name for dept in qs]
    data_values = [dept.emp_count for dept in qs]

    context = {
        "chart_labels": labels,
        "chart_data": data_values,
    }
    return render(request, "reports/employees_per_department.html", context)


@login_required
def monthly_attendance_overview_view(request):
    """
    Renders a bar chart of daily Present counts for a selected year & month.
    If no year/month in GET, defaults to current month.
    """
    today = date.today()

    year = request.GET.get("year", today.year)
    month = request.GET.get("month", today.month)
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        year = today.year
        month = today.month

    num_days = calendar.monthrange(year, month)[1]
    labels = list(range(1, num_days + 1))

    data_values = []
    for day in labels:
        count_present = Attendance.objects.filter(
            date__year=year,
            date__month=month,
            date__day=day,
            status="present",
        ).count()
        data_values.append(count_present)

    context = {
        "year": year,
        "month": month,
        "chart_labels": labels,
        "chart_data": data_values,
    }
    return render(request, "reports/monthly_attendance_overview.html", context)
class EmployeesPerDepartmentAPIView(APIView):
    """
    GET /api/reports/employees-per-department/
    Returns JSON: each { department_name, employee_count }.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Annotate each Department with its employee count (reverse FK 'employees')
        qs = Department.objects.annotate(emp_count=Count("employees"))

        data = [
            {
                "department_id": dept.id,
                "department_name": dept.name,
                "employee_count": dept.emp_count,
            }
            for dept in qs
        ]
        return Response(data, status=status.HTTP_200_OK)

class MonthlyAttendanceOverviewAPIView(APIView):
    """
    GET /api/reports/monthly-attendance-overview/?year=YYYY&month=MM
    Returns JSON: daily present‐counts for the specified month.
    If no year/month provided, defaults to current month.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = date.today()
        year = request.GET.get("year", today.year)
        month = request.GET.get("month", today.month)
        try:
            year = int(year)
            month = int(month)
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid year/month; must be integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # How many days in that month?
        num_days = calendar.monthrange(year, month)[1]
        labels = list(range(1, num_days + 1))  # [1,2,...,28/29/30/31]

        # Count “present” per day
        data_values = []
        for day in labels:
            count_present = Attendance.objects.filter(
                date__year=year,
                date__month=month,
                date__day=day,
                status="present",
            ).count()
            data_values.append(count_present)

        response_payload = {
            "year": year,
            "month": month,
            "labels": labels,
            "present_counts": data_values,
        }
        return Response(response_payload, status=status.HTTP_200_OK)