from pydantic import BaseModel
from typing import Optional

class Job(BaseModel):
    job_id: str
    status: str
    file_s3: Optional[str] = None
