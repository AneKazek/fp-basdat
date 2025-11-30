from typing import List

import structlog
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.schemas import Metadata, MonitorResponse, TransactionItem
from app.rate_limit import limiter
from app.services.etherscan_client import EtherscanClient
from app.services.processor import is_valid_address, to_transaction_items


router = APIRouter(prefix="/monitor")
logger = structlog.get_logger()


@router.get("/wallet", response_model=MonitorResponse)
@limiter.limit(settings.rate_limit_str())
async def monitor_wallet(request: Request, address: str):
    if not is_valid_address(address):
        payload = MonitorResponse(
            status="error",
            data=[],
            metadata=Metadata(count=0, wallet=address, network="sepolia"),
        )
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=payload.model_dump(by_alias=True))
    client = EtherscanClient(settings.ETHERSCAN_API_KEY)
    try:
        resp = await client.get_txlist(address)
    except Exception as exc:
        logger.error("etherscan_call_failed", wallet=address, error=str(exc))
        payload = MonitorResponse(
            status="error",
            data=[],
            metadata=Metadata(count=0, wallet=address, network="sepolia"),
        )
        return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=payload.model_dump(by_alias=True))

    if str(resp.get("status", "0")) != "1":
        msg = str(resp.get("message", "")) or str(resp.get("result", ""))
        if "No transactions found" in msg:
            payload = MonitorResponse(
                status="success",
                data=[],
                metadata=Metadata(count=0, wallet=address, network="sepolia"),
            )
            return JSONResponse(status_code=status.HTTP_200_OK, content=payload.model_dump(by_alias=True))
        if "Max rate limit" in msg:
            logger.warning("etherscan_rate_limited", wallet=address)
        payload = MonitorResponse(
            status="error",
            data=[],
            metadata=Metadata(count=0, wallet=address, network="sepolia"),
        )
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=payload.model_dump(by_alias=True))

    raw_list: List[dict] = resp.get("result", [])
    items: List[TransactionItem] = to_transaction_items(raw_list, address)
    payload = MonitorResponse(
        status="success",
        data=items,
        metadata=Metadata(count=len(items), wallet=address, network="sepolia"),
    )
    logger.info("monitor_wallet_success", wallet=address, count=len(items))
    return JSONResponse(status_code=status.HTTP_200_OK, content=payload.model_dump(by_alias=True))

