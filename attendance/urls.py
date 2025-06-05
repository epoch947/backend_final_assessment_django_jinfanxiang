from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AttendanceViewSet

router = DefaultRouter()
router.register(r"attendance", AttendanceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
