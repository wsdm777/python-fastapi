from pydantic import BaseModel, ConfigDict


class MessageResponse(BaseModel):
    Message: str


class PositionRead(BaseModel):
    id: int
    section_name: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class PositionCreate(BaseModel):
    section_id: int
    name: str


class PositionPaginationResponse(BaseModel):
    items: list[PositionRead]
    last_position_name: str | None
    final: bool
    size: int
