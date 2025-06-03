from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Attendance
from .serializers import AttendanceSerializer
from rest_framework.permissions import IsAuthenticated
from .filters import AttendanceFilter
class AttendanceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Attendance.objects.select_related('employee').all()
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.OrderingFilter,
                       filters.SearchFilter, #search on any text fields
                       ]
    filterset_class = AttendanceFilter
    #filterset_fields = ['employee__id', 'date', 'status']
    ordering_fields = ['date', 'status']
    search_fields = ['status']
