from django.contrib import admin
from .models import OvertimeRule, OvertimeEntry


@admin.register(OvertimeRule)
class OvertimeRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "scope", "threshold_hours", "multiplier", "department", "role", "is_active")
    list_filter = ("scope", "is_active", "department", "role")
    search_fields = ("name",)


@admin.register(OvertimeEntry)
class OvertimeEntryAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "rule",
        "period_start",
        "period_end",
        "hours_regular",
        "hours_overtime",
        "overtime_amount",
        "is_locked",
    )
    list_filter = ("rule", "employee", "is_locked", "period_start", "period_end")
    search_fields = ("employee__username", "employee__employee_code")
