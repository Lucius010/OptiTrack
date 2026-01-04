from __future__ import annotations

from datetime import date

from django.db import transaction
from django.utils import timezone

from apps.attendance.models import WorkSession
from apps.users.models import Employee
from .models import OvertimeRule, OvertimeEntry


@transaction.atomic
def calculate_overtime_for_period(period_start: date, period_end: date) -> None:
    """
    Recalculate overtime entries for all active employees and active rules
    for the given date range (inclusive).

    - Aggregates WorkSession durations per employee per day using:
        - work_date
        - clock_in_at / clock_out_at
    - Applies daily or weekly thresholds from OvertimeRule.
    - Creates or updates OvertimeEntry unless it is locked.
    """
    # Load active rules once
    rules = list(OvertimeRule.objects.filter(is_active=True))

    if not rules:
        return

    # Consider only active employees
    employees = Employee.objects.filter(is_active=True)

    for employee in employees:
        # Fetch sessions in the period for this employee
        sessions = WorkSession.objects.filter(
            employee=employee,
            work_date__gte=period_start,
            work_date__lte=period_end,
        )

        if not sessions.exists():
            continue

        # Aggregate total hours per day
        daily_hours: dict[date, float] = {}

        for session in sessions:
            # Skip incomplete sessions
            if not session.clock_in_at or not session.clock_out_at:
                continue

            duration_seconds = (session.clock_out_at - session.clock_in_at).total_seconds()
            duration_hours = duration_seconds / 3600.0

            day = session.work_date
            daily_hours[day] = daily_hours.get(day, 0.0) + duration_hours

        if not daily_hours:
            continue

        base_rate = float(employee.pay_rate)

        for rule in rules:
            threshold = float(rule.threshold_hours)
            multiplier = float(rule.multiplier)

            total_regular = 0.0
            total_ot = 0.0

            if rule.scope == OvertimeRule.DAILY:
                # Apply threshold independently per day, sum overtime
                for _, hours in daily_hours.items():
                    regular = min(hours, threshold)
                    ot = max(hours - threshold, 0.0)
                    total_regular += regular
                    total_ot += ot

                entry_period_start = period_start
                entry_period_end = period_end

            elif rule.scope == OvertimeRule.WEEKLY:
                total_hours = sum(daily_hours.values())
                total_regular = min(total_hours, threshold)
                total_ot = max(total_hours - threshold, 0.0)

                entry_period_start = period_start
                entry_period_end = period_end

            else:
                # Unknown scope, skip
                continue

            if total_ot <= 0:
                # No overtime for this rule/employee/period
                continue

            overtime_amount = total_ot * base_rate * multiplier

            entry, created = OvertimeEntry.objects.get_or_create(
                employee=employee,
                rule=rule,
                period_start=entry_period_start,
                period_end=entry_period_end,
                defaults={
                    "hours_regular": total_regular,
                    "hours_overtime": total_ot,
                    "base_rate": base_rate,
                    "overtime_multiplier": multiplier,
                    "overtime_amount": overtime_amount,
                },
            )

            if not created and not entry.is_locked:
                entry.hours_regular = total_regular
                entry.hours_overtime = total_ot
                entry.base_rate = base_rate
                entry.overtime_multiplier = multiplier
                entry.overtime_amount = overtime_amount
                entry.finalized_at = timezone.now()
                entry.save()
