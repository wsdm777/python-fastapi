from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.services.redis import get_current_superuser, get_current_user
from src.position.schemas import (
    MessageResponse,
    PositionCreate,
    PositionPaginationResponse,
    PositionRead,
)
from src.databasemodels import Position, Section, User
from src.database import get_async_session
from src.utils.logger import logger

router = APIRouter(prefix="/position", tags=["position"])


@router.post("/create", response_model=MessageResponse)
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
            logger.warning(
                f"{user.email}: Trying to create an existing position {position.name}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Position already exist"
            )

        if "Foreign" in error:
            logger.warning(
                f"{user.email}: Trying to create a position in non-existent section id {position.section_id}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The section with id {position.section_id} does not exist ",
            )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    logger.info(
        f"{user.email}: Created new position, name = {position.name}, section = {position.section_id}"
    )

    return JSONResponse(
        content={"message": "Position created"}, status_code=status.HTTP_201_CREATED
    )


@router.delete("/{position_name}/remove", response_model=MessageResponse)
async def delete_position(
    user: Annotated[User, Depends(get_current_superuser)],
    position_name: str,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = delete(Position).filter(Position.name == position_name)
    result = await session.execute(stmt)
    await session.commit()

    if result.rowcount == 0:
        logger.warning(
            f"{user.email}: Trying to delete non-existent position {position_name}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Position not found"
        )

    logger.info(f"{user.email}: Deleted position {position_name}")
    return JSONResponse(
        content={"Message": "Position deleted"}, status_code=status.HTTP_200_OK
    )


@router.patch("/{position_name}/{section_id}")
async def update_position(
    user: Annotated[User, Depends(get_current_superuser)],
    position_name: str,
    section_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        stmt = (
            update(Position)
            .filter(Position.name == position_name)
            .values(section_id=section_id)
        )
        result = await session.execute(stmt)
        await session.commit()

    except IntegrityError as e:

        error = str(e.orig)

        if "Foreign" in error:

            logger.warning(
                f"{user.email}: Trying to change position section id to non-existent {section_id}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The section {section_id} does not exist ",
            )

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if result.rowcount == 0:
        logger.warning(
            f"{user.email}: Trying to update non-existent position {position_name}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Position not found"
        )

    logger.info(
        f"{user.email}: Update position {position_name}, new section = {section_id}"
    )
    return JSONResponse(
        content={"message": "position update"}, status_code=status.HTTP_200_OK
    )


@router.get("/{position_name}", response_model=PositionRead)
async def get_position_by_name(
    user: Annotated[User, Depends(get_current_user)],
    position_name: str,
    session: AsyncSession = Depends(get_async_session),
):
    query = (
        select(Position)
        .options(joinedload(Position.section).load_only(Section.name))
        .filter(Position.name == position_name)
    )
    position = await session.execute(query)

    position = position.scalars().one_or_none()

    if position is None:
        logger.warning(
            f"{user.email}: Trying to select a non-existent position {position_name}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Position not found"
        )

    logger.info(f"{user.email}: Select info of position {position_name}")

    return PositionRead(
        id=position.id, section_name=position.section.name, name=position_name
    )


@router.get("/list/", response_model=PositionPaginationResponse)
async def get_positions(
    desc: bool = Query(False, description="Тип сортировки"),
    filter_name: Optional[str] = Query(None, description="Должность"),
    page_size: int = Query(10, ge=1, le=100, description="Размер страницы"),
    last_position_name: Optional[str] = Query(
        None, description="Последняя должность на предыдущей странице"
    ),
    section: Optional[int] = Query(None, description="Отдел"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    log = f"{user.email}: Selected positions with params pg_size = {page_size}, desc = {desc}"

    query = select(Position).options(
        joinedload(Position.section).load_only(Section.name)
    )

    query = (
        query.order_by(Position.name.desc()) if desc else query.order_by(Position.name)
    )

    if section:
        log += f", section = {section}"
        query = query.filter(Position.section_id == section)

    if last_position_name:
        log += f", last_name = {last_position_name}"

        cursor_filter = (
            (Position.name < last_position_name)
            if desc
            else (Position.name > last_position_name)
        )
        query = query.filter(cursor_filter)

    if filter_name:
        log += f", filter name = {filter_name}"
        query = query.filter(Position.name.ilike(f"{filter_name}%"))

    query = query.limit(page_size + 1)

    results = await session.execute(query)
    results = results.scalars().all()
    positions = [
        PositionRead(
            id=position.id, section_name=position.section.name, name=position.name
        )
        for position in results
    ]

    is_final = False if len(results) > page_size else True

    now_last_name = None if is_final else positions[-2].name

    logger.info(log)

    return PositionPaginationResponse(
        items=positions[:page_size],
        last_position_name=now_last_name,
        final=is_final,
        size=page_size,
    )
