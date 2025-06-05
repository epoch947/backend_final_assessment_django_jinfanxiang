from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Attendance
from .serializers import AttendanceSerializer
from rest_framework.permissions import IsAuthenticated
from .filters import AttendanceFilter
from employees.permissions import IsAdminGroup, IsHRGroup, IsEmployeeSelfOrHRorAdmin
from rest_framework.authentication import TokenAuthentication

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    Attendance endpoints:
      - Admin/HR: can list/create/update/delete any attendance record.
      - Employee: can only list/retrieve attendance records for themselves.
    """

    queryset = Attendance.objects.select_related("employee").all()
    serializer_class = AttendanceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsEmployeeSelfOrHRorAdmin]
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,  # search on any text fields
    ]
    filterset_class = AttendanceFilter
    # filterset_fields = ['employee__id', 'date', 'status']
    ordering_fields = ["date", "status"]
    search_fields = ["status"]

    def get_queryset(self):
        """
        Override to permit:
        - Admin/HR see all records
        - Employee sees only Attendance entries where attendance.employee.user == request.user
        """
        user = self.request.user

        # If Admin or HR, return all attendance records
        if user.groups.filter(name__in=["Admin", "HR"]).exists():
            return super().get_queryset()

        # Otherwise (Employee group), only return attendance for that employee
        return super().get_queryset().filter(employee__user=user)
