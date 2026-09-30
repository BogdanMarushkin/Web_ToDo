from main import FastAPI
from sqlalchemy import text
from db import engine, Base
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)

    # create_all не добавляет колонки в уже существующие таблицы,
    # поэтому для старых БД добавляем category_id вручную (идемпотентно)
    with engine.begin() as conn:
        conn.execute(text(
            "ALTER TABLE tasks "
            "ADD COLUMN IF NOT EXISTS category_id VARCHAR "
            "REFERENCES categories(id) ON DELETE SET NULL"
        ))
    yield