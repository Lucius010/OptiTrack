from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    #path("attendance/", include("apps.attendance.urls")),
    #path("tracker/", include("apps.tracker.urls")),
    #path("users/", include("apps.users.urls")),
]
