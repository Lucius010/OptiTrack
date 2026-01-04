from django.db import models

class OvertimeRule(models.Model):
    DAILY = "daily"
    WEEKLY = "weekly"

    SCOPE_CHOICES = [
        (DAILY, "Daily"),
        (WEEKLY, "Weekly"),
    ]

    name = models.CharField(max_length=100)
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES, default=WEEKLY)

    threshold_hours = models.DecimalField(max_digits=5, decimal_places=2)
    multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.50)

    is_active = models.BooleanField(default=True)

    department = models.ForeignKey(
        "users.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="overtime_rules",
    )
    role = models.ForeignKey(
        "users.Role",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="overtime_rules",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Overtime rule"
        verbose_name_plural = "Overtime rules"

    def __str__(self):
        return self.name


class OvertimeEntry(models.Model):
    employee = models.ForeignKey(
        "users.Employee",
        on_delete=models.CASCADE,
        related_name="overtime_entries",
    )
    rule = models.ForeignKey(
        "OvertimeRule",
        on_delete=models.PROTECT,
        related_name="entries",
    )

    period_start = models.DateField()
    period_end = models.DateField()

    hours_regular = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    hours_overtime = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    base_rate = models.DecimalField(max_digits=8, decimal_places=2)
    overtime_multiplier = models.DecimalField(max_digits=4, decimal_places=2)
    overtime_amount = models.DecimalField(max_digits=10, decimal_places=2)

    finalized_at = models.DateTimeField(auto_now_add=True)
    is_locked = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Overtime entry"
        verbose_name_plural = "Overtime entries"
        unique_together = ("employee", "rule", "period_start", "period_end")

    def __str__(self):
        return f"{self.employee} {self.period_start}–{self.period_end}"
