from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime

from .services import calculate_overtime_for_period
from .models import OvertimeRule, OvertimeEntry
from .serializers import OvertimeRuleSerializer, OvertimeEntrySerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class OvertimeRuleViewSet(viewsets.ModelViewSet):
    queryset = OvertimeRule.objects.all()
    serializer_class = OvertimeRuleSerializer
    permission_classes = [IsAdminOrReadOnly]

class IsAdminUser(permissions.IsAdminUser):
    pass

class OvertimeEntryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OvertimeEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = OvertimeEntry.objects.select_related("employee", "rule")
        user = self.request.user

        if user.is_staff:
            return qs
        return qs.filter(employee=user)

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser])
    def recalculate(self, request):
        """
        Admin-only: recalculate overtime entries for a given date range.
        Body: {"period_start": "2025-01-01", "period_end": "2025-01-31"}
        """
        period_start = request.data.get("period_start")
        period_end = request.data.get("period_end")

        if not period_start or not period_end:
            return Response(
                {"detail": "period_start and period_end are required (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start = datetime.strptime(period_start, "%Y-%m-%d").date()
            end = datetime.strptime(period_end, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if start > end:
            return Response(
                {"detail": "period_start must be before or equal to period_end."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        calculate_overtime_for_period(start, end)

        return Response(
            {"detail": "Overtime recalculation completed.", "period_start": period_start, "period_end": period_end},
            status=status.HTTP_200_OK,
        )