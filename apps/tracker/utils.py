from django.utils import timezone
from django.db.models import Sum, F, Count
from apps.attendance.models import WorkSession
from apps.users.models import Employee
from datetime import timedelta

def get_currently_clocked_in_employees():
    """
    Return a queryset of distinct employees with an open work session.
    """
    return (
        Employee.objects
        .filter(work_sessions__clock_out_at__isnull=True)
        .select_related("department")
        .distinct()
    )

def calculate_daily_stats(employee, target_date=None):
    if target_date is None:
        target_date = timezone.now().date()

    sessions = WorkSession.objects.filter(
        employee=employee,
        work_date=target_date,
        clock_out_at__isnull=False,
    )

    total_duration = sessions.aggregate(total=Sum("total_work_duration"))["total"] or timedelta()

    total_seconds = int(total_duration.total_seconds())

    return {
        "employee_code": employee.employee_code,
        "date": target_date,
        "total_seconds": total_seconds,
        "total_hours": round(total_seconds / 3600, 2),
        "session_count": sessions.count(),
    }

def get_department_occupancy():
    """
    Returns a mapping of department name -> active employee count.
    """
    rows = (
        WorkSession.objects
        .filter(clock_out_at__isnull=True)
        .values("employee__department__name")
        .annotate(active_count=Count("employee", distinct=True))
    )

    stats = {}
    for row in rows:
        dept_name = row["employee__department__name"] or "Unassigned"
        stats[dept_name] = row["active_count"]
    return stats
