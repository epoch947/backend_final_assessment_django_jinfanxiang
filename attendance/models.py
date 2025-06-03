from django.db import models

# Create your models here.
from django.db import models
from employees.models import Employee

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent',  'Absent'),
        ('late',    'Late'),
    ]
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='attendances'
    )
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.name}: {self.date} → {self.status}"
