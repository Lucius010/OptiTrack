from django.urls import path
from .views import DashboardLiveView, DepartmentStatsView, EmployeeDailySummaryView

# The app_name helps with 'namespacing' (e.g., tracker:live-dashboard)
app_name = 'tracker'

urlpatterns = [
    # ==========================================================
    # TRACKER ENDPOINTS
    # ==========================================================
    
    # Path: /api/v1/tracker/live/
    path('live/', DashboardLiveView.as_view(), name='live-dashboard'),
    
    # Path: /api/v1/tracker/stats/departments/
    path('stats/departments/', DepartmentStatsView.as_view(), name='dept-stats'),
    
    # Path: /api/v1/tracker/my-summary/
    path('my-summary/', EmployeeDailySummaryView.as_view(), name='personal-summary'),
]