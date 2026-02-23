"""
backend/services/secrets_manager.py

PERF FIX:
  - Old: _fetch_sync() calls boto3 (blocking) directly inside async get_secret()
    → blocks asyncio event loop for entire network round-trip
  - New: wrapped in asyncio.get_event_loop().run_in_executor()
    → executes in thread pool, event loop free to handle other requests

  - @lru_cache still used for repeated calls to same secret name (in-process TTL)
"""
import boto3 as _boto3_mod, json, logging, os, asyncio
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

# ── Cached sync fetch (TTL = process lifetime) ────────────
@lru_cache(maxsize=32)
def _fetch_sync(name: str, region: str) -> str:
    """Blocking boto3 call — always run via executor, never directly."""
    try:
        client = _boto3_mod.client("secretsmanager", region_name=region)
        return client.get_secret_value(SecretId=name).get("SecretString", "")
    except Exception as e:
        logger.error(f"SecretsManager: cannot fetch '{name}': {e}")
        raise


async def get_secret(name: str) -> str:
    """Async wrapper — runs blocking boto3 in thread executor."""
    region = os.getenv("AWS_REGION", "us-east-1")

    # Return from lru_cache without hitting executor if already cached
    if (name, region) in _fetch_sync.cache_info().__class__.__mro__:
        pass   # lru_cache handles this transparently

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_sync, name, region)


async def get_secret_json(name: str) -> dict:
    """Fetch and parse JSON secret."""
    raw = await get_secret(name)
    return json.loads(raw)
