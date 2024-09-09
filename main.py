import argparse
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.tools import log_set
from backend.routers import example_router

# init logging
log_set(logging.DEBUG)

# init Fastapi
app = FastAPI()
app.include_router(example_router)

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
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host of the server")
    parser.add_argument("--port", type=int, default=12538, help="Port of the server")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)