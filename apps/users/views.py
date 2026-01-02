from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Department, Role, Employee
from .serializers import DepartmentSerializer, RoleSerializer, EmployeeSerializer

# ==========================================================
# 1. DEPARTMENT VIEWSET
# ==========================================================
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated] # Managers/Staff can view depts


# ==========================================================
# 2. ROLE VIEWSET
# ==========================================================
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


# ==========================================================
# 3. EMPLOYEE VIEWSET
# ==========================================================
class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Handles all Employee logic: listing, details, and updates.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    # Highlight: Custom permissions
    def get_permissions(self):
        # Only Admins can delete or create employees
        if self.action in ['create', 'destroy']:
            return [IsAdminUser()]
        # Any logged-in user can view the list
        return [IsAuthenticated()]

    # Highlight: Filter to see only current user's profile if not admin
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Employee.objects.all()
        return Employee.objects.filter(id=user.id)