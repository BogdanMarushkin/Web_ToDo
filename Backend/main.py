from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from lifespan import lifespan
from db import TaskORM, TaskSchema, TaskCreate, TaskUpdate, SessionLocal, CategoryGetSchema, CategoryORM, CategoryCreateSchema, CategoryUpdateSchema
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

def category_orm_to_model(category_orm: CategoryORM) -> CategoryGetSchema:
    
    return CategoryGetSchema(id=category_orm.id, name=category_orm.name)


@app.get("/tasks")
def read_tasks(db: Session = Depends(get_db)) -> list[TaskSchema]:
    
    task_from_db = db.scalars(select(TaskORM)).all()
    
    return [task_orm_to_model(task) for task in task_from_db]

@app.get("/categories")
def get_category(db: Session = Depends(get_db)) -> list[CategoryGetSchema]:
    
    category_from_db = db.scalars(select(CategoryORM)).all()
    
    return [category_orm_to_model(category) for category in category_from_db]

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskSchema:
    
    new_task = TaskORM(title=payload.title, done=False)
    
    db.add(new_task)
    
    db.commit()
    
    return task_orm_to_model(new_task)

@app.post("/categories")
def create_category(payload: CategoryCreateSchema, db: Session = Depends(get_db)) -> CategoryGetSchema:
    
    new_category = CategoryORM(name=payload.name)
    
    db.add(new_category)
    
    db.commit()
    
    db.refresh(new_category)
    
    return category_orm_to_model(new_category)

@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(get_db)):
    
    task_for_update = db.get(TaskORM, task_id)
    
    if task_for_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    if payload.title is not None: 
        task_for_update.title = payload.title
        
    if payload.done is not None:
        task_for_update.done = payload.done
        
    db.commit()
    
    return task_for_update

@app.patch("/categories/{category_id}")
def update_category(category_id: str, payload: CategoryUpdateSchema, db: Session = Depends(get_db)):
    
    category_for_update = db.get(CategoryORM, category_id)
    
    if category_for_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    if payload.title:
        category_for_update.name = payload.title
        
    db.commit()
    
    return category_for_update
    
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    
    task_for_delete = db.get(TaskORM, task_id)
    
    if task_for_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    db.delete(task_for_delete)
    
    db.commit()
    
@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, db: Session = Depends(get_db)):
    
    category_for_delete = db.get(CategoryORM, category_id)
    
    if category_for_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    db.delete(category_for_delete)
    
    db.commit()
    
    

            