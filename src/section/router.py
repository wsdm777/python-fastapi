from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import delete, insert, select, update

from src.section.schemas import SectionCreate, SectionRead
from src.databasemodels import Section, User
from src.user.router import current_super_user, current_user
from src.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/section", tags=["section"])


@router.post("/add/")
async def create_new_section(
    user: Annotated[User, Depends(current_super_user)],
    data: SectionCreate,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = insert(Section).values(data.model_dump())
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(content={"message": "section created"}, status_code=201)


@router.delete("/delete/{section_id}")
async def delete_section(
    user: Annotated[User, Depends(current_super_user)],
    section_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = delete(Section).where(Section.id == section_id)
    result = await session.execute(stmt)
    await session.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Section not found")
    return JSONResponse(content={"message": "section deleted"}, status_code=200)


@router.patch("/update/{section_id}")
async def update_section(
    user: Annotated[User, Depends(current_super_user)],
    section_id: int,
    head_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = update(Section).where(Section.id == section_id).values(head_id=head_id)
    result = await session.execute(stmt)
    await session.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="section not found")
    return JSONResponse(content={"message": "section update"}, status_code=200)


@router.get("/{section_id}", response_model=SectionRead)
async def get_section_by_id(
    user: Annotated[User, Depends(current_user)],
    section_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(Section).where(Section.id == section_id)
    result = await session.execute(stmt)

    result = result.scalars().one_or_none()

    if result is None:
        raise HTTPException(status_code=404, detail="Section not found")

    return SectionRead.model_validate(result)


@router.get("/all/", response_model=list[SectionRead])
async def get_section(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(Section).order_by(Section.id)

    results = await session.execute(stmt)
    results = results.scalars().all()
    sections = [SectionRead.model_validate(section) for section in results]

    return sections
