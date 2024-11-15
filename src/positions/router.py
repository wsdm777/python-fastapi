from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from httpx import delete
from sqlalchemy import insert, update, values

from src.positions.schemas import PositionCreate
from src.section.schemas import SectionCreate
from src.databasemodels import Position, Section, User
from src.user.router import current_super_user
from src.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/position", tags=["position"])


@router.post("/add/")
async def create_new_position(
    user: Annotated[User, Depends(current_super_user)],
    data: PositionCreate,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = insert(Position).values(data.model_dump())
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(content={"message": "position created"}, status_code=201)


@router.delete("/delete/{position_id}")
async def create_new_position(
    user: Annotated[User, Depends(current_super_user)],
    position_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = delete(Position).where(Position.id == position_id)
    result = await session.execute(stmt)
    await session.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Postion not found")
    return JSONResponse(content={"message": "position deleted"}, status_code=200)


@router.patch("/update/{position_id}")
async def update_position(
    user: Annotated[User, Depends(current_super_user)],
    position_id: int,
    section_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = update(Position).where(Position.id == position_id).values(id=section_id)
    result = await session.execute(stmt)
    await session.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="position not found")
    return JSONResponse(content={"message": "position update"}, status_code=200)
