from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from src.auth.schemas import UserCreate, UserRead
from src.auth.manager import get_user_manager
from src.auth.models import User
from src.auth.authentification import auth_backend



fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
