from datetime import date

from fastapi import APIRouter, Depends, Query, status

from app.auth.permissions import require_roles
from app.core.enums import UserRole
from app.database.session import AsyncSessionDependency
from app.schemas.reports import (
    ActiveStudentsReport,
    DailyAccessReport,
    DefaultersReport,
    MostUsedPlansReport,
    RevenueSummaryReport,
    WorkoutSummaryReport,
)
from app.services.report_service import ReportService, get_report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])

MANAGEMENT_REPORT_ROLES = (UserRole.ADMIN, UserRole.RECEPTIONIST)
WORKOUT_REPORT_ROLES = (UserRole.ADMIN, UserRole.INSTRUCTOR)


@router.get(
    "/students/active",
    response_model=ActiveStudentsReport,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*MANAGEMENT_REPORT_ROLES))],
)
async def active_students_report(
    session: AsyncSessionDependency,
    service: ReportService = Depends(get_report_service),
) -> ActiveStudentsReport:
    return await service.active_students(session)


@router.get(
    "/students/defaulters",
    response_model=DefaultersReport,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*MANAGEMENT_REPORT_ROLES))],
)
async def defaulters_report(
    session: AsyncSessionDependency,
    service: ReportService = Depends(get_report_service),
) -> DefaultersReport:
    return await service.defaulter_students(session)


@router.get(
    "/plans/most-used",
    response_model=MostUsedPlansReport,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*MANAGEMENT_REPORT_ROLES))],
)
async def most_used_plans_report(
    session: AsyncSessionDependency,
    service: ReportService = Depends(get_report_service),
) -> MostUsedPlansReport:
    return await service.most_used_plans(session)


@router.get(
    "/revenue/summary",
    response_model=RevenueSummaryReport,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*MANAGEMENT_REPORT_ROLES))],
)
async def revenue_summary_report(
    session: AsyncSessionDependency,
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    service: ReportService = Depends(get_report_service),
) -> RevenueSummaryReport:
    return await service.revenue_summary(
        session,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/access/daily",
    response_model=DailyAccessReport,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*MANAGEMENT_REPORT_ROLES))],
)
async def daily_access_report(
    session: AsyncSessionDependency,
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    service: ReportService = Depends(get_report_service),
) -> DailyAccessReport:
    return await service.daily_access(
        session,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/workouts/summary",
    response_model=WorkoutSummaryReport,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*WORKOUT_REPORT_ROLES))],
)
async def workout_summary_report(
    session: AsyncSessionDependency,
    service: ReportService = Depends(get_report_service),
) -> WorkoutSummaryReport:
    return await service.workout_summary(session)
