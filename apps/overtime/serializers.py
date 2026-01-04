from rest_framework import serializers
from .models import OvertimeRule, OvertimeEntry


class OvertimeRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OvertimeRule
        fields = [
            "id",
            "name",
            "scope",
            "threshold_hours",
            "multiplier",
            "is_active",
            "department",
            "role",
            "created_at",
            "updated_at",
        ]


class OvertimeEntrySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)
    employee_code = serializers.CharField(source="employee.employee_code", read_only=True)

    class Meta:
        model = OvertimeEntry
        fields = [
            "id",
            "employee",
            "employee_name",
            "employee_code",
            "rule",
            "period_start",
            "period_end",
            "hours_regular",
            "hours_overtime",
            "base_rate",
            "overtime_multiplier",
            "overtime_amount",
            "finalized_at",
            "is_locked",
        ]
        read_only_fields = [
            "hours_regular",
            "hours_overtime",
            "base_rate",
            "overtime_multiplier",
            "overtime_amount",
            "finalized_at",
        ]
