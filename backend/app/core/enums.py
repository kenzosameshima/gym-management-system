from enum import Enum


class UserRole(str, Enum):  # noqa: UP042
    ADMIN = "ADMIN"
    RECEPTIONIST = "RECEPTIONIST"
    INSTRUCTOR = "INSTRUCTOR"


class StudentStatus(str, Enum):  # noqa: UP042
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class PlanStatus(str, Enum):  # noqa: UP042
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class WorkoutPlanStatus(str, Enum):  # noqa: UP042
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ExerciseStatus(str, Enum):  # noqa: UP042
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class EnrollmentStatus(str, Enum):  # noqa: UP042
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class PaymentStatus(str, Enum):  # noqa: UP042
    PENDING = "PENDING"
    PAID = "PAID"
    OVERDUE = "OVERDUE"


class AccessDeniedReason(str, Enum):  # noqa: UP042
    STUDENT_NOT_FOUND = "STUDENT_NOT_FOUND"
    STUDENT_INACTIVE = "STUDENT_INACTIVE"
    NO_ACTIVE_ENROLLMENT = "NO_ACTIVE_ENROLLMENT"
    ENROLLMENT_EXPIRED = "ENROLLMENT_EXPIRED"
    PAYMENT_OVERDUE = "PAYMENT_OVERDUE"
