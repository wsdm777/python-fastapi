from typing import Annotated
from fastapi import APIRouter, Depends
from src.database import get_user_id
from src.auth.authentification import fastapi_users
from src.auth.models import User
from src.auth.schemas import UserRead


router = APIRouter(
    prefix="/user",
    tags=["user"])

current_user = fastapi_users.current_user()

current_super_user = fastapi_users.current_user(superuser = True)

@router.get("/me", response_model=UserRead)
def get_me(user: User = Depends(current_user)):
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user: Annotated[
        User,
        Depends(current_super_user)],
        userdata = Depends(get_user_id)
    ):
    return UserRead.model_validate(userdata)