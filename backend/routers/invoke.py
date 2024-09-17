import json
import os.path
import uuid
import logging

from fastapi import APIRouter, WebSocket
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from operator import itemgetter

from ..basic_configs import CACHE_PATH, CHUNK_SIZE, CHUNK_OVERLAP, SEPARATORS
from ..exceptions import file_notEmbedded_ws_exception, nvapi_verify_failed_ws_exception
from ..prompt_template import decomposition_prompt, check_prompt, summary_prompt, query_prompt
from ..types import InvokeResponse, UploadFileDB
from .file import verify_file_exists, file_loader
from ..tools import nvapi_verify

app_router = APIRouter(prefix="/api/invoke", tags=["invoke"])


#/api/invoke/query
@app_router.websocket("/query")
async def query_standard(
        *,
        websocket: WebSocket,
        question: str,
        standard_file_id: uuid.UUID,
        standard_file_md5: str,
        nv_api_key: str,
        embedder_model: str = "nvidia/nv-embed-v1",
        chat_model: str = "mistralai/mixtral-8x7b-instruct-v0.1",
):
    await websocket.accept()
    await websocket.send_json(InvokeResponse(status="verifying", message="start verify files").model_dump())
    # verify nv_api_key
    if not nvapi_verify(nv_api_key):
        raise nvapi_verify_failed_ws_exception
        # await websocket.send_json(InvokeResponse(status="field", message="nv_api_key verify failed").model_dump())

    # 根据file_id和file_md5提取文件
    standard_data: UploadFileDB = verify_file_exists(standard_file_id, standard_file_md5)

    # 根据file_id和file_md5查询数据库状态是否为embedded
    if standard_data.embedded_status != "embedded":
        raise file_notEmbedded_ws_exception

    # 加载standard faiss数据库
    await websocket.send_json(InvokeResponse(status="loading", message="start load faiss database").model_dump())
    embedder = NVIDIAEmbeddings(model=embedder_model, truncate="END", api_key=nv_api_key)
    standard_store = FAISS.load_local(
        folder_path=os.path.join(CACHE_PATH, standard_data.md5_code),
        index_name=standard_data.md5_code,
        embeddings=embedder,
        allow_dangerous_deserialization=True
    )

    # query standard
    await websocket.send_json(InvokeResponse(status="querying", message="start query").model_dump())
    retriever = standard_store.as_retriever()
    instruct_llm = ChatNVIDIA(model=chat_model, api_key=nv_api_key)
    query_chain = {"question": itemgetter("question"),
                   "standard": itemgetter("question") | retriever | RunnableLambda(lambda x: '\n'.join(
                       [y.page_content for y in x]))} | query_prompt | instruct_llm | StrOutputParser()
    query_res = query_chain.invoke({"question": question})

    # send response
    await websocket.send_json(InvokeResponse(status="success", message="success", result=query_res).model_dump())
    await websocket.close()
    return
    # except Exception as e:
    #     # 针对非预期错误，返回错误信息
    #     await websocket.send_json(InvokeResponse(status="field", message=str(e)).model_dump())
    #     await websocket.close()
    #     return


