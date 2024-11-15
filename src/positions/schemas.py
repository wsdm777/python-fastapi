from typing import Optional
from pydantic import BaseModel


class PositionRead(BaseModel):
    id: int
    sectuin_id: int | None
    name: str


class PositionCreate(BaseModel):
    section_id: Optional[int]
    name: str
