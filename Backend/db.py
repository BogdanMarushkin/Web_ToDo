from sqlalchemy import create_engine, String
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, DeclarativeBase
from uuid import uuid4

DB_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    
class TaskORM(Base):
    __tablename__ = "tasks"
    title: Mapped[str] 
    done: Mapped[bool] = mapped_column(default=False)


class TaskSchema(BaseModel):
    id: str
    title: str
    done: bool
    
class TaskCreate(BaseModel):
    title: str
    
class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None