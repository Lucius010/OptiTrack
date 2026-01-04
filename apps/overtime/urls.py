from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OvertimeRuleViewSet, OvertimeEntryViewSet

app_name = "overtime"

router = DefaultRouter()
router.register(r"rules", OvertimeRuleViewSet, basename="overtime-rule")
router.register(r"entries", OvertimeEntryViewSet, basename="overtime-entry")

urlpatterns = [
    path("", include(router.urls)),
]
