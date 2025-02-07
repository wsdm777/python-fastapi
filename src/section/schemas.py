from pydantic import BaseModel, ConfigDict, EmailStr


class MessageResponse(BaseModel):
    Message: str


class SectionRead(BaseModel):
    id: int
    name: str
    head_email: EmailStr | None

    model_config = ConfigDict(from_attributes=True)


class SectionCreate(BaseModel):
    name: str
    head_id: int = None


class SectionPaginationResponse(BaseModel):
    items: list[SectionRead]
    last_section_name: str | None
    final: bool
    size: int

    model_config = ConfigDict(from_attributes=True)
