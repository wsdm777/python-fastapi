from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import insert, select, update, delete
from src.auth.JWT import get_current_superuser, get_current_user
from src.position.schemas import (
    MessageResponse,
    PositionCreate,
    PositionPaginationResponse,
    PositionRead,
)
from src.databasemodels import Position, User
from src.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.utils.logger import logger

router = APIRouter(prefix="/position", tags=["position"])


@router.post("/add/", response_model=MessageResponse)
async def create_new_position(
    user: Annotated[User, Depends(get_current_superuser)],
    position: PositionCreate,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        stmt = insert(Position).values(position.model_dump())
        await session.execute(stmt)
        await session.commit()

    except IntegrityError as e:

        error = str(e.orig)

        if "Unique" in error:
            logger.info(
                f"{user.email}: Trying to add an existing position {position.name}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Position already exist"
            )

        if "Foreign" in error:
            logger.info(
                f"{user.email}: Trying to add a position in non-existent section {position.section_name}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The section with name {position.section_name} does not exist ",
            )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    logger.info(
        f"{user.email}: Added new position, name = {position.name}, section = {position.section_name}"
    )

    return JSONResponse(
        content={"Message": "Position created"}, status_code=status.HTTP_201_CREATED
    )


@router.delete("/delete/{position_id}")
async def delete_position(
    user: Annotated[User, Depends(get_current_superuser)],
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
    user: Annotated[User, Depends(get_current_superuser)],
    position_id: int,
    section_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        update(Position).where(Position.id == position_id).values(section_id=section_id)
    )
    result = await session.execute(stmt)
    await session.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="position not found")
    return JSONResponse(content={"message": "position update"}, status_code=200)


@router.get("/{position_id}", response_model=PositionRead)
async def get_position_by_id(
    user: Annotated[User, Depends(get_current_user)],
    position_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(Position).where(Position.id == position_id)
    result = await session.execute(stmt)

    result = result.scalars().one_or_none()

    if result is None:
        raise HTTPException(status_code=404, detail="Position not found")

    return PositionRead.model_validate(result)


@router.get("/all/", response_model=PositionPaginationResponse)
async def get_position(
    size: int,
    lc: Optional[int] = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(Position).order_by(Position.id).limit(size)
    if lc:
        stmt = stmt.filter(Position.id > lc)

    results = await session.execute(stmt)
    results = results.scalars().all()
    positions = [PositionRead.model_validate(position) for position in results]
    last_id = positions[-1].id if positions else None

    return PositionPaginationResponse(items=positions, next_cursor=last_id, size=size)


@router.get("/all/to/{section}", response_model=PositionPaginationResponse)
async def get_position_to_section(
    size: int,
    section_id: int,
    lc: Optional[int] = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        select(Position)
        .order_by(Position.id)
        .limit(size)
        .filter(Position.section_id == section_id)
    )
    if lc:
        stmt = stmt.filter(Position.id > lc)
    results = await session.execute(stmt)
    results = results.scalars().all()
    vacations = [PositionRead.model_validate(vacation) for vacation in results]
    last_id = vacations[-1].id if vacations else None

    return PositionPaginationResponse(items=vacations, next_cursor=last_id, size=size)
