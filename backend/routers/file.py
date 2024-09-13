import os
import hashlib
import uuid
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, WebSocket, Depends
from langchain_core.documents import Document
from sqlalchemy import Engine
from sqlmodel import Session, select
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.word_document import Docx2txtLoader

from ..exceptions import (
    file_md5_exception,
    file_md5_ws_exception,
    file_notFound_ws_exception,
    file_type_exception,
    nvapi_verify_failed_ws_exception
)
from ..tools import nvapi_verify
from ..types import UploadFileDB, FileEmbeddedResponse
from ..lifespanDB import get_cache_db
from ..basic_configs import CACHE_PATH, CHUNK_SIZE, CHUNK_OVERLAP, SEPARATORS

app_router = APIRouter(prefix="/api/file", tags=["file"])


# /api/file/
@app_router.post("/", response_model=UploadFileDB)
async def upload_file(file: UploadFile = File(...), file_md5: str = Form(...), cache_db: Engine = Depends(get_cache_db)):
    # verify md5
    file_raw = file.file.read()
    file_md5_ = hashlib.md5(file_raw).hexdigest()
    if file_md5_ != file_md5:
        raise file_md5_exception

    # 查找md5值是否已存在
    with Session(cache_db) as session:
        statement = select(UploadFileDB).where(UploadFileDB.md5_code == file_md5)
        result: UploadFileDB = session.exec(statement).first()

    if not result:
        session_tag: UploadFileDB = UploadFileDB(md5_code=file_md5, file_suffix=os.path.splitext(file.filename)[1])
        # write_db
        with Session(cache_db) as session:
            session.add(session_tag)
            session.commit()
            session.refresh(session_tag)
        result: UploadFileDB = session_tag

    # write_file
    target_file_path = os.path.join(CACHE_PATH, result.md5_code, f"{result.md5_code}{result.file_suffix}")
    if not os.path.exists(target_file_path):
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
        with open(target_file_path, "wb") as f:
            f.write(file_raw)

    return result


# /api/file/{file_id}/ws
@app_router.websocket("/{file_id}")
async def embedded_file(
        *,
        websocket: WebSocket,
        file_id: uuid.UUID,
        file_md5: str,
        nv_api_key: str,
        cache_db=Depends(get_cache_db)
):
    await websocket.accept()

    await websocket.send_json(FileEmbeddedResponse(status="verifying", message="start verify files").model_dump())
    # verify nv_api_key
    if not nvapi_verify(nv_api_key):
        raise nvapi_verify_failed_ws_exception
        # await websocket.send_json(InvokeResponse(status="field", message="nv_api_key verify failed").model_dump())

    # get file from db
    with Session(cache_db) as session:
        statement = select(UploadFileDB).where(UploadFileDB.id == file_id)
        result: UploadFileDB = session.exec(statement).first()
    if not result:
        raise file_notFound_ws_exception

    # verify file exists
    file_path = os.path.join(CACHE_PATH, result.md5_code, f"{result.md5_code}{result.file_suffix}")
    if not os.path.exists(file_path):
        # remove item in db
        with Session(cache_db) as session:
            session.delete(result)
            session.commit()
        raise file_notFound_ws_exception

    # verify md5
    if result.md5_code != file_md5:
        raise file_md5_ws_exception

    # verify finished, return model
    await websocket.send_json(
        FileEmbeddedResponse(status="verified", data=result, message="Successful verified").model_dump()
    )

    # check embedded_status
    if result.embedded_status == "embedded":
        # check cache .faiss & .pkl file
        if os.path.exists(os.path.join(CACHE_PATH, result.md5_code, f"{result.md5_code}.faiss")) and \
                os.path.exists(os.path.join(CACHE_PATH, result.md5_code, f"{result.md5_code}.pkl")):
            await websocket.send_json(
                FileEmbeddedResponse(status="success", data=result, message="Successfully embedded").model_dump()
            )
            await websocket.close()
            return

    # verify file type (.pdf/.md) and get file loader
    # todo: support more file type
    doc = file_loader(file_path)

    # set status to embedding
    with Session(cache_db) as session:
        statement = select(UploadFileDB).where(UploadFileDB.id == file_id)
        result: UploadFileDB = session.exec(statement).first()
        result.embedded_status = "embedding"
        session.commit()
        session.refresh(result)

    # return embedding status
    await websocket.send_json(
        FileEmbeddedResponse(status="embedding", data=result, message="Start embedding").model_dump()
    )

    # file Loader
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
                                                   separators=SEPARATORS)

    # doc spliter
    doc_chunks = text_splitter.split_documents(doc)

    # embedder
    embedder = NVIDIAEmbeddings(model="nvidia/nv-embed-v1", truncate="END", api_key=nv_api_key)
    standard_store = FAISS.from_documents(doc_chunks, embedder)
    standard_store.save_local(folder_path=os.path.join(CACHE_PATH, result.md5_code), index_name=result.md5_code)

    # update DB
    with Session(cache_db) as session:
        statement = select(UploadFileDB).where(UploadFileDB.id == file_id)
        result: UploadFileDB = session.exec(statement).first()
        result.embedded_status = "embedded"
        session.commit()
        session.refresh(result)

    # send response
    await websocket.send_json(
        FileEmbeddedResponse(status="success", data=result, message="Successfully embedded").model_dump()
    )

    # close websocket
    await websocket.close()
    return
    # except Exception as e:
    #     # 针对非预期错误，返回错误信息
    #     await websocket.send_json(InvokeResponse(status="field", message=str(e)).model_dump())
    #     await websocket.close()
    #     return


# get standard file list
# @app_router.get("/standard")
# async def get_standard_file_list():
#     with Session(CACHE_DB) as session:
#         statement = select(UploadFileDB).where(UploadFileDB.file_type == "STANDARD")
#         result: UploadFileDB = session.exec(statement).all()
#     return result


# file loader
def file_loader(file_path: str) -> List[Document]:
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith((".md", ".markdown")):
        loader = UnstructuredMarkdownLoader(file_path)
    elif file_path.endswith((".txt", ".text")):
        loader = TextLoader(file_path)
    elif file_path.endswith((".doc", ".docx")):
        loader = Docx2txtLoader(file_path)
    else:
        raise file_type_exception
    return loader.load()


# verify file exists
def verify_file_exists(file_id: uuid.UUID, file_md5: str) -> UploadFileDB:
    with Session(get_cache_db()) as session:
        statement = select(UploadFileDB).where(UploadFileDB.id == file_id)
        result: UploadFileDB = session.exec(statement).first()
    if not result:
        return file_notFound_ws_exception
    if result.md5_code != file_md5:
        return file_md5_ws_exception
    file_path = os.path.join(CACHE_PATH, result.md5_code, f"{result.md5_code}{result.file_suffix}")
    if not os.path.exists(file_path):
        return file_notFound_ws_exception
    return result
