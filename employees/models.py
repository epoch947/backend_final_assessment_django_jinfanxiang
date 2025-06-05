from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User  # import the built-in User model


class Department(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    # Link each Employee to exactly one Django user account.
    # on_delete=models.CASCADE means if the User is deleted, the Employee record is also deleted.
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        # null=False,
        # blank=False
    )
    name = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10, blank=True)
    address = models.TextField(blank=True)
    date_of_joining = models.DateField()
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="employees"
    )

    def __str__(self):
        return f"{self.name} ({self.user.username})"


