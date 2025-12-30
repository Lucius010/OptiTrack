from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Department, Role, Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    search_fields = ("code", "name")
    list_filter = ("is_active",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("HR Info", {
            "fields": (
                "employee_code",
                "department",
                "role",
                "employment_status",
                "hire_date",
                "termination_date",
                "timezone",
            )
        }),
    )
    list_display = UserAdmin.list_display + ("employee_code", "department", "role", "employment_status")
    list_filter = UserAdmin.list_filter + ("department", "role", "employment_status")
