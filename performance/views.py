from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Performance
from .serializers import PerformanceSerializer
from .filters import PerformanceFilter #import the filter class
from employees.permissions import IsEmployeeSelfOrHRorAdmin

class PerformanceViewSet(viewsets.ModelViewSet):
    """
        Performance endpoints:
          - Admin and HR users can list/create/update/delete any Performance record.
          - An Employee user can only see and modify their own Performance records.
    """

    queryset = Performance.objects.select_related('employee').all()
    serializer_class = PerformanceSerializer
    # Only authenticated users who pass the object‐level rules in IsEmployeeSelfOrHRorAdmin may access
    permission_classes = [IsAuthenticated & IsEmployeeSelfOrHRorAdmin]
    filter_backends = [DjangoFilterBackend,
                       filters.OrderingFilter,
                       filters.SearchFilter, #search a text field
                       ]
    # Tell DRF to usePerformanceFilter
    filterset_class = PerformanceFilter
    #filterset_fields = ['employee__id', 'rating', 'review_date']
    search_fields = ['comment']
    ordering_fields = ['review_date', 'rating']

    def get_queryset(self):
        """
        Override get_queryset() so that:
          - Users in Admin or HR groups see all Performance records.
          - Users in Employee group see only Performance records where
            performance.employee.user == request.user.
        """
        user = self.request.user

        # Admin and HR can view all Performance records
        if user.groups.filter(name__in=["Admin", "HR"]).exists():
            return Performance.objects.select_related('employee').all()

        # Otherwise (Employee), only return records linked to this user's Employee profile
        return Performance.objects.select_related('employee').filter(employee__user=user)
