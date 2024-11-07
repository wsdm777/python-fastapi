from fastapi import APIRouter, Depends
from src.auth.authentification import fastapi_users
from src.auth.user.schemas import UserCreate, UserRead
from src.auth.user.router import current_user


router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(current_user)])

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/jwt",
    tags=["auth"],
)
