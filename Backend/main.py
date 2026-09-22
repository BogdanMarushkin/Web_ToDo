from fastapi import FastAPI, status
from pydantic import BaseModel
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped
from contextlib import asynccontextmanager

DB_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    
class TaskORM(Base):
    __tablename__ = "tasks",
    title: Mapped[str] 
    done: Mapped[bool] = mapped_column(default=False)
    
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
)
tasks: list[TaskSchema] = []

class TaskSchema(BaseModel):
    id: str
    title: str
    done: bool
    
class TaskCreate(BaseModel):
    title: str
    
class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

@app.get("/tasks")
def read_tasks() -> list[TaskSchema]:
    return tasks

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> TaskSchema:
    new_task = TaskSchema(id=str(uuid4()), title=payload.title, done=False)
    tasks.append(new_task)
    return new_task

@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdate):
    for task in tasks:
        if task.id == task_id:
            if payload.title:
                task.title = payload.title
            if payload.done is not None:
                task.done = payload.done
            
            return task
    
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            