from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator


class VacationRead(BaseModel):
    id: int
    giver_id: int
    receiver_id: int
    start_date: datetime
    end_date: datetime
    desciption: str | None


class VacationCreate(BaseModel):
    id: int
    giver_id: int
    receiver_id: int
    start_date: datetime
    end_date: datetime
    desciption: str | None

    @model_validator(mode="before")
    def check_date(cls, values):
        start_date = values.get("start_date")
        end_date = values.get("end_date")

        if start_date > end_date:
            raise ValueError("the start date must be earlier than the end date")

        return values
