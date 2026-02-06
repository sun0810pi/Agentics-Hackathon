import json
from app.core.aws import sqs_client
from app.core.config import SQS_QUEUE_URL

def enqueue_job(payload: dict):
    sqs_client.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(payload)
    )
