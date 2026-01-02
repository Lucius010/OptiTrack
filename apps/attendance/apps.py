# apps/attendance/apps.py
from django.apps import AppConfig

class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.attendance'

    def ready(self):
        # ==========================================================
        # HIGHLIGHT: This line is required to activate signals!
        # ==========================================================
        import apps.attendance.signals