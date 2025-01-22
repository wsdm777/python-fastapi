from pydantic import BaseModel, EmailStr


class MessageResponse(BaseModel):
    Message: str


class SectionRead(BaseModel):
    id: int
    name: str
    head_email: EmailStr | None

    class Config:
        from_attributes = True


class SectionCreate(BaseModel):
    name: str
    head_email: EmailStr = None


class SectionPaginationResponse(BaseModel):
    items: list[SectionRead]
    last_section_name: str | None
    final: bool
    size: int

    class ConfigDict:
        from_attributes = True
