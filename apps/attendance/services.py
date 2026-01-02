from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import WorkSession

class AttendanceService:
    """
    Business logic for clock-in, clock-out, and earnings calculation.
    """

    @staticmethod
    def clock_in(employee, source="WEB"):
        """
        Starts a new work session if the employee isn't already clocked in.
        """
        # ==========================================================
        # RULE: Check for existing active sessions
        # ==========================================================
        active_session = WorkSession.objects.filter(
            employee=employee, 
            clock_out_at__isnull=True
        ).exists()

        if active_session:
            raise ValidationError("You are already clocked in. Please clock out first.")

        # Create and return the session
        return WorkSession.objects.create(
            employee=employee,
            work_date=timezone.now().date(),
            clock_in_at=timezone.now(),
            clock_in_source=source
        )

    @staticmethod
    def clock_out(employee, source="WEB"):
        """
        Ends the current active session and calculates duration.
        """
        # Highlight: Find the most recent session without a clock-out time
        try:
            session = WorkSession.objects.get(
                employee=employee, 
                clock_out_at__isnull=True
            )
        except WorkSession.DoesNotExist:
            raise ValidationError("No active session found. Please clock in first.")

        # Highlight: Finalize the session
        session.clock_out_at = timezone.now()
        session.clock_out_source = source
        
        # Django handles the duration calculation automatically
        session.total_work_duration = session.clock_out_at - session.clock_in_at
        session.save()
        return session

    @staticmethod
    def calculate_earnings(session):
        """
        Calculates pay based on the Pay Type set in the Employee model.
        ==========================================================
        NEW: Professional Pay Engine
        ==========================================================
        """
        employee = session.employee
        # Convert duration to hours (as a Decimal for precision)
        duration_hours = Decimal(session.total_work_duration.total_seconds()) / Decimal(3600)
        
        # 1. HOURLY LOGIC
        if employee.pay_type == "HOURLY":
            return round(duration_hours * employee.pay_rate, 2)

        # 2. DAILY LOGIC
        elif employee.pay_type == "DAILY":
            # If they worked at least 1 hour, they get the full day rate
            if duration_hours >= Decimal("1.0"):
                return employee.pay_rate
            return Decimal("0.00")

        # 3. MONTHLY LOGIC
        elif employee.pay_type == "MONTHLY":
            # Typically handled by a separate monthly payroll run, 
            # but we can return 0 or a prorated amount here.
            return Decimal("0.00")

        return Decimal("0.00")