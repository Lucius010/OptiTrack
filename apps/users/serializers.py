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
    department_name = serializers.CharField(source="department.name", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_code",
            "username",
            "full_name",
            "department",
            "department_name",
            "role",
            "role_name",
            "employment_status",
            "hire_date",
            "timezone",
        ]
        extra_kwargs = {
            "department": {"read_only": True},
            "role": {"read_only": True},
        }
