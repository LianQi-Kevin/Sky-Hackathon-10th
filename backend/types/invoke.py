# import time
# import uuid
from typing import Optional, Literal

from pydantic import BaseModel, Field
# from sqlmodel import SQLModel, Field as sqlField


# invoke response
class InvokeResponse(BaseModel):
    status: Literal["verifying", "loading", "extracting", "retrieving", "checking", "summarizing", "querying", "success", "field"]
    message: Optional[str] = Field(default="", description="message")
    result: Optional[str] = Field(default="", description="result")