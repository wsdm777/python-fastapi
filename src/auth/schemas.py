from pydantic import BaseModel, EmailStr


class UserTokenInfo(BaseModel):
    email: EmailStr
    is_superuser: bool
