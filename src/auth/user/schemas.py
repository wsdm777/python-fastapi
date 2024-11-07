from datetime import datetime
from typing import Optional
from fastapi_users import schemas
from pydantic import EmailStr


class UserRead(schemas.BaseUser[int]):
    id: int
    name: str
    role_id: int
    email: EmailStr
    is_vacation: bool
    joined_at: datetime
    last_bonus_payment: datetime | None


class UserCreate(schemas.BaseUserCreate):
    id: int
    name: str
    role_id: int
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
