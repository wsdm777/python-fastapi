from fastapi import FastAPI
from src.auth.authentification import fastapi_users, auth_backend
from src.auth.userrouter import router as userRouter
from src.auth.authrouter import router as authRouter

# from src.post.router import router as postRouter


app = FastAPI(title="TestApp")


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"]
)

app.include_router(userRouter)
app.include_router(authRouter)
