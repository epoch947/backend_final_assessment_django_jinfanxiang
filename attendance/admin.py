from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "status")
    list_filter = ("status",)
    search_fields = ("employee__name",)
