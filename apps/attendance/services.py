from datetime import datetime, timedelta
from typing import Optional

from django.db import transaction
from django.utils import timezone

from apps.attendance.exceptions import (
    AttendanceError,
    AlreadyClockedInError,
    NotClockedInError,
)
from apps.attendance.models import WorkSession, AttendanceDaySummary
from apps.users.models import Employee


def _now(when: Optional[datetime] = None) -> datetime:
    """Return an aware datetime in the current timezone."""
    return when if when is not None else timezone.now()


@transaction.atomic
def clock_in(
    employee: Employee,
    source: str = "WEB",
    when: Optional[datetime] = None,
) -> WorkSession:
    """
    Start a new work session for an employee.

    Raises:
        AlreadyClockedInError: if there is an open session.
    """
    when = _now(when)

    # Lock rows to avoid race conditions with concurrent requests.
    open_session = (
        WorkSession.objects
        .select_for_update()
        .filter(employee=employee, clock_out_at__isnull=True)
        .first()
    )
    if open_session:
        raise AlreadyClockedInError("Employee already has an open work session.")

    work_date = when.date()

    session = WorkSession.objects.create(
        employee=employee,
        clock_in_at=when,
        clock_in_source=source,
        work_date=work_date,
        total_work_duration=timedelta(0),
        is_overtime=False,
    )

    _update_daily_summary_for_session(session)

    return session


@transaction.atomic
def clock_out(
    employee: Employee,
    source: str = "WEB",
    when: Optional[datetime] = None,
) -> WorkSession:
    """
    Close the employee's open work session.

    Raises:
        NotClockedInError: if no open session exists.
    """
    when = _now(when)

    session = (
        WorkSession.objects
        .select_for_update()
        .filter(employee=employee, clock_out_at__isnull=True)
        .first()
    )
    if not session:
        raise NotClockedInError("Employee does not have an open work session.")

    if when <= session.clock_in_at:
        # Defensive: ensure positive duration.
        when = session.clock_in_at + timedelta(seconds=1)

    session.clock_out_at = when
    session.clock_out_source = source
    session.total_work_duration = session.clock_out_at - session.clock_in_at
    session.work_date = session.clock_in_at.date()
    session.save(update_fields=[
        "clock_out_at",
        "clock_out_source",
        "total_work_duration",
        "work_date",
        "updated_at",
    ])

    _update_daily_summary_for_session(session)

    return session


def _update_daily_summary_for_session(session: WorkSession) -> None:
    """
    Rebuild the AttendanceDaySummary for the session's employee and date.
    """
    employee = session.employee
    work_date = session.work_date

    sessions = WorkSession.objects.filter(
        employee=employee,
        work_date=work_date,
        clock_out_at__isnull=False,
    )

    total_work = timedelta(0)
    for s in sessions:
        if s.total_work_duration:
            total_work += s.total_work_duration

    expected = timedelta(hours=8)

    summary, created = AttendanceDaySummary.objects.get_or_create(
        employee=employee,
        work_date=work_date,
        defaults={
            "expected_work_duration": expected,
            "total_work_duration": total_work,
            "total_overtime_duration": max(total_work - expected, timedelta(0)),
            "status": _compute_status(total_work, expected),
        },
    )

    if not created:
        summary.total_work_duration = total_work
        summary.expected_work_duration = expected
        summary.total_overtime_duration = max(total_work - expected, timedelta(0))
        summary.status = _compute_status(total_work, expected)
        summary.save(update_fields=[
            "total_work_duration",
            "expected_work_duration",
            "total_overtime_duration",
            "status",
            "updated_at",
        ])


def _compute_status(total_work: timedelta, expected: timedelta) -> str:
    """
    Simple status logic placeholder.

    Later we extend this aight (e.g. LATE, HOLIDAY).
    """
    if total_work == timedelta(0):
        return "ABSENT"
    return "PRESENT"
