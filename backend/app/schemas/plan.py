from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import PlanStatus


class PlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    price: Decimal = Field(gt=0, decimal_places=2)
    duration_days: int = Field(gt=0)
    status: PlanStatus = PlanStatus.ACTIVE


class PlanUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    duration_days: int | None = Field(default=None, gt=0)
    status: PlanStatus | None = None


class PlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal
    duration_days: int
    status: PlanStatus
    created_at: datetime
    updated_at: datetime
