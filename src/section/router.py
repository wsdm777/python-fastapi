from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import delete, insert, select, update
from src.auth.JWT import get_current_superuser, get_current_user
from src.auth.schemas import UserTokenInfo
from src.section.schemas import (
    MessageResponse,
    SectionCreate,
    SectionPaginationResponse,
    SectionRead,
)
from src.databasemodels import Section, User
from src.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.utils.logger import logger

router = APIRouter(prefix="/section", tags=["section"])


@router.post("/add/", response_model=MessageResponse)
async def create_new_section(
    user: Annotated[UserTokenInfo, Depends(get_current_superuser)],
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
        f"{user.email}: Added new section, name = {section.name}, head = {section.head_email}"
    )

    return JSONResponse(
        content={"message": f"Section {section.name} created"},
        status_code=status.HTTP_201_CREATED,
    )


@router.delete("/delete/{section_name}", response_model=MessageResponse)
async def delete_section(
    user: Annotated[UserTokenInfo, Depends(get_current_superuser)],
    section_name: str,
    session: AsyncSession = Depends(get_async_session),
):

    stmt = delete(Section).filter(Section.name == section_name)
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
    return JSONResponse(
        content={"message": "Section deleted"}, status_code=status.HTTP_202_ACCEPTED
    )


@router.patch("/update/", response_model=MessageResponse)
async def update_section(
    user: Annotated[UserTokenInfo, Depends(get_current_superuser)],
    section: SectionCreate = Query(),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        stmt = (
            update(Section)
            .filter(Section.name == section.name)
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
        content={"message": "Section update"}, status_code=status.HTTP_200_OK
    )


@router.get("/{section_name}", response_model=SectionRead)
async def get_section_by_name(
    user: Annotated[UserTokenInfo, Depends(get_current_user)],
    section_name: str,
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Section).filter(Section.name == section_name)
    result = await session.execute(query)

    result = result.scalars().one_or_none()

    if result is None:
        logger.info(
            f"{user.email}: Trying to select a non-existent section {section_name}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section {section_name} not found",
        )

    logger.info(f"{user.email}: Select info of section {section_name}")
    return SectionRead.model_validate(result)


@router.get("/list/", response_model=SectionPaginationResponse)
async def get_sections(
    desc: bool = Query(False, description="Тип сортировки"),
    filter_name: Optional[str] = Query(None, description="Фамилия"),
    page_size: int = Query(10, ge=1, le=100, description="Размер страницы"),
    last_section_name: Optional[str] = Query(
        None, description="Последний на предыдущей странице"
    ),
    user: UserTokenInfo = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Section)

    query = (
        query.order_by(Section.name.desc()) if desc else query.order_by(Section.name)
    )

    if last_section_name:
        cursor_filter = (
            (Section.name < last_section_name)
            if desc
            else (Section.name > last_section_name)
        )
        query.filter(cursor_filter)

    if filter_name:
        query = query.filter(User.surname.ilike(f"%{filter_name}%"))

    query = query.limit(page_size + 1)

    results = await session.execute(query)
    results = results.scalars().all()
    sections = [SectionRead.model_validate(section) for section in results]

    is_final = False if len(results) > page_size else True

    now_last_name = None if is_final else sections[-2].name

    logger.info(
        f"{user.email}: Selected sections with params pg_size = {page_size}, desc = {desc}, l_name = {last_section_name}"
    )

    return SectionPaginationResponse(
        items=sections[:page_size],
        last_section_name=now_last_name,
        final=is_final,
        size=page_size,
    )
