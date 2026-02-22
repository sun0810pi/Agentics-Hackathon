"""
backend/services/secrets_manager.py
=====================================
Fetch secrets from AWS Secrets Manager.
NEVER hardcode secrets in code!
"""

import boto3
import json
import logging
import os
from typing import Any
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=32)
def _get_cached_secret(secret_name: str, region: str) -> str:
    """Cached synchronous secret fetch (for startup)."""
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    return response.get("SecretString", "")


async def get_secret(secret_name: str) -> str:
    """
    Fetch a secret from AWS Secrets Manager.
    Uses sync boto3 (Lambda doesn't need async for this).
    """
    region = os.getenv("AWS_REGION", "us-east-1")
    try:
        return _get_cached_secret(secret_name, region)
    except Exception as e:
        logger.error(f"Failed to get secret '{secret_name}': {e}")
        raise


async def get_secret_json(secret_name: str) -> dict:
    """Fetch and parse a JSON secret."""
    raw = await get_secret(secret_name)
    return json.loads(raw)
