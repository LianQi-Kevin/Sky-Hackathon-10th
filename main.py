import argparse
import logging
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.lifespanDB import lifespan
from backend.routers import file_router, invoke_router
from backend.tools import log_set

# init logging
log_set(logging.DEBUG)

# init Fastapi
app = FastAPI(lifespan=lifespan)
app.include_router(file_router)
app.include_router(invoke_router)


# load vue dist
@app.get("/")
async def get_index():
    return FileResponse('dist/index.html')


@app.get("/{custom_path:path}")
async def get_static_files_or_404(custom_path):
    # try open file for path
    file_path = os.path.join("dist", custom_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse('dist/index.html')


app.mount("/dist", StaticFiles(directory="dist/"), name="dist")
# noinspection PyTypeChecker
app.add_middleware(GZipMiddleware, minimum_size=1000)

# allow CORS
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the FastAPI server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host of the server")
    parser.add_argument("--port", type=int, default=12538, help="Port of the server")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)
