from datetime import date
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from sqlalchemy import and_, case, delete, exists, func, select, tuple_, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from src.auth.router import hash_password
from src.auth.schemas import UserSessionInfo
from src.utils.logger import logger
from src.database import get_async_session
from src.databasemodels import Position, Section, User, Vacation
from src.user.schemas import (
    MessageResponse,
    UserInfo,
    UserPagination,
    UserPaginationResponse,
    UserPassChange,
)
from src.services.redis import (
    get_current_superuser,
    get_current_user,
    remove_all_user_session,
)

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/{user_email}", response_model=UserInfo)
async def get_user_by_email(
    user: Annotated[UserSessionInfo, Depends(get_current_user)],
    user_email: EmailStr,
    session: AsyncSession = Depends(get_async_session),
):
    query = (
        select(User, Position.name, Section.name)
        .outerjoin(Position, User.position_id == Position.id)
        .outerjoin(Section, Position.section_id == Section.id)
        .options(selectinload(User.receiven_vacations))
        .filter(User.email == user_email)
    )

    result = await session.execute(query)
    result = result.unique().one_or_none()
    if result is None:
        logger.warning(f"{user.email}: User {user_email} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    logger.info(f"{user.email}: Selected info of user {user_email}")
    user, position_name, section_name = result
    on_vacation = False
    for vacation in user.receiven_vacations:
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


@router.patch("/grand-admin/{user_email}", response_model=MessageResponse)
async def update_user_access(
    user: Annotated[UserSessionInfo, Depends(get_current_superuser)],
    user_email: EmailStr,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        update(User)
        .filter(User.email == user_email)
        .values(is_superuser=True)
        .returning(User.id)
    )
    result = await session.execute(stmt)
    await session.commit()

    user_id = result.scalar()

    if user_id is None:
        logger.warning(f"{user.email}: User {user_email} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await remove_all_user_session(user_id)
    logger.info(f"{user.email}: User {user_email} upgrade")
    return JSONResponse(
        content={"message": f"User {user_email} upgrade"},
        status_code=status.HTTP_200_OK,
    )


@router.delete("/{user_email}", response_model=MessageResponse)
async def delete_user(
    user: Annotated[UserSessionInfo, Depends(get_current_superuser)],
    user_email: EmailStr,
    session: AsyncSession = Depends(get_async_session),
):
    if user.email == user_email:
        logger.warning(f"{user.email}: Attempted self-deleting")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"You cannot delete yourself"
        )

    stmt = delete(User).filter(User.email == user_email).returning(User.id)
    result = await session.execute(stmt)
    await session.commit()

    user_id = result.scalar()

    if user_id is None:
        logger.warning(
            f"{user.email}: Trying to delete a non-existent user {user_email}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_email} not found"
        )

    await remove_all_user_session(user_id)
    logger.info(f"{user.email}: User {user_email} deleted")
    return JSONResponse(
        content={"message": f"User {user_email} deleted"},
        status_code=status.HTTP_200_OK,
    )


@router.get("/list/", response_model=UserPaginationResponse)
async def get_users(
    desc: bool = Query(False, description="Тип сортировки"),
    filter_surname: Optional[str] = Query(None, description="Фамилия"),
    page_size: int = Query(10, ge=1, le=100, description="Размер страницы"),
    last_name: Optional[str] = Query(
        None, description="Имя последнего пользователя на предыдущей странице"
    ),
    last_surname: Optional[str] = Query(
        None, description="Фамилия последнего пользователя на предыдущей странице"
    ),
    on_vacation_only: Optional[bool] = Query(
        None, description="Фильтр пользователей в отпуске (True/False)"
    ),
    user: UserSessionInfo = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    log = (
        f"{user.email}: Selected users with params pg_size = {page_size}, desc = {desc}"
    )

    query = (
        select(
            User.id,
            User.name,
            User.surname,
            User.is_superuser,
            User.email,
            Position.name,
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
        .outerjoin(Position, User.position_id == Position.id)
        .group_by(User, Position.name)
    )

    query = (
        query.order_by(User.surname.desc(), User.name.desc())
        if desc
        else query.order_by(User.surname, User.name)
    )

    if last_surname and last_name:
        log += f", last_surname = {last_surname}, last_name = {last_name}"

        cursor_filter = (
            tuple_(User.surname, User.name) < tuple_(last_surname, last_name)
            if desc
            else tuple_(User.surname, User.name) > tuple_(last_surname, last_name)
        )
        query = query.filter(cursor_filter)

    if filter_surname:
        log += f", filter surname = {filter_surname}"

        query = query.filter(User.surname.ilike(f"{filter_surname}%"))

    if on_vacation_only is not None:
        aliasVac = aliased(Vacation)
        vacation_filter = exists().where(
            and_(
                aliasVac.start_date <= date.today(),
                aliasVac.end_date >= date.today(),
                aliasVac.receiver_id == User.id,
            )
        )
        query = query.filter(vacation_filter if on_vacation_only else ~vacation_filter)

    query = query.limit(page_size + 1)

    results = await session.execute(query)
    results = results.all()
    users = [
        UserPagination(
            id=user_id,
            name=user_name,
            surname=user_surname,
            is_admin=user_is_admin,
            position_name=position_name,
            email=user_email,
            on_vacation=is_on_vacation,
        )
        for user_id, user_name, user_surname, user_is_admin, user_email, position_name, is_on_vacation in results
    ]

    is_final = False if len(results) > page_size else True

    now_last_name = None if is_final else users[-2].name
    now_last_surname = None if is_final else users[-2].surname

    logger.info(log)

    return UserPaginationResponse(
        items=users[:page_size],
        next_cursor={"last_surname": now_last_surname, "last_name": now_last_name},
        final=is_final,
        size=page_size,
    )


@router.patch("/{user_email}/position/{position_id}", response_model=MessageResponse)
async def update_user_position(
    user: Annotated[UserSessionInfo, Depends(get_current_superuser)],
    user_email: EmailStr,
    position_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        stmt = (
            update(User)
            .filter(User.email == user_email)
            .values(position_id=position_id)
        )
        result = await session.execute(stmt)
        await session.commit()
    except IntegrityError as e:

        error = str(e.orig)

        if "Foreign" in error:
            logger.info(
                f"{user.email}: Trying to give user {user.email} a non-existent position with id = {position_id}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The position with id {position_id} does not exist ",
            )

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if result.rowcount == 0:
        logger.info(f"{user.email}: Trying to update non-existent user {user_email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    logger.info(f"{user.email}: Update {user_email}")
    return JSONResponse(
        content={"message": "User update"}, status_code=status.HTTP_200_OK
    )


@router.patch("/change-password", response_model=MessageResponse)
async def change_password(
    user: Annotated[UserSessionInfo, Depends(get_current_user)],
    data: UserPassChange,
    session: AsyncSession = Depends(get_async_session),
):
    hash_pass = hash_password(data.new_password)
    stmt = (
        update(User).values(hashed_password=hash_pass).filter(User.email == user.email)
    )
    await session.execute(stmt)
    await session.commit()

    await remove_all_user_session(user.id)
    return JSONResponse(
        content={"message": "Password update"}, status_code=status.HTTP_200_OK
    )
