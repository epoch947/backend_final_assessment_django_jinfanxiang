from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from .models import Employee, Department
from .serializers import EmployeeSerializer, DepartmentSerializer
from .filters import EmployeeFilter
from .permissions import IsAdminGroup, IsHRGroup, IsEmployeeSelfOrHRorAdmin


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    Department list/create/update/delete endpoints.
    Allow only Admin or HR users to manage departments.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & (IsAdminGroup | IsHRGroup)]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name"]


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Employee list/retrieve/update/delete endpoints.
    - Admin/HR: can list all Employees, create new, update/delete any.
    - Employee: can only retrieve or update their own record.
    """

    authentication_classes = [TokenAuthentication]
    queryset = Employee.objects.select_related("department", "user").all()
    serializer_class = EmployeeSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = EmployeeFilter
    search_fields = ["name", "email"]
    ordering_fields = ["name", "date_of_joining"]

    def get_permissions(self):
        """
        - Only Admin or HR may create a new Employee.
        - For all other actions, use IsEmployeeSelfOrHRorAdmin.
        """
        if self.action == "create":
            permission_classes = [IsAuthenticated & (IsAdminGroup | IsHRGroup)]
        else:
            permission_classes = [IsAuthenticated & IsEmployeeSelfOrHRorAdmin]

        return [permission() for permission in permission_classes]
