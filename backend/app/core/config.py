import os

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")
S3_BUCKET = os.getenv("S3_BUCKET", "fintech-invoice-bucket")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL", "https://sqs.mock.amazonaws.com/123/queue")

ENV = os.getenv("ENV", "dev")
