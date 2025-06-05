from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Employee, Department
from .serializers import EmployeeSerializer, DepartmentSerializer
from rest_framework.permissions import IsAuthenticated
from .filters import EmployeeFilter  # import custom filter set
from django.contrib.auth.models import User
from .permissions import IsAdminGroup, IsHRGroup, IsEmployeeSelfOrHRorAdmin
from rest_framework.authentication import TokenAuthentication

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    Department list/create/update/delete endpoints.
    Allow only Admin or HR users to manage departments.
    """

    # Only authenticated users who are in Admin or HR group can do anything here.
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

    queryset = Employee.objects.select_related("department", "user").all()
    serializer_class = EmployeeSerializer
    # Enforce TokenAuth:
    authentication_classes = [TokenAuthentication]
    # Then combine with custom role‐based permissions:
    permission_classes = [IsAuthenticated & IsEmployeeSelfOrHRorAdmin]
    # Filtering / searching / ordering:
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    # Tell DRF to use EmployeeFilter class:
    filterset_class = EmployeeFilter
    # filterset_fields = ['department__id', 'date_of_joining']
    search_fields = ["name", "email"]
    ordering_fields = ["name", "date_of_joining"]

    def get_permissions(self):
        """
        Override this method to allow only Admin/HR to create new Employee records,
        but let an Employee user update their own profile.
        """
        # If this is a "create" action, only Admin or HR can proceed.
        if self.action == "create":
            # allow only Admin or HR to create a brand‐new Employee
            permission_classes = [IsAuthenticated & (IsAdminGroup | IsHRGroup)]
        else:
            # For list/retrieve/update/delete, use the generic mix above
            permission_classes = [IsAuthenticated & IsEmployeeSelfOrHRorAdmin]

        return [permission() for permission in permission_classes]

    # def perform_create(self, serializer):
    #     # Always assign the new Employee to request.user
    #     serializer.save(user=self.request.user)