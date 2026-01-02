class AttendanceError(Exception):
    """Base error for attendance operations."""


class AlreadyClockedInError(AttendanceError):
    """Raised when an employee tries to clock in with an open session."""


class NotClockedInError(AttendanceError):
    """Raised when an employee tries to clock out with no open session."""
