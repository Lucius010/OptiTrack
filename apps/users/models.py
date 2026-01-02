from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)  # EMPLOYEE, MANAGER, HR_ADMIN
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Employee(AbstractUser):
    employee_code = models.CharField(max_length=50, unique=True)

    PAY_TYPE_CHOICES = [
        ("HOURLY", "Pay per Hour"),
        ("DAILY", "Pay per Day"),
        ("MONTHLY", "Monthly Salary"),
    ]

    pay_type = models.CharField(
        max_length=10,
        choices=PAY_TYPE_CHOICES,
        default="MONTHLY",  # must match choices
    )
    pay_rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Base rate used for pay estimates (not full payroll).",
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="employees",
        null=True,
        blank=True,
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="employees",
        null=True,
        blank=True,
    )

    EMPLOYMENT_STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("SUSPENDED", "Suspended"),
        ("TERMINATED", "Terminated"),
    ]
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default="ACTIVE",
    )

    hire_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)

    timezone = models.CharField(max_length=64, default="UTC")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_code} - {self.get_full_name() or self.username}"
