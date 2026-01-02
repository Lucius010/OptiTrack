from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.users.serializers import EmployeeSerializer
from .utils import (
    get_currently_clocked_in_employees, 
    get_department_occupancy, 
    calculate_daily_stats
)

class DashboardLiveView(APIView):
    """
    Returns a list of all employees currently clocked in.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        active_employees = get_currently_clocked_in_employees()
        serializer = EmployeeSerializer(active_employees, many=True)
        return Response(
            {
                "count": active_employees.count() if hasattr(active_employees, "count") else len(active_employees),
                "employees": serializer.data,
            },
            status=status.HTTP_200_OK,
        )



class DepartmentStatsView(APIView):
    """
    Returns the count of active employees grouped by department.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Highlight: Provides data for charts or heatmaps
        occupancy_data = get_department_occupancy()
        return Response(occupancy_data, status=status.HTTP_200_OK)


class EmployeeDailySummaryView(APIView):
    """
    Returns the total hours worked for the logged-in employee today.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Highlight: Uses the daily stats util for the current user
        stats = calculate_daily_stats(request.user)
        return Response(stats, status=status.HTTP_200_OK)
