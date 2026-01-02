from django.utils import timezone
from django.db.models import Sum, F
from apps.attendance.models import WorkSession
from apps.users.models import Employee
from datetime import timedelta

def get_currently_clocked_in_employees():
    """
    Returns a queryset of employees who have an active (open) work session.
    """
    # Highlight: We look for sessions where clock_out_at is NULL
    active_sessions = WorkSession.objects.filter(clock_out_at__isnull=True).select_related('employee', 'employee__department')
    return [session.employee for session in active_sessions]


def calculate_daily_stats(employee, target_date=None):
    """
    Calculates the total hours worked for a specific employee on a specific date.
    ==========================================================
    NEW: Sums up multiple sessions (e.g., morning and afternoon)
    ==========================================================
    """
    if target_date is None:
        target_date = timezone.now().date()

    sessions = WorkSession.objects.filter(
        employee=employee,
        work_date=target_date,
        clock_out_at__isnull=False
    )

    # Use Django's Sum aggregate to get total duration
    total_duration = sessions.aggregate(total=Sum('total_work_duration'))['total'] or timedelta()
    
    return {
        "employee_code": employee.employee_code,
        "date": target_date,
        "total_seconds": total_duration.total_seconds(),
        "total_hours": round(total_duration.total_seconds() / 3600, 2),
        "session_count": sessions.count()
    }

def get_department_occupancy():
    """
    Returns a count of how many people are 'In' per department.
    """
    # Highlight: Useful for the 'OptiTrack' real-time dashboard
    active_sessions = WorkSession.objects.filter(clock_out_at__isnull=True)
    stats = {}
    
    for session in active_sessions:
        dept_name = session.employee.department.name if session.employee.department else "Unassigned"
        stats[dept_name] = stats.get(dept_name, 0) + 1
        
    return stats