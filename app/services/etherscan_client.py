from typing import Any, Dict
import asyncio

import aiohttp

from app.config import settings


BASE_URL = "https://api.etherscan.io/v2/api"
CHAIN_ID = 11155111


class EtherscanClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_txlist(self, address: str) -> Dict[str, Any]:
        params = {
            "module": "account",
            "chainid": CHAIN_ID,
            "action": "txlist",
            "address": address,
            "sort": "desc",
            "apikey": self.api_key,
        }
        timeout = aiohttp.ClientTimeout(total=10)
        attempt = 0
        backoffs = [0.2, 0.5, 1.0]
        last_exc: Exception | None = None
        async with aiohttp.ClientSession(timeout=timeout) as session:
            while attempt < 3:
                attempt += 1
                try:
                    async with session.get(BASE_URL, params=params) as resp:
                        if 500 <= resp.status <= 599:
                            if attempt < 3:
                                await asyncio.sleep(backoffs[attempt - 1])
                                continue
                            return {"status": 0, "message": "SERVER_ERROR", "result": []}
                        data = await resp.json(content_type=None)
                        return data
                except Exception as exc:
                    last_exc = exc
                    if attempt < 3:
                        await asyncio.sleep(backoffs[attempt - 1])
                        continue
                    raise exc
        if last_exc is not None:
            raise last_exc
        return {"status": 0, "message": "UNKNOWN_ERROR", "result": []}

