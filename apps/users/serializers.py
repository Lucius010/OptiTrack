from rest_framework import serializers
from .models import Department, Role, Employee

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'is_active']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'is_active']


class EmployeeSerializer(serializers.ModelSerializer):
    # ==========================================================
    # UPDATED: Nested fields for better data display
    # ==========================================================
    department_name = serializers.CharField(source='department.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'employee_code', 'department', 'department_name', 'role', 'role_name',
            'employment_status', 'hire_date', 'timezone',
            # ==========================================================
            # HIGHLIGHT: New Pay Fields integrated into the Serializer
            # ==========================================================
            'pay_type', 'pay_rate'
        ]
        # Password is write-only for security; pay_rate might be sensitive
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_pay_rate(self, value):
        """
        Custom Validation: Ensure pay rate isn't negative.
        """
        if value < 0:
            raise serializers.ValidationError("Pay rate cannot be negative.")
        return value