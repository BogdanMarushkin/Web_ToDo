from main import FastAPI
from db import engine, Base
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield