from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import select, true, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from src.auth.authentification import fastapi_users
from src.user.models import User
from src.user.schemas import PaginationResponse, UserRead


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


@router.get("/all/", response_model=PaginationResponse)
async def GetUsers(
    size: int, lc: int = None, session: AsyncSession = Depends(get_async_session)
):
    query = (
        select(
            User.id,
            User.name,
            User.role_id,
            User.is_superuser,
            User.email,
            User.is_vacation,
            User.joined_at,
            User.last_bonus_payment,
        )
        .order_by(User.id)
        .limit(size)
    )
    if lc:
        query = query.filter(User.id > lc)
    results = await session.execute(query)
    results = results.all()
    users = [
        UserRead(
            id=row[0],
            name=row[1],
            role_id=row[2],
            is_superuser=row[3],
            email=row[4],
            is_vacation=row[5],
            joined_at=row[6],
            last_bonus_payment=row[7],
        )
        for row in results
    ]
    last_id = users[-1].id if users else None

    return PaginationResponse(items=users, next_cursor=last_id, size=size)
