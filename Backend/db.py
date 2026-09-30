import os

from sqlalchemy import ForeignKey, create_engine, String
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, DeclarativeBase
from uuid import uuid4

DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres")
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    
class CategoryORM(Base):
    __tablename__ = "categories"
    name: Mapped[str]


class TaskORM(Base):
    __tablename__ = "tasks"
    title: Mapped[str]
    # Атрибут называется completed, а колонка в БД осталась "done" - миграция переименования не нужна
    completed: Mapped[bool] = mapped_column("done", default=False)
    category_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, default=None
    )


class TaskSchema(BaseModel):
    id: str
    title: str
    completed: bool
    category_id: str | None = None

class TaskCreate(BaseModel):
    title: str
    category_id: str | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None
    category_id: str | None = None

    
    
class CategoryGetSchema(BaseModel):
    id: str
    name: str

class CategoryCreateSchema(BaseModel):
    name: str
    
class CategoryUpdateSchema(BaseModel):
    name: str | None = None
    