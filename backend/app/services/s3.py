from app.core.aws import s3_client
from app.core.config import S3_BUCKET

def upload_file_to_s3(file, job_id: str) -> str:
    key = f"input/{job_id}/{file.filename}"

    s3_client.upload_fileobj(
        file.file,
        S3_BUCKET,
        key
    )

    return f"s3://{S3_BUCKET}/{key}"
