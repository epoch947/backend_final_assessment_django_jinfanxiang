from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from .models import Attendance
from .serializers import AttendanceSerializer
from .filters import AttendanceFilter
from employees.permissions import IsAdminGroup, IsHRGroup, IsAttendanceSelfOrHRorAdmin


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    Attendance endpoints:
      - Admin/HR: can list/create/update/delete any attendance record.
      - Employee: can only list/retrieve attendance records for themselves.
    """

    authentication_classes = [TokenAuthentication]
    queryset = Attendance.objects.select_related("employee").all()
    serializer_class = AttendanceSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_class = AttendanceFilter
    ordering_fields = ["date", "status"]
    search_fields = ["status"]

    def get_permissions(self):
        """
        - Only Admin or HR may create a new Attendance record.
        - For all other actions, use IsAttendanceSelfOrHRorAdmin.
        """
        if self.action == "create":
            permission_classes = [IsAuthenticated & (IsAdminGroup | IsHRGroup)]
        else:
            permission_classes = [IsAuthenticated & IsAttendanceSelfOrHRorAdmin]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Admin/HR see all records;
        Employee sees only Attendance entries where attendance.employee.user == request.user.
        """
        user = self.request.user
        if user.groups.filter(name__in=["Admin", "HR"]).exists():
            return super().get_queryset()
        return super().get_queryset().filter(employee__user=user)
