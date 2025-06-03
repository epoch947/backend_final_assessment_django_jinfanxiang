from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Employee, Department
from .serializers import EmployeeSerializer, DepartmentSerializer
from rest_framework.permissions import IsAuthenticated
from .filters import EmployeeFilter #import custom filter set
class DepartmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']

class EmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.select_related('department').all()
    serializer_class = EmployeeSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Tell DRF to use EmployeeFilter class:
    filterset_class = EmployeeFilter
    #filterset_fields = ['department__id', 'date_of_joining']
    search_fields = ['name', 'email']
    ordering_fields = ['name', 'date_of_joining']
