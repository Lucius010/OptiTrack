from datetime import timedelta

from django.db import models
from django.db.models import Q, UniqueConstraint

from apps.users.models import Employee


class WorkSession(models.Model):
    SOURCE_CHOICES = [
        ("WEB", "Web"),
        ("MOBILE", "Mobile"),
        ("KIOSK", "Kiosk"),
        ("API", "API"),
    ]
    END_SOURCE_CHOICES = [
        ("WEB", "Web"),
        ("MOBILE", "Mobile"),
        ("AUTO_TIMEOUT", "Auto timeout"),
        ("MANUAL_ADJUST", "Manual adjust"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="work_sessions",
    )

    clock_in_at = models.DateTimeField()
    clock_out_at = models.DateTimeField(null=True, blank=True)

    clock_in_source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="WEB",
    )
    clock_out_source = models.CharField(
        max_length=20,
        choices=END_SOURCE_CHOICES,
        null=True,
        blank=True,
    )

    is_manual_edit = models.BooleanField(default=False)
    manual_edit_reason = models.TextField(blank=True)

    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_work_sessions",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    total_work_duration = models.DurationField(default=timedelta)
    is_overtime = models.BooleanField(default=False)

    work_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["employee"],
                condition=Q(clock_out_at__isnull=True),
                name="uniq_open_session_per_employee",
            ),
        ]
        indexes = [
            models.Index(fields=["employee", "work_date"]),
        ]

    def __str__(self):
        return f"{self.employee} {self.work_date} {self.clock_in_at}–{self.clock_out_at or 'OPEN'}"


class AttendanceDaySummary(models.Model):
    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("LATE", "Late"),
        ("ON_LEAVE", "On leave"),
        ("HOLIDAY", "Holiday"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="daily_summaries",)
    work_date = models.DateField()

    total_work_duration = models.DurationField(default=timedelta(0))
    total_overtime_duration = models.DurationField(default=timedelta(0))
    expected_work_duration = models.DurationField(default=timedelta(0))
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PRESENT",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("employee", "work_date")
        indexes = [
            models.Index(fields=["employee", "work_date"]),
        ]

    def __str__(self):
        return f"{self.employee} {self.work_date} ({self.status})"
