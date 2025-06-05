from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Department, Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "department", "date_of_joining")
    list_filter = ("department",)
