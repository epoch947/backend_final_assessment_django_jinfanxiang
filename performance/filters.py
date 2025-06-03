# performance/filters.py

import django_filters
from .models import Performance


class PerformanceFilter(django_filters.FilterSet):
    """
    Filters for Performance model.
    - review_date_min / review_date_max: allow filtering by a date range.
    - rating: allow exact match or range filtering on rating (assuming rating is an integer or decimal field).
    """
    # Date range filters
    review_date_min = django_filters.DateFilter(
        field_name='review_date',
        lookup_expr='gte',
        label='Review Date (on or after)'
    )
    review_date_max = django_filters.DateFilter(
        field_name='review_date',
        lookup_expr='lte',
        label='Review Date (on or before)'
    )


    rating_min = django_filters.NumberFilter(
        field_name='rating',
        lookup_expr='gte',
        label='Rating (greater than or equal)'
    )
    rating_max = django_filters.NumberFilter(
        field_name='rating',
        lookup_expr='lte',
        label='Rating (less than or equal)'
    )

    class Meta:
        model = Performance
        # Expose department and employee foreign keys if needed:
        fields = {
            'employee__id': ['exact'],   # filter by e.g. ?employee__id=5
            #'rating_min': ['exact'],     # exposes e.g. ?rating_min=3
            #'rating_max': ['exact'],     # exposes e.g. ?rating_max=5
            #'review_date_min': ['exact'],
            #'review_date_max': ['exact'],
        }
