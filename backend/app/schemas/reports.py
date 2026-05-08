from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.core.enums import StudentStatus


class ReportDateRange(BaseModel):
    start_date: date | None = None
    end_date: date | None = None


class ActiveStudentReportItem(BaseModel):
    id: int
    name: str
    cpf: str
    email: str
    status: StudentStatus


class ActiveStudentsReport(BaseModel):
    total: int = Field(ge=0)
    students: list[ActiveStudentReportItem]


class DefaulterStudentReportItem(BaseModel):
    student_id: int
    name: str
    cpf: str
    email: str
    overdue_amount: Decimal
    overdue_payments: int = Field(ge=0)


class DefaultersReport(BaseModel):
    total: int = Field(ge=0)
    students: list[DefaulterStudentReportItem]


class MostUsedPlanReportItem(BaseModel):
    plan_id: int
    plan_name: str
    enrollments_count: int = Field(ge=0)


class MostUsedPlansReport(BaseModel):
    plans: list[MostUsedPlanReportItem]


class RevenueSummaryReport(BaseModel):
    expected_revenue: Decimal
    received_revenue: Decimal
    overdue_revenue: Decimal
    pending_revenue: Decimal


class DailyAccessReportItem(BaseModel):
    date: date
    total_attempts: int = Field(ge=0)
    allowed_count: int = Field(ge=0)
    blocked_count: int = Field(ge=0)


class DailyAccessReport(BaseModel):
    days: list[DailyAccessReportItem]


class WorkoutSummaryReport(BaseModel):
    active_workout_plans: int = Field(ge=0)
    inactive_workout_plans: int = Field(ge=0)
    total_exercises: int = Field(ge=0)
    exercise_progress_records: int = Field(ge=0)
