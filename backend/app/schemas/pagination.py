from pydantic import BaseModel, Field


class Page[T](BaseModel):
    items: list[T]
    total: int = Field(ge=0)
    limit: int = Field(gt=0, le=100)
    offset: int = Field(ge=0)
