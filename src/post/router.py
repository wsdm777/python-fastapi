from fastapi import APIRouter, Depends
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.post.schemas import PostRead
from src.schemas import goodResponse
from src.post.models import Post
from src.database import get_async_session
from src.auth.models import User
from src.auth.userrouter import current_user

router = APIRouter(prefix="/post", tags=["post"])


@router.post("", response_model=goodResponse)
async def postPost(
    topic: str,
    content: str | None = None,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = insert(Post).values(
        {"user_id": user.id, "topic": topic, "content": content}
    )
    await session.execute(query)
    await session.commit()
    return {"status": 201}


@router.get("/{id}")
async def get_post_by_id(id: int, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Post).where(Post.id == id)
    result = await session.execute(stmt)
    result = result.scalars().one()
    return PostRead.model_validate(result, from_attributes=True)
