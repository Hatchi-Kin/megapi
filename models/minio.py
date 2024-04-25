from pydantic import BaseModel
from typing import List


class S3Object(BaseModel):
    name: str
    size: int
    etag: str
    last_modified: str