from fastapi import FastAPI, status, Depends
from pydantic import BaseModel
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped, Session
from contextlib import asynccontextmanager

DB_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    
class TaskORM(Base):
    __tablename__ = "tasks"
    title: Mapped[str] 
    done: Mapped[bool] = mapped_column(default=False)
    
 
@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

def task_orm_to_model(task_orm: TaskORM) -> TaskSchema:
    return TaskSchema(id=task_orm.id, title=task_orm.title, done=task_orm.done)


@app.get("/tasks")
def read_tasks(db: Session = Depends(get_db)) -> list[TaskSchema]:
    
    task_from_db = db.scalars(select(TaskORM)).all()
    
    return [task_orm_to_model(task) for task in task_from_db]


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskSchema:
    
    new_task = TaskORM(title=payload.title, done=False)
    
    db.add(new_task)
    
    db.commit()
    
    return task_orm_to_model(new_task)

@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(get_db)):
    
    task_for_update = db.get(TaskORM, task_id)
    
    if payload.title: 
        task_for_update.title = payload.title
        
    if payload.done:
        task_for_update.done = payload.done
        
    db.commit()
    
    return task_for_update

    
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    
    task_for_delete = db.get(TaskORM, task_id)
    
    db.delete(task_for_delete)
    
    db.commit()

            