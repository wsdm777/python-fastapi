from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from src.auth.user.models import User, timenow


Base = declarative_base()


class Post(Base):
    __tablename__ = "post"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(User.id, onupdate="CASCADE", ondelete="CASCADE")
    )
    topic: Mapped[str] = mapped_column(String, nullable=False)
    content = mapped_column(String, nullable=True)
    created_at = mapped_column(TIMESTAMP, default=timenow)
