from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from httpx import delete
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.databasemodels import User, Vacation
from src.user.router import current_super_user
from src.database import get_async_session
from src.vacations.schemas import VacationCreate

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
async def create_new_vacation(
    user: Annotated[User, Depends(current_super_user)],
    vacation_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = delete(Vacation).where(Vacation.id == vacation_id)
    result = await session.execute(stmt)
    await session.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Vacation not found")
    return JSONResponse(content={"message": "vacation deleted"}, status_code=200)
