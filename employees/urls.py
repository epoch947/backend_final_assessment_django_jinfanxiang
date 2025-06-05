from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, DepartmentViewSet

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet)
router.register(r"employees", EmployeeViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
