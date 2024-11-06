from fastapi import APIRouter, Depends
from src.auth.authentification import fastapi_users
from fastapi.security import HTTPBasic
from src.auth.schemas import UserCreate, UserRead

security = HTTPBasic()
router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(security)])

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/jwt",
    tags=["auth"],
)
