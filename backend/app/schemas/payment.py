from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import PaymentStatus


class PaymentCreate(BaseModel):
    enrollment_id: int = Field(gt=0, examples=[1])
    amount: Decimal = Field(gt=0, decimal_places=2, examples=["99.90"])
    due_date: date = Field(examples=["2026-05-08"])
    status: PaymentStatus = PaymentStatus.PENDING


class PaymentUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    due_date: date | None = None
    payment_date: date | None = None
    status: PaymentStatus | None = None

    @model_validator(mode="after")
    def validate_payment_date(self) -> "PaymentUpdate":
        if self.status == PaymentStatus.PAID and self.payment_date is None:
            self.payment_date = date.today()
        if self.status != PaymentStatus.PAID and self.payment_date is not None:
            raise ValueError("Payment date is only valid for paid payments.")
        return self


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    enrollment_id: int
    amount: Decimal
    due_date: date
    payment_date: date | None
    status: PaymentStatus
    created_at: datetime
