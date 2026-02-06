import uuid
from fastapi import APIRouter, UploadFile, File
from app.services.s3 import upload_file_to_s3
from app.services.sqs import enqueue_job

router = APIRouter()

@router.post("/")
async def create_job(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())

    s3_path = upload_file_to_s3(file, job_id)

    enqueue_job({
        "job_id": job_id,
        "file_s3": s3_path,
        "notify": ["slack"]
    })

    return {
        "job_id": job_id,
        "status": "QUEUED"
    }


@router.get("/{job_id}")
def get_job_status(job_id: str):
    # Demo version – real version đọc DB
    return {
        "job_id": job_id,
        "status": "PROCESSING"
    }
