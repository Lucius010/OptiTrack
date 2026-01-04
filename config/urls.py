from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/v1/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Existing apps
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/attendance/', include('apps.attendance.urls')),
    path('api/v1/tracker/', include('apps.tracker.urls')),
    path("api/v1/overtime/", include("apps.overtime.urls")),
]

