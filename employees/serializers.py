from rest_framework import serializers
from .models import Employee, Department


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name"]


class EmployeeSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source="department", write_only=True
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "name",
            "email",
            "phone_number",
            "address",
            "date_of_joining",
            "department",
            "department_id",
            "user"
        ]
        read_only_fields = ["id", "department"]
