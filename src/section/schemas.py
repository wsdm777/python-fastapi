from typing import Optional
from pydantic import BaseModel, EmailStr


class SectionRead(BaseModel):
    id: int
    name: str
    head_email: EmailStr | None

    class Config:
        from_attributes = True


class SectionCreate(BaseModel):
    name: str
    head_email: EmailStr = None


class UserPaginationResponse(BaseModel):
    items: list[SectionRead]
    next_cursor: int
    size: int
