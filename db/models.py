import datetime
from sqlalchemy import INTEGER, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM
from typing import Annotated

from db.database import Base

main_id = Annotated[int, mapped_column(INTEGER, primary_key=True, autoincrement=True, nullable=False, unique=True)]
str_500 = Annotated[str, mapped_column(String(500), nullable=False)]

class Hashs(Base):
    __tablename__ = "hashs"

    id: Mapped[main_id]
    hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    question: Mapped["Questions"] = relationship()

class Questions(Base):
    __tablename__ = "questions"

    id: Mapped[main_id]
    text: Mapped[str_500]
    verified: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    complexity: Mapped[str] = mapped_column(ENUM('easy', 'medium', 'hard', 'very hard', name='complexity_level_enum'))
    lang: Mapped[str] = mapped_column(String(3))

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    category: Mapped["Categories"] = relationship()
    options: Mapped[list["Options"]] = relationship()

class Options(Base):
    __tablename__ = "options"

    id: Mapped[main_id]
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    text: Mapped[str] = mapped_column(String(256), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=True, server_default="false")

    question: Mapped["Questions"] = relationship()

class Categories(Base):
    __tablename__ = "categories"

    id: Mapped[main_id]
    name: Mapped[str] = mapped_column(String(64), server_default=None, unique=True, nullable=False)

    questions: Mapped[list["Questions"]] = relationship()


# Scheduler / Timer
class Scheduler(Base):
    __tablename__ = "scheduler"

    id: Mapped[main_id]
    name: Mapped[str] #"web-site",
    url: Mapped[str] #"website.com"
    state: Mapped[str] = mapped_column(ENUM("WORKING", "PAUSED", "STOPED", name='state_scheduler_enum'))
    mode: Mapped[str] = mapped_column(ENUM("CRON", "TIMER", name='mode_scheduler_enum'))
    schedule: Mapped[str]
    interval: Mapped[int]
    nextRunAt: Mapped[datetime]
    lastRunAt: Mapped[datetime]

