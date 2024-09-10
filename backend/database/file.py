import time
import uuid
from typing import Optional, Literal

from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field as sqlField


# the db with uploaded files, item: id, file_name, upload_time, md5_code, embedded_status
class UploadFile(SQLModel):
    file_type: str = sqlField(description="file type")
    md5_code: str = sqlField(index=True, unique=True, description="file md5 code")
    upload_time: Optional[float] = sqlField(default_factory=time.time, description="upload time")
    embedded_status: Optional[str] = sqlField(default="pending", description="['pending', 'embedding', 'embedded']")

class UploadFileDB(UploadFile, table=True):
    id: uuid.UUID = sqlField(default_factory=uuid.uuid4, primary_key=True, description="file id")


class FileEmbeddedResponse(BaseModel):
    status: Literal["verified", "success", "embedding", "field"]
    data: UploadFile
    message: str
