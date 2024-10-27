from typing import Optional
from fastapi_users import schemas
from pydantic import EmailStr


class UserRead(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    name: str
    role_id: int
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    name: str
    role_id: int