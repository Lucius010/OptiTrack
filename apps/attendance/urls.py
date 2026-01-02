from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WorkSessionViewSet, 
    AttendanceDaySummaryViewSet, 
    ClockInView, 
    ClockOutView
)

app_name = 'attendance'

# 1. Register ViewSets for the data tables (Sessions and Summaries)
router = DefaultRouter()
router.register(r'sessions', WorkSessionViewSet, basename='worksession')
router.register(r'summaries', AttendanceDaySummaryViewSet, basename='summary')

urlpatterns = [
    # Paths: /api/v1/attendance/sessions/ and /api/v1/attendance/summaries/
    path('', include(router.urls)),
    
    # Path: /api/v1/attendance/clock-in/
    path('clock-in/', ClockInView.as_view(), name='clock-in'),
    
    # Path: /api/v1/attendance/clock-out/
    path('clock-out/', ClockOutView.as_view(), name='clock-out'),
]