from typing import Optional
from pydantic import BaseModel


class SectionRead(BaseModel):
    id: int
    name: str
    head_id: int | None

    class Config:
        from_attributes = True


class SectionCreate(BaseModel):
    name: str
    head_id: Optional[int] = None


class UserPaginationResponse(BaseModel):
    items: list[SectionRead]
    next_cursor: int
    size: int
