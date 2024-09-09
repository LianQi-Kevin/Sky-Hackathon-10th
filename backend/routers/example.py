import logging

from fastapi import APIRouter

app_router = APIRouter(prefix="/api/example", tags=["example"])

@app_router.get("/", summary="example")
async def example():
    logging.info("example")
    return "example"
