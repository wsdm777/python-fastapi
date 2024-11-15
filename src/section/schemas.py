from typing import Optional
from pydantic import BaseModel


class SectionRead(BaseModel):
    id: int
    name: str
    head_id: int | None


class SectionCreate(BaseModel):
    name: str
    head_id: Optional[int]
