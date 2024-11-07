from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from src.auth.authentification import fastapi_users
from src.auth.user.models import User
from src.auth.user.schemas import UserRead


router = APIRouter(prefix="/user", tags=["user"])


current_user = fastapi_users.current_user()


current_super_user = fastapi_users.current_user(superuser=True)


@router.get("/me", response_model=UserRead)
def get_me(user: User = Depends(current_user)):
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user: Annotated[User, Depends(current_super_user)],
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    result = result.scalars().one()
    return UserRead.model_validate(result)


@router.patch("/getsuper/{user_id}")
async def getSuperUser(
    user: Annotated[User, Depends(current_super_user)],
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = update(User).where(User.id == user_id).values(is_superuser=True)
    await session.execute(stmt)
    await session.commit()
