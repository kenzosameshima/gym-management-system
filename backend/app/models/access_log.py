from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import AccessDeniedReason
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.student import Student


class AccessLog(Base):
    __tablename__ = "access_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int | None] = mapped_column(
        ForeignKey("students.id"),
        index=True,
        nullable=True,
    )
    cpf_attempted: Mapped[str] = mapped_column(String(14), index=True, nullable=False)
    accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
        nullable=False,
    )
    allowed: Mapped[bool] = mapped_column(nullable=False)
    reason: Mapped[AccessDeniedReason | None] = mapped_column(
        Enum(AccessDeniedReason, native_enum=False, length=40),
        nullable=True,
    )

    student: Mapped["Student | None"] = relationship()
