from datetime import date

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ApplicationError
from app.repositories.report_repository import ReportRepository, get_report_repository
from app.schemas.reports import (
    ActiveStudentsReport,
    DailyAccessReport,
    DefaultersReport,
    MostUsedPlansReport,
    RevenueSummaryReport,
    WorkoutSummaryReport,
)


class ReportService:
    def __init__(self, repository: ReportRepository) -> None:
        self._repository = repository

    async def active_students(self, session: AsyncSession) -> ActiveStudentsReport:
        students = await self._repository.active_students(session)
        return ActiveStudentsReport(total=len(students), students=students)

    async def defaulter_students(self, session: AsyncSession) -> DefaultersReport:
        students = await self._repository.defaulter_students(session)
        return DefaultersReport(total=len(students), students=students)

    async def most_used_plans(self, session: AsyncSession) -> MostUsedPlansReport:
        plans = await self._repository.most_used_plans(session)
        return MostUsedPlansReport(plans=plans)

    async def revenue_summary(
        self,
        session: AsyncSession,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> RevenueSummaryReport:
        self._validate_date_range(start_date=start_date, end_date=end_date)
        return await self._repository.revenue_summary(
            session,
            start_date=start_date,
            end_date=end_date,
        )

    async def daily_access(
        self,
        session: AsyncSession,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> DailyAccessReport:
        self._validate_date_range(start_date=start_date, end_date=end_date)
        days = await self._repository.daily_access(
            session,
            start_date=start_date,
            end_date=end_date,
        )
        return DailyAccessReport(days=days)

    async def workout_summary(self, session: AsyncSession) -> WorkoutSummaryReport:
        return await self._repository.workout_summary(session)

    @staticmethod
    def _validate_date_range(*, start_date: date | None, end_date: date | None) -> None:
        if start_date is not None and end_date is not None and start_date > end_date:
            raise ApplicationError(
                code="INVALID_DATE_RANGE",
                message="start_date must be less than or equal to end_date.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )


def get_report_service(
    repository: ReportRepository = Depends(get_report_repository),
) -> ReportService:
    return ReportService(repository=repository)
