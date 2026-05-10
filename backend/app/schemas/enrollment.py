from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import EnrollmentStatus, PaymentStatus


class EnrollmentCreate(BaseModel):
    student_id: int = Field(gt=0, examples=[1])
    plan_id: int = Field(gt=0, examples=[1])
    start_date: date = Field(examples=["2026-05-08"])
    first_payment_due_date: date | None = Field(default=None, examples=["2026-05-08"])


class EnrollmentUpdate(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    status: EnrollmentStatus | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "EnrollmentUpdate":
        if self.start_date is not None and self.end_date is not None:
            if self.end_date < self.start_date:
                raise ValueError("End date cannot be before start date.")
        return self


class EnrollmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    plan_id: int
    start_date: date
    end_date: date
    status: EnrollmentStatus
    payment_status: PaymentStatus | None
    created_at: datetime
    updated_at: datetime