# /api/invoke/compare
@app_router.websocket("/compare")
async def compare_schema_with_standard(
        *,
        websocket: WebSocket,
        schema_file_id: uuid.UUID,
        schema_file_md5: str,
        standard_file_id: uuid.UUID,
        standard_file_md5: str,
        nv_api_key: str,
        embedder_model: str = "nvidia/nv-embed-v1",
        chat_model: str = "mistralai/mixtral-8x7b-instruct-v0.1",
):
    await websocket.accept()
    await websocket.send_json(InvokeResponse(status="verifying", message="start verify files").model_dump())
    # verify nv_api_key
    if not nvapi_verify(nv_api_key):
        raise nvapi_verify_failed_ws_exception
        # await websocket.send_json(InvokeResponse(status="field", message="nv_api_key verify failed").model_dump())

    # 根据file_id和file_md5提取文件
    schema_data: UploadFileDB = verify_file_exists(schema_file_id, schema_file_md5)
    standard_data: UploadFileDB = verify_file_exists(standard_file_id, standard_file_md5)

    # 根据file_id和file_md5查询数据库状态是否为embedded
    if standard_data.embedded_status != "embedded":
        raise file_notEmbedded_ws_exception

    # 加载standard faiss数据库
    await websocket.send_json(InvokeResponse(status="loading", message="start load faiss database").model_dump())
    embedder = NVIDIAEmbeddings(model=embedder_model, truncate="END", api_key=nv_api_key)
    standard_store = FAISS.load_local(
        folder_path=os.path.join(CACHE_PATH, standard_data.md5_code),
        index_name=standard_data.md5_code,
        embeddings=embedder,
        allow_dangerous_deserialization=True
    )

    # get schema file Loader and text spliter
    await websocket.send_json(InvokeResponse(status="loading", message="start load schema file").model_dump())
    schema_pages = file_loader(os.path.join(CACHE_PATH, schema_data.md5_code, f"{schema_data.md5_code}{schema_data.file_suffix}"))
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, separators=SEPARATORS)
    schema_chunks = text_splitter.split_documents(schema_pages)

    # 使用llm从schema文件提取条目
    # await websocket.send_json(InvokeResponse(status="extracting", message="start extract schema entries").model_dump())
    instruct_llm = ChatNVIDIA(model=chat_model, api_key=nv_api_key)
    problems = ""
    for index, chunk in enumerate(schema_chunks):
        await websocket.send_json(InvokeResponse(
            status="extracting", message=f"extracting schema entries, {index + 1}/{len(schema_chunks)}").model_dump())
        decomposition_chain = {"scheme": lambda x: chunk.page_content} | decomposition_prompt | instruct_llm | StrOutputParser()
        decomposition_str = decomposition_chain.invoke("")
        logging.debug(f"decomposition_str: {decomposition_str}")
        try:
            decomposition_list = json.loads(decomposition_str)
        except Exception:  # 冗余设计，避免输出的不是list[str]，增强代码健壮性
            logging.warning("cannot load as json")
            decomposition_list = decomposition_str.replace("\"", "").split(',')
        logging.debug(f"decomposition_list: {decomposition_list}")

        # 对decomposition之后的检查项逐一进行retrieve
        await websocket.send_json(InvokeResponse(
            status="retrieving", message=f"start retrieve standards, {index + 1}/{len(schema_chunks)}").model_dump())
        retriever = standard_store.as_retriever()
        retrieved_standards = set()
        for decomposition_item in decomposition_list:
            invoked = retriever.invoke(decomposition_item)
            for doc in invoked:
                retrieved_standards.add(doc.page_content)

        # 针对每一个分片进行retrieve+check
        await websocket.send_json(InvokeResponse(
            status="checking", message=f"start retrieve check, {index + 1}/{len(schema_chunks)}").model_dump())
        check_chain = {"scheme": lambda x: chunk.page_content,
                       #"standard": (lambda x: decomposition_str + chunk.page_content) | retriever | RunnableLambda(lambda x: ''.join([y.page_content for y in x]))} | check_prompt | instruct_llm | StrOutputParser()
                       "standard": (lambda x: '\n'.join(retrieved_standards))} | check_prompt | instruct_llm | StrOutputParser()
        problems += check_chain.invoke("")

    # 如果设计文档被分片了，对所有分片的合规检测结果进行总结
    if len(schema_chunks) > 1:
        await websocket.send_json(InvokeResponse(
            status="summarizing", message="start summarize all problems").model_dump())
        summary_chain = {"problem_list": lambda x: problems} | summary_prompt | instruct_llm | StrOutputParser()
        problems = summary_chain.invoke("")
    await websocket.send_json(InvokeResponse(status="success", message="success", result=problems).model_dump())
    await websocket.close()
    return
# except Exception as e:
    #     # 针对非预期错误，返回错误信息
    #     await websocket.send_json(InvokeResponse(status="field", message=str(e)).model_dump())
    #     await websocket.close()
    #     return