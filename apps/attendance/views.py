from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from apps.attendance.models import AttendanceSession
from django.utils import timezone
from django.db.models import Sum


from .services import AttendanceService
from .serializers import WorkSessionSerializer, AttendanceDaySummarySerializer
from .models import WorkSession, AttendanceDaySummary

class ClockInView(APIView):
    """
    Endpoint to start a work session.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ==========================================================
        # LOGIC: Use the currently logged-in user as the employee
        # ==========================================================
        employee = request.user
        
        try:
            # Call our Service to handle the database creation
            session = AttendanceService.clock_in(employee, source="WEB")
            
            # Serialize the new session to return to the frontend
            serializer = WorkSessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Highlight: Returns the error message if already clocked in
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ClockOutView(APIView):
    """
    Endpoint to end the current active work session.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        employee = request.user
        
        try:
            # Call our Service to calculate duration and close the session
            session = AttendanceService.clock_out(employee, source="WEB")
            
            # Highlight: We calculate earnings immediately upon clock-out
            earnings = AttendanceService.calculate_earnings(session)
            
            serializer = WorkSessionSerializer(session)
            data = serializer.data
            data['session_earnings'] = earnings  # Add earnings to the response
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class WorkSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides the list of all work sessions (e.g., /api/v1/attendance/sessions/)
    """
    queryset = WorkSession.objects.all()
    serializer_class = WorkSessionSerializer
    permission_classes = [IsAuthenticated]

class AttendanceDaySummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides the daily totals (e.g., /api/v1/attendance/summaries/)
    """
    queryset = AttendanceDaySummary.objects.all()
    serializer_class = AttendanceDaySummarySerializer
    permission_classes = [IsAuthenticated]

class DailyReportView(APIView):
    def get(self, request):
        today = timezone.now().date()
        sessions = AttendanceSession.objects.filter(work_date=today)
        
        return Response({
            "date": today,
            "total_active_employees": sessions.filter(clock_out__isnull=True).count(),
            "total_hours_today": sessions.aggregate(Sum('duration'))['duration__sum'] or 0,
        })