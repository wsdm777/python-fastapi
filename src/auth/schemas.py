from pydantic import BaseModel, EmailStr


class UserTokenInfo(BaseModel):
    id: int
    email: EmailStr
    is_superuser: bool
