from pydantic import BaseModel


class SectionRead(BaseModel):
    id: int
    name: str
    head_id: int


class SectionCreate(BaseModel):
    name: str
    head_id: int | None
