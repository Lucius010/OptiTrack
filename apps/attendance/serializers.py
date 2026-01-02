from rest_framework import serializers
from .models import WorkSession, AttendanceDaySummary

# ==========================================================
# 1. WORK SESSION SERIALIZER (Existing)
# ==========================================================
class WorkSessionSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.get_full_name')
    duration_display = serializers.SerializerMethodField()

    class Meta:
        model = WorkSession
        fields = [
            'id', 'employee', 'employee_name', 'work_date',
            'clock_in_at', 'clock_out_at', 'clock_in_source',
            'total_work_duration', 'duration_display'
        ]

    def get_duration_display(self, obj):
        if obj.total_work_duration:
            total_seconds = int(obj.total_work_duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return "00:00:00"

# ==========================================================
# 2. ATTENDANCE SUMMARY SERIALIZER (NEW - Fixes 404)
# ==========================================================
class AttendanceDaySummarySerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.get_full_name')
    
    class Meta:
        model = AttendanceDaySummary
        fields = [
            'id', 'employee', 'employee_name', 'work_date', 
            'total_work_duration', 'total_earnings'
        ]