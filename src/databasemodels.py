from datetime import date
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Date, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase): ...


class Vacation(Base):
    __tablename__ = "vacation"
    id: Mapped[int] = mapped_column(primary_key=True)
    giver_email: Mapped[str] = mapped_column(
        ForeignKey(
            "user.email",
            use_alter=True,
            name="fk_vacation_giv_user",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    receiver_email: Mapped[str] = mapped_column(
        ForeignKey(
            "user.email",
            use_alter=True,
            name="fk_vacation_rev_user",
            ondelete="CASCADE",
        ),
    )
    start_date = mapped_column(Date, default=date.today)
    end_date = mapped_column(Date)
    created_date = mapped_column(Date, default=date.today)
    description: Mapped[str] = mapped_column(nullable=True)

    giver = relationship(
        "User", back_populates="given_vacations", foreign_keys=[giver_email]
    )

    receiver = relationship(
        "User", back_populates="receiver_vacations", foreign_keys=[receiver_email]
    )

    __table_args__ = (
        Index("ix_vacation_receiver_id", receiver_email),
        Index("ix_vacation_giver_id", giver_email),
        Index("ix_vacation_dates", start_date, end_date),
    )


class Section(Base):
    __tablename__ = "section"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, index=True, unique=True)
    head_email: Mapped[str] = mapped_column(
        ForeignKey(
            "user.email", use_alter=True, name="fk_section_user", ondelete="SET NULL"
        ),
        nullable=True,
    )

    head = relationship(
        "User", back_populates="section_headed", foreign_keys=[head_email]
    )
    __table_args__ = (Index("ix_section_head_email", head_email),)


class Position(Base):
    __tablename__ = "position"
    id: Mapped[int] = mapped_column(primary_key=True)
    section_name: Mapped[str] = mapped_column(
        ForeignKey(
            "section.name",
            use_alter=True,
            name="fk_position_section",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)

    user = relationship("User", back_populates="position")
    __table_args__ = (Index("ix_position_section_name", section_name),)


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    position_name: Mapped[str] = mapped_column(
        ForeignKey(
            "position.name",
            use_alter=True,
            name="fk_user_position",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    joined_at = mapped_column(Date, default=date.today)
    birthday = mapped_column(Date)

    position = relationship("Position", back_populates="user")

    section_headed = relationship("Section", back_populates="head")

    given_vacations = relationship(
        "Vacation", back_populates="giver", foreign_keys=[Vacation.giver_email]
    )
    receiver_vacations = relationship(
        "Vacation",
        back_populates="receiver",
        foreign_keys="Vacation.receiver_email",
    )
    __table_args__ = (
        Index("ix_user_position_name", position_name),
        Index("ix_user_surname_name", surname, name),
    )
