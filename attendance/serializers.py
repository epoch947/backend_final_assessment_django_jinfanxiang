from rest_framework import serializers
from .models import Attendance
from employees.serializers import EmployeeSerializer

class AttendanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Attendance.objects.none(),  # we’ll override in `get_queryset()`
        source='employee',
        write_only=True
    )

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_id', 'date', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee_id'].queryset = self.Meta.model.objects.model.employee.field.related_model.objects.all()
