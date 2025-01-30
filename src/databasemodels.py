from datetime import date
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Date, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase): ...


class Vacation(Base):
    __tablename__ = "vacation"
    id: Mapped[int] = mapped_column(primary_key=True)
    giver_id: Mapped[int] = mapped_column(
        ForeignKey(
            "user.id",
            use_alter=True,
            name="fk_vacation_giv_user",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    receiver_id: Mapped[int] = mapped_column(
        ForeignKey(
            "user.id",
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
        "User", back_populates="given_vacations", foreign_keys=[giver_id]
    )

    receiver = relationship(
        "User", back_populates="receiven_vacations", foreign_keys=[receiver_id]
    )

    __table_args__ = (
        Index("ix_vacation_receiver_id", receiver_id),
        Index("ix_vacation_giver_id", giver_id),
        Index("ix_vacation_start_date", start_date),
        Index("ix_vacation_end_date", end_date),
        Index("ix_vacation_dates", start_date, end_date),
    )


class Section(Base):
    __tablename__ = "section"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, index=True, unique=True)
    head_id: Mapped[int] = mapped_column(
        ForeignKey(
            "user.id", use_alter=True, name="fk_section_user", ondelete="SET NULL"
        ),
        nullable=True,
    )

    head = relationship("User")

    __table_args__ = (Index("ix_section_head_email", head_id),)


class Position(Base):
    __tablename__ = "position"
    id: Mapped[int] = mapped_column(primary_key=True)
    section_id: Mapped[int] = mapped_column(
        ForeignKey(
            "section.id",
            use_alter=True,
            name="fk_position_section",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)

    section = relationship("Section")

    __table_args__ = (Index("ix_position_section_name", section_id),)


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    position_id: Mapped[str] = mapped_column(
        ForeignKey(
            "position.id",
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

    given_vacations = relationship(
        "Vacation", back_populates="giver", foreign_keys=[Vacation.giver_id]
    )
    receiven_vacations = relationship(
        "Vacation",
        back_populates="receiver",
        foreign_keys=[Vacation.receiver_id],
    )
    __table_args__ = (
        Index("ix_user_position_name", position_id),
        Index("ix_user_surname_name", surname, name),
    )
