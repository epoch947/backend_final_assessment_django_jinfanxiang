# attendance/filters.py
import django_filters
from .models import Attendance


class AttendanceFilter(django_filters.FilterSet):
    date_min = django_filters.DateFilter(
        field_name="date", lookup_expr="gte", label="Attendance Date (on or after)"
    )
    date_max = django_filters.DateFilter(
        field_name="date", lookup_expr="lte", label="Attendance Date (on or before)"
    )

    class Meta:
        model = Attendance
        fields = {
            "employee__id": ["exact"],
            #'date_min': ['exact'],
            #'date_max': ['exact'],
            "status": ["exact"],  # filter by status (e.g. ?status=present)
        }
