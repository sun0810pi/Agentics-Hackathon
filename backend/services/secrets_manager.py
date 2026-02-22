"""backend/services/secrets_manager.py"""
import boto3, json, logging, os
from functools import lru_cache
logger = logging.getLogger(__name__)

@lru_cache(maxsize=32)
def _fetch_sync(name: str, region: str) -> str:
    return boto3.client("secretsmanager", region_name=region).get_secret_value(SecretId=name).get("SecretString","")

async def get_secret(name: str) -> str:
    try: return _fetch_sync(name, os.getenv("AWS_REGION","us-east-1"))
    except Exception as e: logger.error(f"Secret '{name}': {e}"); raise

async def get_secret_json(name: str) -> dict:
    return json.loads(await get_secret(name))
