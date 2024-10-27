from fastapi import FastAPI
from src.auth.authentification import fastapi_users, auth_backend
from src.auth.schemas import UserCreate, UserRead

app = FastAPI(title="TestApp")


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth/jwt",
    tags=["auth"]
)