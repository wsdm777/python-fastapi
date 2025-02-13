from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserSessionInfo(BaseModel):
    id: int
    email: EmailStr
    is_superuser: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4)


class UserCreate(BaseModel):
    name: str
    surname: str
    position_id: int | None = None
    email: EmailStr
    password: str = Field(min_length=4)
    is_superuser: Optional[bool] = False
    birthday: date
    model_config = ConfigDict(from_attributes=True)

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
