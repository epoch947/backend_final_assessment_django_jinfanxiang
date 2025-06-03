from rest_framework import serializers
from .models import Performance
from employees.serializers import EmployeeSerializer

class PerformanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Performance.objects.none(),
        source='employee',
        write_only=True
    )

    class Meta:
        model = Performance
        fields = ['id', 'employee', 'employee_id', 'rating', 'review_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee_id'].queryset = self.Meta.model.objects.model.employee.field.related_model.objects.all()
