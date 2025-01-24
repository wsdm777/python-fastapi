from pydantic import BaseModel


class MessageResponse(BaseModel):
    Message: str


class PositionRead(BaseModel):
    id: int
    section_name: str
    name: str

    class Config:
        from_attributes = True


class PositionCreate(BaseModel):
    section_name: str
    name: str


class PositionPaginationResponse(BaseModel):
    items: list[PositionRead]
    last_position_name: str | None
    final: bool
    size: int
