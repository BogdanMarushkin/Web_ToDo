from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from lifespan import lifespan
from db import TaskORM, TaskSchema, TaskCreate, TaskUpdate, SessionLocal, CategoryGetSchema, CategoryORM, CategoryCreateSchema, CategoryUpdateSchema
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(lifespan=lifespan)

app.add_middleware (
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

def task_orm_to_model(task_orm: TaskORM) -> TaskSchema:
    
    return TaskSchema(
        id=task_orm.id,
        title=task_orm.title,
        completed=task_orm.completed,
        category_id=task_orm.category_id,
    )

def ensure_category_exists(db: Session, category_id: str) -> None:
    
    if db.get(CategoryORM, category_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

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
    
    if payload.category_id is not None:
        ensure_category_exists(db, payload.category_id)
    
    new_task = TaskORM(title=payload.title, completed=False, category_id=payload.category_id)
    
    db.add(new_task)
    
    db.commit()
    
    db.refresh(new_task)
    
    return task_orm_to_model(new_task)

@app.post("/categories", status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreateSchema, db: Session = Depends(get_db)) -> CategoryGetSchema:
    
    new_category = CategoryORM(name=payload.name)
    
    db.add(new_category)
    
    db.commit()
    
    db.refresh(new_category)
    
    return category_orm_to_model(new_category)

@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(get_db)) -> TaskSchema:
    
    task_for_update = db.get(TaskORM, task_id)
    
    if task_for_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # exclude_unset нужен, чтобы отличать "category_id": null (снять категорию) от отсутствующего поля
    changes = payload.model_dump(exclude_unset=True)
    
    if changes.get("title") is not None:
        task_for_update.title = changes["title"]
        
    if changes.get("completed") is not None:
        task_for_update.completed = changes["completed"]
        
    if "category_id" in changes:
        new_category_id = changes["category_id"]
        if new_category_id is not None:
            ensure_category_exists(db, new_category_id)
        task_for_update.category_id = new_category_id
        
    db.commit()
    
    db.refresh(task_for_update)
    
    return task_orm_to_model(task_for_update)

@app.patch("/categories/{category_id}")
def update_category(category_id: str, payload: CategoryUpdateSchema, db: Session = Depends(get_db)) -> CategoryGetSchema:
    
    category_for_update = db.get(CategoryORM, category_id)
    
    if category_for_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    if payload.name:
        category_for_update.name = payload.name
        
    db.commit()
    
    db.refresh(category_for_update)
    
    return category_orm_to_model(category_for_update)
    
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
    
    # Задачи удалённой категории не удаляем, а отвязываем (не полагаемся только на ON DELETE SET NULL)
    db.execute(update(TaskORM).where(TaskORM.category_id == category_id).values(category_id=None))
    
    db.delete(category_for_delete)
    
    db.commit()

            