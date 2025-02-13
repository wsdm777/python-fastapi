from typing import Annotated
import bcrypt
from fastapi import APIRouter, Depends
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from datetime import datetime, timedelta, timezone
from fastapi.responses import JSONResponse
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.schemas import LoginRequest, UserCreate, UserSessionInfo
from src.databasemodels import User
from src.database import get_async_session
from src.utils.logger import logger
from src.services.redis import (
    create_session,
    get_current_superuser,
    get_current_user,
    remove_session,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(user_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        user_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


@router.post("/login")
async def login(
    credentials: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
):
    query = select(User).filter(User.email == credentials.email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning(
            f"Login failed for {credentials.email}: Invalid email or password"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials"
        )
    session_value = await create_session(user.id, user.email, user.is_superuser)

    response.set_cookie(
        "authcook",
        value=session_value,
        httponly=True,
    )

    logger.info(f"User {user.email} login")
    return {"message": "Login successful"}


@router.post("/register")
async def register(
    user: Annotated[UserSessionInfo, Depends(get_current_superuser)],
    user_data: UserCreate,
    session: AsyncSession = Depends(get_async_session),
):
    hashed_password = hash_password(password=user_data.password)
    user_create = {
        "name": user_data.name,
        "surname": user_data.surname,
        "position_id": user_data.position_id,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "is_superuser": user_data.is_superuser,
        "birthday": user_data.birthday,
    }
    stmt = insert(User).values(user_create)
    await session.execute(stmt)
    await session.commit()
    logger.info(f"{user.email}: Register user {user_data.email}")
    return JSONResponse(
        content={"message": f"User {user_data.email} created"},
        status_code=status.HTTP_201_CREATED,
    )


@router.post("/logout")
async def logout(response: Response, request: Request):
    cookies = request.cookies

    if "authcook" not in cookies:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    expired_date = datetime.now(timezone.utc) - timedelta(days=1)

    await remove_session(cookies.get("authcook"))

    response.set_cookie(
        "authcook",
        expires=expired_date,
        httponly=True,
        secure=False,
        samesite="Lax",
    )

    return {"message": "Successfully logged out"}
