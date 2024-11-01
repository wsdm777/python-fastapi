from datetime import UTC, datetime
from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from src.auth.models import User


Base = declarative_base()


def timenow():
    return datetime.now(UTC).replace(tzinfo=None)


class Post(Base):
    __tablename__ = "post"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(User.id, onupdate="CASCADE", ondelete="CASCADE")
    )
    topic: Mapped[str] = mapped_column(String, nullable=False)
    content = mapped_column(String, nullable=True)
    created_at = mapped_column(TIMESTAMP(timezone=True), default=timenow)
