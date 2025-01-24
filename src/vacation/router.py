from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.databasemodels import User, Vacation
from src.user.router import get_current_superuser
from src.database import get_async_session
from src.vacation.schemas import (
    MessageResponse,
    VacationCreate,
    VacationPaginationResponse,
    VacationRead,
)
from src.user.router import get_current_user
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


@router.delete("/delete/{vacation_id}")
async def delete_vacation(
    user: Annotated[User, Depends(get_current_superuser)],
    vacation_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = delete(Vacation).where(Vacation.id == vacation_id)
    result = await session.execute(stmt)
    await session.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Vacation not found")
    return JSONResponse(content={"message": "Vacation deleted"}, status_code=200)


@router.get("/{vacation_id}", response_model=VacationRead)
async def get_vacation_by_id(
    user: Annotated[User, Depends(get_current_superuser)],
    vacation_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(Vacation).where(Vacation.id == vacation_id)
    result = await session.execute(stmt)

    result = result.scalars().one_or_none()

    if result is None:
        raise HTTPException(status_code=404, detail="Vacation not found")

    return VacationRead.model_validate(result)


@router.get("/all/", response_model=VacationPaginationResponse)
async def get_vacations(
    size: int,
    lc: Optional[int] = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(Vacation).order_by(Vacation.id).limit(size)
    if lc:
        stmt = stmt.filter(Vacation.id > lc)

    results = await session.execute(stmt)
    results = results.scalars().all()
    vacations = [VacationRead.model_validate(vacation) for vacation in results]
    last_id = vacations[-1].id if vacations else None

    return VacationPaginationResponse(items=vacations, next_cursor=last_id, size=size)


@router.get("/all/by/{giver_id}", response_model=VacationPaginationResponse)
async def get_vacation_by_id(
    size: int,
    giver_id: int,
    lc: Optional[int] = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        select(Vacation)
        .order_by(Vacation.id)
        .limit(size)
        .filter(Vacation.giver_id == giver_id)
    )
    if lc:
        stmt = stmt.filter(Vacation.id > lc)
    results = await session.execute(stmt)
    results = results.scalars().all()
    vacations = [VacationRead.model_validate(vacation) for vacation in results]
    last_id = vacations[-1].id if vacations else None

    return VacationPaginationResponse(items=vacations, next_cursor=last_id, size=size)


@router.get("/all/to/{receiver_id}", response_model=VacationPaginationResponse)
async def get_vacation_to_id(
    size: int,
    receiver_id: int,
    lc: Optional[int] = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        select(Vacation)
        .order_by(Vacation.id)
        .limit(size)
        .filter(Vacation.receiver_id == receiver_id)
    )
    if lc:
        stmt = stmt.filter(Vacation.id > lc)
    results = await session.execute(stmt)
    results = results.scalars().all()
    vacations = [VacationRead.model_validate(vacation) for vacation in results]
    last_id = vacations[-1].id if vacations else None

    return VacationPaginationResponse(items=vacations, next_cursor=last_id, size=size)
