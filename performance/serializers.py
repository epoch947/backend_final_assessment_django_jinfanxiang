from rest_framework import serializers
from .models import Performance


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = [
            "id",
            "employee",   # FK to Employee (integer ID)
            "rating",
            "review_date",
        ]
