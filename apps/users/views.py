from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Department, Role, Employee
from .serializers import DepartmentSerializer, RoleSerializer, EmployeeSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    Manage departments.

    - Authenticated users can list/retrieve (for dropdowns, etc.).
    - Only admins can create/update/delete.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

class RoleViewSet(viewsets.ModelViewSet):
    """
    Manage roles.

    - Authenticated users can list/retrieve.
    - Only admins can create/update/delete.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    View and manage employees.

    - Non-staff users can only see (and potentially update) their own record.
    - Admins can see and manage all employees.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_permissions(self):
        # Only admins can create or delete employees
        if self.action in ["create", "destroy"]:
            return [IsAdminUser()]
        # Authenticated users can list/retrieve/update within their queryset
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Employee.objects.all()
        return Employee.objects.filter(id=user.id)
