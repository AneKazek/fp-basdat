import re
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.models.schemas import ADDRESS_REGEX, DbTransaction, TransactionItem


def is_valid_address(address: str) -> bool:
    return re.fullmatch(ADDRESS_REGEX, address) is not None


def _to_iso(ts: str) -> str:
    dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def _wei_to_eth(value: str) -> float:
    return int(value) / 1e18


def to_transaction_items(items: List[Dict[str, Any]], wallet_address: str) -> List[TransactionItem]:
    sorted_items = sorted(items, key=lambda x: int(x.get("timeStamp", "0")), reverse=True)
    result: List[TransactionItem] = []
    for it in sorted_items[:500]:
        status = "success" if str(it.get("isError", "0")) == "0" else "failed"
        obj = TransactionItem(
            tx_hash=str(it.get("hash", "")),
            block_number=int(it.get("blockNumber", 0)),
            timestamp=_to_iso(str(it.get("timeStamp", "0"))),
            **{"from": str(it.get("from", ""))},
            **{"to": str(it.get("to", ""))},
            value_eth=_wei_to_eth(str(it.get("value", "0"))),
            status=status,
            gas_used=int(it.get("gasUsed", 0)),
        )
        result.append(obj)
    return result


def _direction(wallet: str, from_addr: str, to_addr: str) -> str:
    wl = wallet.lower()
    fa = from_addr.lower()
    ta = to_addr.lower()
    if fa == wl and ta == wl:
        return "self"
    if fa == wl:
        return "out"
    if ta == wl:
        return "in"
    return "self"


def to_db_row(item: TransactionItem, wallet_id: int, network_id: int, wallet_address: str) -> DbTransaction:
    gas_price = 0
    tx_fee_eth = 0.0
    direction = _direction(wallet_address, item.from_address, item.to_address)
    return DbTransaction(
        network_id=network_id,
        wallet_id=wallet_id,
        tx_hash=item.tx_hash,
        block_number=item.block_number,
        time_stamp=item.timestamp,
        from_address=item.from_address,
        to_address=item.to_address,
        value_eth=item.value_eth,
        gas_used=item.gas_used,
        tx_fee_eth=tx_fee_eth,
        direction=direction,
        status=item.status,
    )

