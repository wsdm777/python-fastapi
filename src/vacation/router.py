from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.databasemodels import User, Vacation
from src.user.router import current_super_user
from src.database import get_async_session
from src.vacation.schemas import (
    VacationCreate,
    VacationPaginationResponse,
    VacationRead,
)
from src.user.router import current_user

router = APIRouter(prefix="/vacation", tags=["vacation"])


@router.post("/add/")
async def create_new_vacation(
    user: Annotated[User, Depends(current_super_user)],
    data: VacationCreate,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = insert(Vacation).values(data.model_dump())
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(content={"message": "vacation created"}, status_code=201)


@router.delete("/delete/{vacation_id}")
async def delete_vacation(
    user: Annotated[User, Depends(current_super_user)],
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
    user: Annotated[User, Depends(current_super_user)],
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
    user: User = Depends(current_user),
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
    user: User = Depends(current_user),
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
    user: User = Depends(current_user),
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
