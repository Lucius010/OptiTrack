from django.utils import timezone
from django.db.models import Sum

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.attendance.models import WorkSession, AttendanceDaySummary
from apps.attendance import services
from apps.attendance.exceptions import (
    AlreadyClockedInError,
    NotClockedInError,
)
from .serializers import WorkSessionSerializer, AttendanceDaySummarySerializer

class ClockInView(APIView):
    """
    Start a work session for the authenticated employee.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        employee = request.user

        try:
            session = services.clock_in(employee, source="WEB")
        except AlreadyClockedInError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = WorkSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ClockOutView(APIView):
    """
    End the current active work session for the authenticated employee.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        employee = request.user

        try:
            session = services.clock_out(employee, source="WEB")
        except NotClockedInError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = WorkSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
class WorkSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only access to work sessions.
    """
    queryset = WorkSession.objects.all().select_related("employee")
    serializer_class = WorkSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(employee=self.request.user) # for security

class AttendanceDaySummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only access to daily attendance summaries.
    """
    queryset = AttendanceDaySummary.objects.all().select_related("employee")
    serializer_class = AttendanceDaySummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(employee=self.request.user)

class DailyReportView(APIView):
    """
    Simple daily report for the authenticated employee.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        employee = request.user

        sessions = WorkSession.objects.filter(
            employee=employee,
            work_date=today,
        )

        total_seconds = (
            sessions.aggregate(total=Sum("total_work_duration"))["total"] or 0
        )

        return Response(
            {
                "date": today,
                "total_sessions": sessions.count(),
                "total_work_seconds": int(total_seconds.total_seconds())
                if hasattr(total_seconds, "total_seconds")
                else int(total_seconds),
            },
            status=status.HTTP_200_OK,
        )
