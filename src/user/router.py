from datetime import date
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from sqlalchemy import and_, case, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.utils.logger import logger
from src.database import get_async_session
from src.auth.authentification import fastapi_users
from src.databasemodels import Position, Section, User, Vacation
from src.user.schemas import (
    UserInfo,
    UserNotOnVacation,
    UserOnVacation,
    UserPagination,
    UserPaginationAllNotVacationResponse,
    UserPaginationAllVacationResponse,
    UserPaginationResponse,
    UserResponse,
)


router = APIRouter(prefix="/user", tags=["user"])

current_user = fastapi_users.current_user()

current_super_user = fastapi_users.current_user(superuser=True)


@router.get("/{user_email}", response_model=UserInfo)
async def get_user_by_email(
    user: Annotated[User, Depends(current_user)],
    user_email: EmailStr,
    session: AsyncSession = Depends(get_async_session),
):
    query = (
        select(User, Position.name, Section.name)
        .outerjoin(Position, User.position_name == Position.name)
        .outerjoin(Section, Position.section_name == Section.name)
        .options(selectinload(User.receiver_vacations))
        .filter(User.email == user_email)
    )

    result = await session.execute(query)
    result = result.unique().one_or_none()
    if result is None:
        logger.error(f"User {user_email} not found")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Selected info user {user_email}")
    user, position_name, section_name = result
    on_vacation = False
    for vacation in user.receiver_vacations:
        if vacation.start_date <= date.today() <= vacation.end_date:
            on_vacation = True
    return UserInfo(
        id=user.id,
        name=user.name,
        surname=user.surname,
        email=user.email,
        joined_at=user.joined_at,
        birthday=user.birthday,
        position_name=position_name,
        section_name=section_name,
        is_on_vacation=on_vacation,
        is_superuser=user.is_superuser,
    )


@router.patch("/getsuper/{user_email}", response_model=UserResponse)
async def get_superuser(
    user: Annotated[User, Depends(current_super_user)],
    user_email: EmailStr,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = update(User).filter(User.email == user_email).values(is_superuser=True)
    result = await session.execute(stmt)
    await session.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(content={"Message": "User upgrade"}, status_code=200)


@router.delete("/fire/{user_id}", response_model=UserResponse)
async def fire_user(
    user: Annotated[User, Depends(current_super_user)],
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = delete(User).where(User.id == user_id)
    result = await session.execute(stmt)
    await session.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return JSONResponse(content={"Message": "User deleted"}, status_code=200)


@router.get("/all/", response_model=UserPaginationResponse)
async def get_users(
    size: int,
    lc: Optional[int] = None,
    position_id: Optional[int] = None,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        select(
            User,
            func.bool_or(
                case(
                    (
                        and_(
                            Vacation.start_date <= date.today(),
                            Vacation.end_date >= date.today(),
                        ),
                        True,
                    ),
                    else_=False,
                )
            ).label("is_on_vacation"),
        )
        .outerjoin(Vacation, User.id == Vacation.receiver_id)
        .limit(size)
        .group_by(User)
        .order_by(User.id)
    )
    if lc:
        stmt = stmt.filter(User.id > lc)
    if position_id:
        stmt = stmt.filter(User.position_id == position_id)
    results = await session.execute(stmt)
    results = results.all()
    users = [
        UserPagination(
            id=user.id,
            name=user.name,
            surname=user.surname,
            position_id=user.position_id,
            email=user.email,
            on_vacation=vacation,
        )
        for user, vacation in results
    ]
    last_id = users[-1].id if users else None
    return UserPaginationResponse(items=users, next_cursor=last_id, size=size)


@router.get("/all/not_on_vacation", response_model=UserPaginationAllNotVacationResponse)
async def get_all_not_vacation(
    size: int,
    lc: Optional[int] = None,
    position_id: Optional[int] = None,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    active_users_id = (
        select(User.id)
        .join(Vacation, User.id == Vacation.receiver_id)
        .filter(
            and_(
                Vacation.end_date > date.today(),
                Vacation.start_date < date.today(),
            )
        )
        .order_by(User.id)
        .limit(size)
    )
    if lc:
        active_users_id = active_users_id.filter(User.id > lc)
    stmt = (
        select(User, Vacation.start_date)
        .outerjoin(Vacation, User.id == Vacation.receiver_id)
        .filter(User.id.notin_(active_users_id))
        .limit(size)
        .order_by(User.id)
    )
    if lc:
        stmt = stmt.filter(User.id > lc)
    if position_id:
        stmt = stmt.filter(User.position_id == position_id)
    results = await session.execute(stmt)
    results = results.all()
    users = [
        UserNotOnVacation(
            id=user.id,
            name=user.name,
            surname=user.surname,
            position_id=user.position_id,
            email=user.email,
            start_date=start_date,
        )
        for user, start_date in results
    ]
    last_id = users[-1].id if users else None
    return UserPaginationAllNotVacationResponse(
        items=users, next_cursor=last_id, size=size
    )


@router.get("/all/on_vacation", response_model=UserPaginationAllVacationResponse)
async def get_all_vacation(
    size: int,
    lc: Optional[int] = None,
    position_id: Optional[int] = None,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        select(User, Vacation.end_date)
        .join(Vacation, User.id == Vacation.receiver_id)
        .filter(
            and_(
                Vacation.end_date > date.today(),
                Vacation.start_date < date.today(),
            )
        )
        .limit(size)
        .order_by(User.id)
    )
    if lc:
        stmt = stmt.filter(User.id > lc)
    if position_id:
        stmt = stmt.filter(User.position_id == position_id)
    results = await session.execute(stmt)
    results = results.all()
    users = [
        UserOnVacation(
            id=user.id,
            name=user.name,
            surname=user.surname,
            position_id=user.position_id,
            email=user.email,
            end_date=end_date,
        )
        for user, end_date in results
    ]
    last_id = users[-1].id if users else None
    return UserPaginationAllVacationResponse(
        items=users, next_cursor=last_id, size=size
    )


@router.patch("/pos/{user_id}/{position_id}", response_model=UserResponse)
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
        raise HTTPException(status_code=404, detail="User not found")

    return JSONResponse(content={"Message": "User update"}, status_code=200)
