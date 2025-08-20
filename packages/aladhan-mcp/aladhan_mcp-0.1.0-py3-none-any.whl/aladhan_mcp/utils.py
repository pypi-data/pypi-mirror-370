import asyncio
import json
import time
from mcp.types import TextContent

ALADHAN_BASE = "https://api.aladhan.com/v1"


def text_json(obj) -> TextContent:
    """Convert object to JSON string and return as TextContent"""
    return TextContent(type="text", text=json.dumps(obj, ensure_ascii=False))


def text_content(text: str) -> TextContent:
    """Convert string to TextContent"""
    return TextContent(type="text", text=text)


_CACHE: dict[str, tuple[float, dict]] = {}


def cache_get(key: str, ttl_s: int = 86400):
    item = _CACHE.get(key)
    if not item:
        return None
    ts, val = item
    return val if (time.time() - ts) < ttl_s else None


def cache_put(key: str, val: dict):
    _CACHE[key] = (time.time(), val)


async def get_json(url: str, params: dict | None = None, timeout=15):
    # tiny retry with backoff
    for i in range(3):
        try:
            import httpx
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.get(url, params=params)
                r.raise_for_status()
                return r.json()
        except httpx.HTTPError:
            if i == 2:
                raise
            await asyncio.sleep(0.3 * (2 ** i))
