from sqlalchemy import INTEGER, String, Boolean, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM
from typing import Annotated

from db.database import Base

main_id = Annotated[int, mapped_column(INTEGER, primary_key=True, autoincrement=True, nullable=False)]
str_200 = Annotated[str, mapped_column(String(200), nullable=False)]

class Questions(Base):
    __tablename__ = "questions"

    id: Mapped[main_id]
    text: Mapped[str_200]
    hash: Mapped[str]
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    complexity_id: Mapped[int] = mapped_column(ForeignKey("complexity.id"))

    category: Mapped["Categories"] = relationship()
    complexity: Mapped["Complexity"] = relationship()
    options: Mapped[list["Options"]] = relationship()

class Options(Base):
    __tablename__ = "options"

    id: Mapped[main_id]
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    text: Mapped[str_200]
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=True, server_default=False)

    question: Mapped["Questions"] = relationship()

class Categories(Base):
    __tablename__ = "categories"

    id: Mapped[main_id]
    name: Mapped[str_200]

    questions: Mapped[list["Questions"]] = relationship()

class Complexity(Base):
    __tablename__ = "complexity"

    id: Mapped[main_id]
    level: Mapped[str] = mapped_column(ENUM('easy', 'medium', 'hard', 'very hard'))

    questions: Mapped[list["Questions"]] = relationship()

