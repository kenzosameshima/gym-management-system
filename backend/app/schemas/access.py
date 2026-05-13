from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import AccessDeniedReason


class AccessCheckRequest(BaseModel):
    cpf: str = Field(min_length=11, max_length=14)


class AccessDecision(BaseModel):
    student_id: int | None
    student_name: str | None = None
    cpf_attempted: str
    allowed: bool
    reason: AccessDeniedReason | None


class AccessLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int | None
    cpf_attempted: str
    accessed_at: datetime
    allowed: bool
    reason: AccessDeniedReason | None
