from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.user.router import router as userRouter
from src.auth.router import router as regRouter
from src.vacation.router import router as vacRouter
from src.position.router import router as posRouter
from src.section.router import router as secRouter
from src.utils.create_superuser import create_superuser
from src.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App is starting")
    await create_superuser()
    yield
    logger.info("App is shutting down")


app = FastAPI(title="TestApp", lifespan=lifespan)


app.include_router(regRouter)
app.include_router(userRouter)
app.include_router(vacRouter)
app.include_router(posRouter)
app.include_router(secRouter)
