# employees/filters.py

import django_filters
from .models import Employee


class EmployeeFilter(django_filters.FilterSet):
    """
    Filters for Employee.
    - `department`: exact match on department ID (foreign key).
    - `date_of_joining_min` and `date_of_joining_max`: slice by date_of_joining.
    """
    date_of_joining_min = django_filters.DateFilter(
        field_name='date_of_joining',
        lookup_expr='gte',
        label='Date Joined (on or after)'
    )
    date_of_joining_max = django_filters.DateFilter(
        field_name='date_of_joining',
        lookup_expr='lte',
        label='Date Joined (on or before)'
    )

    class Meta:
        model = Employee
        # allow filtering by the integer department name
        fields = {
            'id': ['exact'],
            'department__name': ['exact'],

            #'date_of_joining_min': ['exact'],
            #'date_of_joining_max': ['exact'],
        }
