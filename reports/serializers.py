from rest_framework import serializers


class DepartmentPerformanceSerializer(serializers.Serializer):
    department = serializers.CharField()
    average_rating = serializers.FloatField()
    num_reviews = serializers.IntegerField()


class DepartmentAttendanceSerializer(serializers.Serializer):
    department = serializers.CharField()
    month = serializers.CharField()  # e.g. "2025-06"
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    attendance_rate = serializers.FloatField()  # present_days / total_days
