import os
import shutil
from contextlib import asynccontextmanager
# from typing import List

from fastapi import FastAPI
from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine
# from sqlmodel import Session, select

from .basic_configs import CACHE_PATH
# from .basic_configs import STANDARD_PATH
# from .database import UploadFileDB

shutil.rmtree(CACHE_PATH, ignore_errors=True)
os.makedirs(CACHE_PATH, exist_ok=True)
CACHE_DB: Engine = create_engine(f'sqlite:///{CACHE_PATH}/cache_db.db', echo=True)

# standard db
# os.makedirs(STANDARD_PATH, exist_ok=True)
# STANDARD_DB: Engine = create_engine(f'sqlite:///{STANDARD_PATH}/standard_db.db', echo=True)


def get_cache_db():
    return CACHE_DB


# noinspection PyUnusedLocal
@asynccontextmanager
async def lifespan(app: FastAPI):
    global CACHE_DB
    # init cache
    SQLModel.metadata.create_all(CACHE_DB)

    yield
    # remove all un-standard files in db
    # with Session(CACHE_DB) as session:
    #     statement = select(UploadFileDB).where(UploadFileDB.file_type == "MATERIAL")
    #     results: List[UploadFileDB] = session.exec(statement).all()
    #     for item in results:
    #         file_path = os.path.join(CACHE_PATH, item.md5_code, f"{item.md5_code}{item.file_suffix}")
    #         if not os.path.exists(file_path):
    #             session.delete(item)
    #     session.commit()

    # clean cache
    CACHE_DB.dispose()
    shutil.rmtree(CACHE_PATH, ignore_errors=True)

