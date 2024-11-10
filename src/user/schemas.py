from datetime import date, datetime
from typing import Optional
from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, field_validator


class UserRead(schemas.BaseUser[int]):
    id: int
    name: str
    role_id: int
    email: EmailStr
    is_vacation: bool
    joined_at: datetime
    last_bonus_payment: datetime | None

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    id: int
    name: str
    role_id: int
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    birthday: Optional[datetime]

    @field_validator("birthday", mode="before")
    def validate_birthday(cls, value):
        if value is None:
            return value
        birthdate = datetime.strptime(value, "%Y-%m-%d").date()
        if birthdate > date.today():
            raise ValueError("Birthday cant be in the future")
        return birthdate


class PaginationResponse(BaseModel):
    items: list[UserRead]
    next_cursor: int
    size: int
