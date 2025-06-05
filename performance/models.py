from django.db import models

# Create your models here.
from django.db import models
from employees.models import Employee


class Performance(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="performances"
    )
    rating = models.IntegerField()  # Expect 1–5
    review_date = models.DateField()

    class Meta:
        unique_together = ("employee", "review_date")

    def __str__(self):
        return f"{self.employee.name} – {self.review_date}: {self.rating}"

