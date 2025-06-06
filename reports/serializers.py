from rest_framework import serializers


class DepartmentPerformanceSerializer(serializers.Serializer):
    """
    Serializer for average-performance-by-department endpoint.
    Expects objects with keys: 'department', 'average_rating', 'num_reviews'.
    """
    department = serializers.CharField()
    average_rating = serializers.FloatField()
    num_reviews = serializers.IntegerField()


class DepartmentAttendanceSerializer(serializers.Serializer):
    """
    Serializer for monthly-attendance-rate-by-department endpoint.
    Expects objects with:
      'department_id', 'department_name', 'total_days',
      'days_present', 'days_absent', 'attendance_rate'
    """
    department_id = serializers.IntegerField()
    department_name = serializers.CharField()
    total_days = serializers.IntegerField()
    days_present = serializers.IntegerField()
    days_absent = serializers.IntegerField()
    attendance_rate = serializers.FloatField()
