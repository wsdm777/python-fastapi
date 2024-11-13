from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from httpx import delete
from sqlalchemy import insert, update, values

from src.section.schemas import SectionCreate
from src.databasemodels import Section, User
from src.user.router import current_super_user
from src.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/section", tags=["section"])


@router.post("/add/")
async def create_new_section(
    user: Annotated[User, Depends(current_super_user)],
    data: SectionCreate,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = insert(Section.name, Section.head_id).values(data)
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(content={"message": "section created"}, status_code=201)


@router.delete("/delete/{section_id}")
async def create_new_section(
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
