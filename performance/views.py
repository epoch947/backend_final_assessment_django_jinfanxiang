from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Performance
from .serializers import PerformanceSerializer
from .filters import PerformanceFilter #import the filter class

class PerformanceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Performance.objects.select_related('employee').all()
    serializer_class = PerformanceSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.OrderingFilter,
                       filters.SearchFilter, #search a text field
                       ]
    # Tell DRF to usePerformanceFilter
    filterset_class = PerformanceFilter
    #filterset_fields = ['employee__id', 'rating', 'review_date']
    search_fields = ['comment']
    ordering_fields = ['review_date', 'rating']
