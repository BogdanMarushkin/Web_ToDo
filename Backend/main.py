from fastapi import FastAPI, status, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from lifespan import lifespan
from db import TaskORM, TaskSchema, TaskCreate, TaskUpdate, SessionLocal
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(lifespan=lifespan)

app.add_middleware (
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"]
)

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

            