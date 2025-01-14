import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.auth.authentification import fastapi_users, auth_backend
from src.user.router import router as userRouter
from src.auth.router import router as authRouter
from src.vacations.router import router as vacRouter
from src.positions.router import router as posRouter
from src.section.router import router as secRouter
from src.utils.create_superuser import create_superuser


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Начинаю создание суперпользователя...")
    await create_superuser()
    print("Суперпользователь создан")
    yield


app = FastAPI(title="TestApp", lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"]
)

app.include_router(userRouter)
app.include_router(authRouter)
app.include_router(vacRouter)
app.include_router(posRouter)
app.include_router(secRouter)
