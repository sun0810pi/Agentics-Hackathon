"""
Jobs API - File Upload & Processing
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.models.job import JobResponse, JobListResponse
from app.services.job_service import JobService
from app.core.dependencies import get_current_user

router = APIRouter()
job_service = JobService()

@router.post("/upload", response_model=JobResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload invoice file and start processing"""
    
    # Validate file
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only Excel/CSV files allowed."
        )
    
    # Create job and upload file
    job = await job_service.create_job_and_upload(
        file=file,
        user_email=current_user["email"]
    )
    
    return job

@router.get("/list", response_model=JobListResponse)
async def list_jobs(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """List user's jobs"""
    jobs = await job_service.get_user_jobs(
        user_email=current_user["email"],
        limit=limit
    )
    return {"jobs": jobs, "total": len(jobs)}

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get job details"""
    job = await job_service.get_job(
        job_id=job_id,
        user_email=current_user["email"]
    )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job