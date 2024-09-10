import os
import shutil
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine

from .basic_configs import CACHE_PATH

shutil.rmtree(CACHE_PATH, ignore_errors=True)
os.makedirs(CACHE_PATH, exist_ok=True)
CACHE_DB: Engine = create_engine(f'sqlite:///{CACHE_PATH}/cache_db.db', echo=True)


# noinspection PyUnusedLocal
@asynccontextmanager
async def lifespan(app: FastAPI):
    global CACHE_DB
    # init cache
    SQLModel.metadata.create_all(CACHE_DB)

    yield
    # clean cache
    CACHE_DB.dispose()
    shutil.rmtree(CACHE_PATH, ignore_errors=True)

