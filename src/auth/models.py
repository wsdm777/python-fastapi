from datetime import UTC, datetime
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String

Base = declarative_base()

def timenow():
    return datetime.now(UTC).replace(tzinfo=None)

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"
    id: int = Column(Integer, primary_key=True)
    email: str = Column(String, nullable=False)
    hashed_password: str = Column(String, nullable=False)
    is_active: bool = Column(Boolean, default=True)
    is_superuser: bool = Column(Boolean, default=False)
    is_verified: bool = Column(Boolean, default=False)
    name: str = Column(String, nullable=False)
    role_id: int = Column(Integer, ForeignKey("role.id"))
    register_at = Column(TIMESTAMP(timezone=True), default=timenow)



class Role(Base):
    __tablename__ = "role"
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, nullable=False)
    permiss: str = Column(String)
    descr: str = Column(String)