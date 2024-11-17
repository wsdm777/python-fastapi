from datetime import date, datetime
from typing import Optional
from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, field_validator


class UserRead(schemas.BaseUser[int]):
    id: int
    name: str
    surname: str
    position_id: int | None
    email: EmailStr
    joined_at: date
    birthday: date

    last_bonus_payment: date | None

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    id: int
    name: str
    surname: str
    position_id: int
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
        birthdate = datetime.strptime(value, "%Y-%m-%d").date()
        if birthdate > date.today():
            raise ValueError("Birthday cant be in the future")
        return value


class UserOnVacation(BaseModel):
    id: int
    name: str
    surname: str
    position_id: int | None
    email: EmailStr
    end_date: date


class UserPaginationAllVacationResponse(BaseModel):
    items: list[UserOnVacation]
    next_cursor: int | None
    size: int


class UserNotOnVacation(BaseModel):
    id: int
    name: str
    surname: str
    position_id: int | None
    email: EmailStr
    start_date: date | None


class UserPaginationAllNotVacationResponse(BaseModel):
    items: list[UserNotOnVacation]
    next_cursor: int | None
    size: int


class UserPagination(BaseModel):
    id: int
    name: str
    surname: str
    position_id: int | None
    email: EmailStr
    on_vacation: bool


class UserPaginationResponse(BaseModel):
    items: list[UserPagination]
    next_cursor: int | None
    size: int


class UserResponse(BaseModel):
    Message: str


class UserInfo(BaseModel):
    id: int
    name: str
    surname: str
    position_id: int | None
    email: EmailStr
    joined_at: date
    birthday: date
    is_on_vacation: bool
