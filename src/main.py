from fastapi import FastAPI
from src.auth.authentification import fastapi_users, auth_backend
from src.user.router import router as userRouter
from src.auth.router import router as authRouter

app = FastAPI(title="TestApp")

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"]
)

app.include_router(userRouter)
app.include_router(authRouter)
