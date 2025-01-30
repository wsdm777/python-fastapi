from datetime import date, datetime
from typing import Optional
from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, field_validator


class MessageResponse(BaseModel):
    Message: str


class UserRead(schemas.BaseUser[int]):
    id: int
    name: str
    surname: str
    position_id: int | None
    email: EmailStr
    joined_at: date
    birthday: date

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    name: str
    surname: str
    position_id: int | None = None
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    birthday: date

    @field_validator("birthday", mode="before")
    def validate_birthday(cls, value):
        if value is None:
            return value
        if isinstance(value, date):
            birthdate = value
        elif isinstance(value, str):
            birthdate = datetime.strptime(value, "%Y-%m-%d").date()
        if birthdate > date.today():
            raise ValueError("Birthday cant be in the future")
        return value


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

    class ConfigDict:
        from_attributes = True
