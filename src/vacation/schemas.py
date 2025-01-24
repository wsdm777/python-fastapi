from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, model_validator


class MessageResponse(BaseModel):
    Message: str


class VacationRead(BaseModel):
    id: int
    giver_email: EmailStr
    receiver_email: EmailStr
    start_date: date
    end_date: date
    description: str | None

    class Config:
        from_attributes = True


class VacationCreate(BaseModel):
    receiver_email: EmailStr
    start_date: date
    end_date: date
    description: Optional[str]

    @model_validator(mode="before")
    def check_date(cls, values):
        start_date = values.get("start_date")
        end_date = values.get("end_date")

        if start_date > end_date:
            raise ValueError("the start date must be earlier than the end date")

        return values


class VacationPaginationResponse(BaseModel):
    items: list[VacationRead]
    next_cursor: int | None
    size: int
