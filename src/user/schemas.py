from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class MessageResponse(BaseModel):
    Message: str


class UserRead(BaseModel):
    id: int
    name: str
    surname: str
    position_id: int | None
    email: EmailStr
    joined_at: date
    birthday: date

    model_config = ConfigDict(from_attributes=True)


class UserPagination(BaseModel):
    id: int
    name: str
    surname: str
    is_admin: bool
    position_name: str | None
    email: EmailStr
    on_vacation: bool


class CursorInfo(BaseModel):
    last_surname: str | None
    last_name: str | None


class UserPaginationResponse(BaseModel):
    items: list[UserPagination]
    next_cursor: CursorInfo
    final: bool
    size: int


class UserInfo(BaseModel):
    id: int
    name: str
    surname: str
    position_name: str | None
    section_name: str | None
    email: EmailStr
    joined_at: date
    birthday: date
    is_on_vacation: bool
    is_superuser: bool

    model_config = ConfigDict(from_attributes=True)


class UserPassChange(BaseModel):
    new_password: str = Field(min_length=4)
