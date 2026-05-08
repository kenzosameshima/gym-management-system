from fastapi import APIRouter, Depends, Query, status

from app.auth.permissions import require_roles
from app.core.enums import PaymentStatus, UserRole
from app.database.session import AsyncSessionDependency
from app.models.payment import Payment
from app.schemas.pagination import Page
from app.schemas.payment import PaymentCreate, PaymentRead, PaymentUpdate
from app.services.payment_service import PaymentService, get_payment_service

router = APIRouter(prefix="/api/payments", tags=["payments"])

PAYMENT_MANAGEMENT_ROLES = (UserRole.ADMIN, UserRole.RECEPTIONIST)


@router.post(
    "",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create payment",
    description="Creates a payment linked to an enrollment.",
    dependencies=[Depends(require_roles(*PAYMENT_MANAGEMENT_ROLES))],
)
async def create_payment(
    payload: PaymentCreate,
    session: AsyncSessionDependency,
    service: PaymentService = Depends(get_payment_service),
) -> Payment:
    return await service.create_payment(session=session, payload=payload)


@router.get(
    "",
    response_model=Page[PaymentRead],
    status_code=status.HTTP_200_OK,
    summary="List payments",
    description="Returns a paginated payment list with optional enrollment and status filters.",
    dependencies=[Depends(require_roles(*PAYMENT_MANAGEMENT_ROLES))],
)
async def list_payments(
    session: AsyncSessionDependency,
    limit: int = Query(default=20, gt=0, le=100),
    offset: int = Query(default=0, ge=0),
    enrollment_id: int | None = Query(default=None, gt=0),
    payment_status: PaymentStatus | None = Query(default=None, alias="status"),
    student_search: str | None = Query(default=None, min_length=1, max_length=320),
    service: PaymentService = Depends(get_payment_service),
) -> Page[PaymentRead]:
    return await service.list_payments(
        session=session,
        limit=limit,
        offset=offset,
        enrollment_id=enrollment_id,
        status_filter=payment_status,
        student_search=student_search,
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentRead,
    status_code=status.HTTP_200_OK,
    summary="Get payment",
    description="Returns one payment by id.",
    dependencies=[Depends(require_roles(*PAYMENT_MANAGEMENT_ROLES))],
)
async def get_payment(
    payment_id: int,
    session: AsyncSessionDependency,
    service: PaymentService = Depends(get_payment_service),
) -> Payment:
    return await service.get_payment(session=session, payment_id=payment_id)


@router.put(
    "/{payment_id}",
    response_model=PaymentRead,
    status_code=status.HTTP_200_OK,
    summary="Update payment",
    description="Updates payment amount, due date, payment date, or status.",
    dependencies=[Depends(require_roles(*PAYMENT_MANAGEMENT_ROLES))],
)
async def update_payment(
    payment_id: int,
    payload: PaymentUpdate,
    session: AsyncSessionDependency,
    service: PaymentService = Depends(get_payment_service),
) -> Payment:
    return await service.update_payment(session=session, payment_id=payment_id, payload=payload)


@router.patch(
    "/{payment_id}/pay",
    response_model=PaymentRead,
    status_code=status.HTTP_200_OK,
    summary="Mark payment paid",
    description="Marks a payment as PAID and sets payment_date to today.",
    dependencies=[Depends(require_roles(*PAYMENT_MANAGEMENT_ROLES))],
)
async def mark_payment_paid(
    payment_id: int,
    session: AsyncSessionDependency,
    service: PaymentService = Depends(get_payment_service),
) -> Payment:
    return await service.mark_payment_paid(session=session, payment_id=payment_id)
