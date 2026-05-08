import re
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.enums import StudentStatus

CPF_PATTERN = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$")


class StudentBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    cpf: str = Field(min_length=11, max_length=14)
    birth_date: date
    phone: str | None = Field(default=None, max_length=32)
    email: EmailStr
    address: str | None = None
    status: StudentStatus = StudentStatus.ACTIVE

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        if CPF_PATTERN.fullmatch(value) is None:
            raise ValueError("CPF must contain 11 digits or use 000.000.000-00 format.")
        return value

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Birth date cannot be in the future.")
        return value


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    cpf: str | None = Field(default=None, min_length=11, max_length=14)
    birth_date: date | None = None
    phone: str | None = Field(default=None, max_length=32)
    email: EmailStr | None = None
    address: str | None = None
    status: StudentStatus | None = None

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str | None) -> str | None:
        if value is not None and CPF_PATTERN.fullmatch(value) is None:
            raise ValueError("CPF must contain 11 digits or use 000.000.000-00 format.")
        return value

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("Birth date cannot be in the future.")
        return value


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    cpf: str
    birth_date: date
    phone: str | None
    email: EmailStr
    address: str | None
    status: StudentStatus
    created_at: datetime
    updated_at: datetime
