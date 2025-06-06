# performance/views.py

from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import TokenAuthentication

from .models import Performance
from .serializers import PerformanceSerializer
from .filters import PerformanceFilter
from employees.permissions import IsAdminGroup, IsHRGroup, IsPerformanceSelfOrHRorAdmin


class PerformanceViewSet(viewsets.ModelViewSet):
    """
    Performance endpoints:
      - Admin and HR users can list/create/update/delete any Performance record.
      - An Employee user can only see and modify their own Performance records.
    """

    authentication_classes = [TokenAuthentication]
    serializer_class = PerformanceSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_class = PerformanceFilter
    search_fields = ["comment"]
    ordering_fields = ["review_date", "rating"]

    def get_permissions(self):
        """
        - Only Admin or HR may create a new Performance record.
        - For all other actions, use IsPerformanceSelfOrHRorAdmin.
        """
        if self.action == "create":
            permission_classes = [IsAuthenticated & (IsAdminGroup | IsHRGroup)]
        else:
            permission_classes = [IsAuthenticated & IsPerformanceSelfOrHRorAdmin]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Admin and HR see all Performance records;
        Employee sees only Performance records linked to their own Employee user.
        """
        user = self.request.user
        if user.groups.filter(name__in=["Admin", "HR"]).exists():
            return Performance.objects.select_related("employee").all()
        return Performance.objects.select_related("employee").filter(
            employee__user=user
        )
