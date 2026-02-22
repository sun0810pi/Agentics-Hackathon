"""backend/services/aws_service.py — AWS service wrappers (Textract, Bedrock, S3)"""
import os, logging
logger = logging.getLogger(__name__)

async def textract_analyze(file_bytes: bytes) -> dict:
    """Analyze document with Textract. Returns raw blocks."""
    try:
        import boto3
        client = boto3.client("textract", region_name=os.getenv("AWS_REGION","us-east-1"))
        return client.analyze_document(Document={"Bytes":file_bytes}, FeatureTypes=["TABLES","FORMS"])
    except Exception as e:
        logger.error(f"Textract error: {e}"); return {"Blocks":[]}

async def bedrock_invoke(prompt: str, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0") -> str:
    """Invoke Bedrock model. Returns response text."""
    try:
        import boto3, json
        client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION","us-east-1"))
        resp = client.invoke_model(
            modelId=model_id,
            body=json.dumps({"anthropic_version":"bedrock-2023-05-31","max_tokens":512,
                             "messages":[{"role":"user","content":prompt}]}),
            contentType="application/json", accept="application/json",
        )
        return json.loads(resp["body"].read())["content"][0]["text"]
    except Exception as e:
        logger.error(f"Bedrock error: {e}"); return ""
