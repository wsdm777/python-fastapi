from pydantic import BaseModel


class PositionRead(BaseModel):
    id: int
    section_id: int
    name: str

    class Config:
        from_attributes = True


class PositionCreate(BaseModel):
    section_id: int
    name: str


class PositionPaginationResponse(BaseModel):
    items: list[PositionRead]
    next_cursor: int | None
    size: int
