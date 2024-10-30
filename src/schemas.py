from pydantic import BaseModel


class goodResponse(BaseModel):
    status: int = 201