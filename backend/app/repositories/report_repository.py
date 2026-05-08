from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Select, case, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import PaymentStatus, StudentStatus, WorkoutPlanStatus
from app.models.access_log import AccessLog
from app.models.enrollment import Enrollment
from app.models.exercise import Exercise
from app.models.exercise_progress import ExerciseProgress
from app.models.payment import Payment
from app.models.plan import Plan
from app.models.student import Student
from app.models.workout_plan import WorkoutPlan
from app.schemas.reports import (
    ActiveStudentReportItem,
    DailyAccessReportItem,
    DefaulterStudentReportItem,
    MostUsedPlanReportItem,
    RevenueSummaryReport,
    WorkoutSummaryReport,
)


class ReportRepository:
    async def active_students(self, session: AsyncSession) -> list[ActiveStudentReportItem]:
        result = await session.execute(
            select(Student.id, Student.name, Student.cpf, Student.email, Student.status)
            .where(Student.status == StudentStatus.ACTIVE)
            .order_by(Student.id)
        )
        return [
            ActiveStudentReportItem(
                id=row.id,
                name=row.name,
                cpf=row.cpf,
                email=row.email,
                status=row.status,
            )
            for row in result.all()
        ]

    async def defaulter_students(self, session: AsyncSession) -> list[DefaulterStudentReportItem]:
        overdue_amount = func.coalesce(func.sum(Payment.amount), Decimal("0.00"))
        overdue_payments = func.count(Payment.id)
        result = await session.execute(
            select(
                Student.id.label("student_id"),
                Student.name,
                Student.cpf,
                Student.email,
                overdue_amount.label("overdue_amount"),
                overdue_payments.label("overdue_payments"),
            )
            .join(Enrollment, Enrollment.student_id == Student.id)
            .join(Payment, Payment.enrollment_id == Enrollment.id)
            .where(Payment.status == PaymentStatus.OVERDUE)
            .group_by(Student.id, Student.name, Student.cpf, Student.email)
            .order_by(Student.id)
        )
        return [
            DefaulterStudentReportItem(
                student_id=row.student_id,
                name=row.name,
                cpf=row.cpf,
                email=row.email,
                overdue_amount=row.overdue_amount,
                overdue_payments=row.overdue_payments,
            )
            for row in result.all()
        ]

    async def most_used_plans(self, session: AsyncSession) -> list[MostUsedPlanReportItem]:
        enrollments_count = func.count(Enrollment.id)
        result = await session.execute(
            select(
                Plan.id.label("plan_id"),
                Plan.name.label("plan_name"),
                enrollments_count.label("enrollments_count"),
            )
            .outerjoin(Enrollment, Enrollment.plan_id == Plan.id)
            .group_by(Plan.id, Plan.name)
            .order_by(enrollments_count.desc(), Plan.id)
        )
        return [
            MostUsedPlanReportItem(
                plan_id=row.plan_id,
                plan_name=row.plan_name,
                enrollments_count=row.enrollments_count,
            )
            for row in result.all()
        ]

    async def revenue_summary(
        self,
        session: AsyncSession,
        *,
        start_date: date | None,
        end_date: date | None,
    ) -> RevenueSummaryReport:
        statement = self._payment_date_filtered_statement(start_date=start_date, end_date=end_date)
        paid_amount = case((Payment.status == PaymentStatus.PAID, Payment.amount), else_=0)
        overdue_amount = case((Payment.status == PaymentStatus.OVERDUE, Payment.amount), else_=0)
        pending_amount = case((Payment.status == PaymentStatus.PENDING, Payment.amount), else_=0)
        result = await session.execute(
            statement.with_only_columns(
                func.coalesce(func.sum(Payment.amount), Decimal("0.00")).label(
                    "expected_revenue"
                ),
                func.coalesce(func.sum(paid_amount), Decimal("0.00")).label("received_revenue"),
                func.coalesce(func.sum(overdue_amount), Decimal("0.00")).label("overdue_revenue"),
                func.coalesce(func.sum(pending_amount), Decimal("0.00")).label("pending_revenue"),
            )
        )
        row = result.one()
        return RevenueSummaryReport(
            expected_revenue=row.expected_revenue,
            received_revenue=row.received_revenue,
            overdue_revenue=row.overdue_revenue,
            pending_revenue=row.pending_revenue,
        )

    async def daily_access(
        self,
        session: AsyncSession,
        *,
        start_date: date | None,
        end_date: date | None,
    ) -> list[DailyAccessReportItem]:
        access_date = cast(AccessLog.accessed_at, Date)
        allowed_count = func.sum(case((AccessLog.allowed.is_(True), 1), else_=0))
        blocked_count = func.sum(case((AccessLog.allowed.is_(False), 1), else_=0))
        statement = select(
            access_date.label("date"),
            func.count(AccessLog.id).label("total_attempts"),
            allowed_count.label("allowed_count"),
            blocked_count.label("blocked_count"),
        )
        if start_date is not None:
            statement = statement.where(access_date >= start_date)
        if end_date is not None:
            statement = statement.where(access_date <= end_date)
        result = await session.execute(
            statement.group_by(access_date).order_by(access_date)
        )
        return [
            DailyAccessReportItem(
                date=row.date,
                total_attempts=row.total_attempts,
                allowed_count=row.allowed_count,
                blocked_count=row.blocked_count,
            )
            for row in result.all()
        ]

    async def workout_summary(self, session: AsyncSession) -> WorkoutSummaryReport:
        active_workout_plans = await self._scalar_count(
            session,
            select(func.count(WorkoutPlan.id)).where(
                WorkoutPlan.status == WorkoutPlanStatus.ACTIVE
            ),
        )
        inactive_workout_plans = await self._scalar_count(
            session,
            select(func.count(WorkoutPlan.id)).where(
                WorkoutPlan.status == WorkoutPlanStatus.INACTIVE
            ),
        )
        total_exercises = await self._scalar_count(session, select(func.count(Exercise.id)))
        exercise_progress_records = await self._scalar_count(
            session,
            select(func.count(ExerciseProgress.id)),
        )
        return WorkoutSummaryReport(
            active_workout_plans=active_workout_plans,
            inactive_workout_plans=inactive_workout_plans,
            total_exercises=total_exercises,
            exercise_progress_records=exercise_progress_records,
        )

    def _payment_date_filtered_statement(
        self,
        *,
        start_date: date | None,
        end_date: date | None,
    ) -> Select[tuple[Payment]]:
        statement = select(Payment)
        if start_date is not None:
            statement = statement.where(Payment.due_date >= start_date)
        if end_date is not None:
            statement = statement.where(Payment.due_date <= end_date)
        return statement

    async def _scalar_count(self, session: AsyncSession, statement: Select[tuple[int]]) -> int:
        result = await session.execute(statement)
        return result.scalar_one()


def get_report_repository() -> ReportRepository:
    return ReportRepository()
