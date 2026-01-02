from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from .models import WorkSession, AttendanceDaySummary
from .services import AttendanceService

@receiver(post_save, sender=WorkSession)
def update_daily_summary(sender, instance, created, **kwargs):
    """
    Automatically updates the AttendanceDaySummary when a session is closed.
    """
    # Only trigger if the session has a clock_out time and a calculated duration
    if instance.clock_out_at and instance.total_work_duration:
        
        # 1. Get or create the summary for this specific employee and date
        # FIX: Ensure we use 'work_date' as confirmed by your terminal choices
        summary, created = AttendanceDaySummary.objects.get_or_create(
            employee=instance.employee,
            work_date=instance.work_date
        )

        # 2. Sum up ALL finished sessions for this person today
        all_sessions_today = WorkSession.objects.filter(
            employee=instance.employee,
            work_date=instance.work_date,
            clock_out_at__isnull=False
        )

        total_duration = timedelta()
        for session in all_sessions_today:
            total_duration += session.total_work_duration

        # 3. Update summary fields
        # FIX: Using 'total_work_duration' instead of 'total_hours'
        summary.total_work_duration = total_duration
        
        # Calculate earnings for the day based on the logic in our Service
        summary.total_earnings = AttendanceService.calculate_earnings(instance)
        
        summary.save()