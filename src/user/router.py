from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from src.auth.authentification import fastapi_users
from src.databasemodels import User
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

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    result = result.scalars().one()
    return UserRead.model_validate(result)


@router.patch("/getsuper/{user_id}")
async def getSuperUser(
    user: Annotated[User, Depends(current_super_user)],
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = update(User).where(User.id == user_id).values(is_superuser=True)
    result = await session.execute(stmt)
    await session.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")


@router.delete("/fire/{user_id}")
async def fireUser(
    user: Annotated[User, Depends(current_super_user)],
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = delete(User).where(User.id == user_id)
    result = await session.execute(stmt)
    await session.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/all/", response_model=PaginationResponse)
async def GetUsers(
    size: int, lc: int = None, session: AsyncSession = Depends(get_async_session)
):
    query = select(User).order_by(User.id).limit(size)
    if lc:
        query = query.filter(User.id > lc)
    results = await session.execute(query)
    results = results.all()
    users = [UserRead.model_validate(user) for user in users]
    last_id = users[-1].id if users else None
    return PaginationResponse(items=users, next_cursor=last_id, size=size)


@router.patch("/pos/{user_id}/{position_id}")
async def update_position(
    user: Annotated[User, Depends(current_super_user)],
    user_id: int,
    position_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = update(User).where(User.id == user_id).values(position_id=position_id)
    result = await session.execute(stmt)
    await session.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="user not found")
    return JSONResponse(content={"message": "user update"}, status_code=200)
