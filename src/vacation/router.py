from datetime import date
from typing import Annotated, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from sqlalchemy import and_, insert, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.databasemodels import User, Vacation
from src.user.router import get_current_superuser, get_current_user
from src.database import get_async_session
from src.vacation.schemas import (
    MessageResponse,
    VacationCreate,
    VacationPaginationResponse,
    VacationRead,
)
from src.utils.logger import logger

router = APIRouter(prefix="/vacation", tags=["vacation"])


@router.post("/add/", response_model=MessageResponse)
async def create_new_vacation(
    user: Annotated[User, Depends(get_current_superuser)],
    vacation: VacationCreate,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        values = {**vacation.model_dump(), "giver_email": user.email}
        stmt = insert(Vacation).values(values)
        await session.execute(stmt)
        await session.commit()

    except IntegrityError as e:

        error = str(e.orig)

        if "Foreign" in error:
            logger.info(
                f"{user.email}: Trying to add a vacation to a non-existent user {vacation.receiver_email}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The user with email {vacation.receiver_email} does not exist ",
            )

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    logger.info(
        f"{user.email}: Create vacation, giver = {vacation.receiver_email}, start = {vacation.start_date}, end = {vacation.end_date}"
    )

    return JSONResponse(
        content={"message": "Vacation created"}, status_code=status.HTTP_201_CREATED
    )


@router.get("/{vacation_id}", response_model=VacationRead)
async def get_vacation_by_id(
    user: Annotated[User, Depends(get_current_user)],
    vacation_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(Vacation).filter(Vacation.id == vacation_id)
    result = await session.execute(stmt)

    result = result.scalars().one_or_none()

    if result is None:
        logger.info(
            f"{user.email}: Trying to select a non-existent vacation {vacation_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vacation not found"
        )

    logger.info(f"{user.email}: Select info of vacation {vacation_id}")
    return VacationRead.model_validate(result)


@router.get("/list/", response_model=VacationPaginationResponse)
async def get_vacations(
    desc: bool = Query(False, description="Тип сортировки"),
    page_size: int = Query(10, ge=1, le=100, description="Размер страницы"),
    last_vacation_id: Optional[int] = Query(
        None, description="Последняя запись на предыдущей странице"
    ),
    status: Optional[Literal["active", "future", "past"]] = Query(
        None,
        description="Фильтр по статусу отпуска: active (активные), future (будущие), past (прошедшие)",
    ),
    receiver_email: Optional[EmailStr] = Query(None),
    giver_email: Optional[EmailStr] = Query(None),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    log = f"{user.email}: Selected vacations with params pg_size = {page_size}, desc = {desc}"

    query = select(Vacation)

    query = query.order_by(Vacation.id.desc()) if desc else query.order_by(Vacation.id)

    if last_vacation_id:
        log += f", last_id = {last_vacation_id}"

        cursor_filter = (
            (Vacation.id < last_vacation_id)
            if desc
            else (Vacation.id > last_vacation_id)
        )
        query = query.filter(cursor_filter)

    if receiver_email is not None:
        log += f", receiver_email = {receiver_email}"
        query = query.filter(Vacation.receiver_email == receiver_email)

    if giver_email is not None:
        log += f", giver_email = {giver_email}"
        query = query.filter(Vacation.giver_email == giver_email)

    if status is not None:
        log += f", status = {status}"
        today = date.today()

        if status == "active":
            query = query.filter(
                and_(Vacation.start_date <= today, Vacation.end_date >= today)
            )
        elif status == "future":
            query = query.filter(Vacation.start_date > today)
        elif status == "past":
            query = query.filter(Vacation.end_date < today)

    query = query.limit(page_size + 1)

    results = await session.execute(query)
    results = results.scalars().all()
    vacations = [VacationRead.model_validate(vacation) for vacation in results]

    logger.info(log)

    is_final = False if len(results) > page_size else True

    now_last_id = None if is_final else vacations[-2].id

    return VacationPaginationResponse(
        items=vacations[:page_size], last_id=now_last_id, final=is_final, size=page_size
    )
