from django.shortcuts import render

# Create your views here.
import io
import matplotlib.pyplot as plt
from django.http import HttpResponse
from django.db.models import (
    OuterRef,
    Subquery,
    Value,
    Avg,
    Count,
    F,
    FloatField,
    IntegerField,
    Q,
)
from django.db.models.functions import TruncMonth
from rest_framework import views, status
from rest_framework.response import Response
from django.db.models.functions import Coalesce
from employees.models import Department
from performance.models import Performance
from attendance.models import Attendance
from rest_framework.views import APIView
from .serializers import DepartmentPerformanceSerializer, DepartmentAttendanceSerializer


class AveragePerformanceByDepartmentView(views.APIView):
    """
    GET /api/reports/average-performance/
    Returns each department’s average performance rating, along with the number of reviews.
    """

    def get(self, request):
        # Annotate each Department with average rating and review count
        queryset = Department.objects.annotate(
            avg_rating=Avg("employees__performances__rating"),
            review_count=Count("employees__performances", distinct=True),
        ).filter(review_count__gt=0)

        # Build response data
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
    """
    Returns attendance rates per department for a given year and month,
    including departments that have zero attendance rows.
    """

    def get(self, request, *args, **kwargs):
        # 1) Extract & validate year/month
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

        # 2) Optionally filter by department_id
        dept_id = request.GET.get("department_id")
        try:
            dept_id_int = int(dept_id) if dept_id is not None else None
        except ValueError:
            return Response(
                {"detail": "Invalid department_id parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3) Build a subquery that counts total days for each department
        attendance_qs = Attendance.objects.filter(
            date__year=year_int,
            date__month=month_int,
            employee__department=OuterRef("pk"),  # OuterRef('pk') = Department.id
        )

        # Use Coalesce to return zero if no matching attendance rows exist
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

        # 4) Query all departments (or one department if dept_id_int is provided),
        #    and annotate with those subqueries
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

        # 5) Build the JSON response
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
    """
    Returns a simple JSON payload summarizing attendance counts for
    a specific year/month, based on query parameters ?year=YYYY&month=M.
    """

    def get(self, request, *args, **kwargs):
        # 1. Pull year & month from query params
        year_str = request.GET.get("year")
        month_str = request.GET.get("month")

        # 2. Validate & convert to integers
        try:
            year = int(year_str)
            month = int(month_str)
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid year or month parameter. Expect integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Filter Attendance by that year/month
        monthly_records = Attendance.objects.filter(date__year=year, date__month=month)

        # 4. Build your chart data.
        # count total records, count present vs absent.
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
