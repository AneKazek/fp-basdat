from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sql_models import Network, User, Wallet, Transaction
from app.services.processor import is_valid_address


router = APIRouter(prefix="/wallet", tags=["wallet-tracker"])


def _fmt_dt(dt: datetime) -> str:
    return dt.isoformat()


def _get_eth_network(db: Session) -> Network:
    net = db.query(Network).order_by(Network.network_id.asc()).first()
    if not net:
        raise HTTPException(status_code=500, detail="Network data not found")
    return net


@router.get("/{address}")
def get_wallet_info(address: str, db: Session = Depends(get_db), page: int = Query(1, ge=1), pageSize: int = Query(20, ge=1, le=100)):
    addr = address.strip()
    if not is_valid_address(addr):
        raise HTTPException(status_code=400, detail="Alamat Ethereum tidak valid (harus 0x dan 42 karakter)")

    network = _get_eth_network(db)

    wallet: Optional[Wallet] = (
        db.query(Wallet)
        .filter(Wallet.network_id == network.network_id)
        .filter(Wallet.address == addr.lower())
        .first()
    )

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet tidak ditemukan di database")

    owner: Optional[User] = db.query(User).filter(User.user_id == wallet.user_id).first()

    q = (
        db.query(Transaction)
        .filter(Transaction.wallet_id == wallet.wallet_id)
        .filter(Transaction.network_id == network.network_id)
        .order_by(Transaction.time_stamp.desc())
    )
    total = q.count()
    items: List[Transaction] = q.offset((page - 1) * pageSize).limit(pageSize).all()

    tx_list = [
        {
            "tx_hash": t.tx_hash,
            "block_number": t.block_number,
            "time_stamp": _fmt_dt(t.time_stamp),
            "from_address": t.from_address,
            "to_address": t.to_address,
            "value_eth": float(t.value_eth or 0),
            "tx_fee_eth": float(t.tx_fee_eth or 0),
            "direction": t.direction.value if hasattr(t.direction, "value") else t.direction,
            "status": t.status,
        }
        for t in items
    ]

    return {
        "wallet": {
            "wallet_id": wallet.wallet_id,
            "address": wallet.address,
            "label": wallet.label,
            "owner_name": owner.nama if owner else None,
            "network_name": network.name,
        },
        "transactions": {
            "page": page,
            "pageSize": pageSize,
            "total": total,
            "items": tx_list,
        },
    }


@router.get("/{address}/transactions")
def get_wallet_transactions(address: str, db: Session = Depends(get_db), page: int = Query(1, ge=1), pageSize: int = Query(20, ge=1, le=100)):
    addr = address.strip()
    if not is_valid_address(addr):
        raise HTTPException(status_code=400, detail="Alamat Ethereum tidak valid (harus 0x dan 42 karakter)")

    network = _get_eth_network(db)

    wallet: Optional[Wallet] = (
        db.query(Wallet)
        .filter(Wallet.network_id == network.network_id)
        .filter(Wallet.address == addr.lower())
        .first()
    )

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet tidak ditemukan di database")

    q = (
        db.query(Transaction)
        .filter(Transaction.wallet_id == wallet.wallet_id)
        .filter(Transaction.network_id == network.network_id)
        .order_by(Transaction.time_stamp.desc())
    )
    total = q.count()
    items: List[Transaction] = q.offset((page - 1) * pageSize).limit(pageSize).all()

    tx_list = [
        {
            "tx_hash": t.tx_hash,
            "block_number": t.block_number,
            "time_stamp": _fmt_dt(t.time_stamp),
            "from_address": t.from_address,
            "to_address": t.to_address,
            "value_eth": float(t.value_eth or 0),
            "tx_fee_eth": float(t.tx_fee_eth or 0),
            "direction": t.direction.value if hasattr(t.direction, "value") else t.direction,
            "status": t.status,
        }
        for t in items
    ]

    return {
        "page": page,
        "pageSize": pageSize,
        "total": total,
        "items": tx_list,
    }

