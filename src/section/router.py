from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from sqlalchemy import delete, insert, select, update

from src.section.schemas import SectionCreate, SectionRead
from src.databasemodels import Section, User
from src.user.router import current_super_user, current_user
from src.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.utils.logger import logger

router = APIRouter(prefix="/section", tags=["section"])


@router.post("/add/")
async def create_new_section(
    user: Annotated[User, Depends(current_super_user)],
    section: SectionCreate,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        stmt = insert(Section).values(section.model_dump())

        await session.execute(stmt)
        await session.commit()

    except IntegrityError as e:

        error = str(e.orig)

        if "Unique" in error:
            logger.info(
                f"{user.email}: Trying to add an existing section {section.name}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Section already exist"
            )

        if "Foreign" in error:
            logger.info(
                f"{user.email}: Trying to add a section with a non-existent head {section.head_email}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The user with email {section.head_email} does not exist ",
            )

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    logger.info(
        f"{user.email}: Added new section name = {section.name}, head = {section.head_email}"
    )

    return JSONResponse(
        content={"Message": f"Section {section.name} created"},
        status_code=status.HTTP_201_CREATED,
    )


@router.delete("/delete/{section_name}")
async def delete_section(
    user: Annotated[User, Depends(current_super_user)],
    section_name: str,
    session: AsyncSession = Depends(get_async_session),
):

    stmt = delete(Section).where(Section.name == section_name)
    result = await session.execute(stmt)
    await session.commit()

    if result.rowcount == 0:
        logger.info(
            f"{user.email}: Trying to delete a non-existent section {section_name}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section {section_name} not found",
        )

    logger.info(f"{user.email}: Section {section_name} deleted")
    return JSONResponse(content={"Message": "Section deleted"}, status_code=200)


@router.patch("/update/{section_name}")
async def update_section(
    user: Annotated[User, Depends(current_super_user)],
    section: SectionCreate,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        stmt = (
            update(Section)
            .where(Section.name == section.name)
            .values(head_email=section.head_email)
        )
        result = await session.execute(stmt)
        await session.commit()

    except IntegrityError as e:

        error = str(e.orig)

        if "Foreign" in error:

            logger.info(
                f"{user.email}: Trying to change head of section {section.name} to non-existent user {section.head_email}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The user with email {section.head_email} does not exist ",
            )

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if result.rowcount == 0:
        logger.info(
            f"{user.email}: Trying to update non-existent section {section.name}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section {section.name} not found",
        )

    logger.info(
        f"{user.email}: Change section {section.name} head to {section.head_email}"
    )
    return JSONResponse(
        content={"Message": "Section update"}, status_code=status.HTTP_200_OK
    )


@router.get("/{section_name}", response_model=SectionRead)
async def get_section_by_id(
    user: Annotated[User, Depends(current_user)],
    section_name: str,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(Section).where(Section.name == section_name)
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
    stmt = select(Section).order_by(Section.name)

    results = await session.execute(stmt)
    results = results.scalars().all()
    sections = [SectionRead.model_validate(section) for section in results]

    return sections
