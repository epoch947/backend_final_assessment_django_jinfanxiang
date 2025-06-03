from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Performance

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'review_date', 'rating')
    list_filter = ('rating',)
    search_fields = ('employee__name',)
