from pydantic import BaseModel


class LiveHealthResponse(BaseModel):
    status: str


class ReadyHealthResponse(BaseModel):
    status: str
    database: str
