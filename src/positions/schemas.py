from pydantic import BaseModel


class PositionRead(BaseModel):
    id: int
    sectuin_id: int
    name: str


class PositionCreate(BaseModel):
    section_id: int | None
    name: str
