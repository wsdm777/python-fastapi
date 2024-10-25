from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String

Base = declarative_base()



class User(Base):
    __tablename__ = "user"
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, nullable=False)
    role_id: int = Column(Integer, ForeignKey("role.id"))
    
    


class Role(Base):
    __tablename__ = "role"
    id: int = Column(Integer, primary_key=True)