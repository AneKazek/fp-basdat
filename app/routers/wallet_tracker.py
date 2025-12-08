from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sql_models import Network, User, Wallet, Transaction, DirectionEnum
from app.models.schemas import WalletRegisterRequest
from app.services.processor import is_valid_address, to_transaction_items
from app.services.etherscan_client import EtherscanClient
from app.config import settings
from app.rate_limit import limiter
import random


router = APIRouter(prefix="/wallet", tags=["wallet-tracker"])


def _fmt_dt(dt: datetime) -> str:
    return dt.isoformat()


def _get_eth_network(db: Session) -> Network:
    net = db.query(Network).order_by(Network.network_id.asc()).first()
    if not net:
        raise HTTPException(status_code=500, detail="Network data not found")
    return net


NETWORK_CHAIN_IDS = {
    "ethereum-mainnet": 1,
    "sepolia-testnet": 11155111,
    "sepolia": 11155111,
    "goerli-testnet": 5,
    "goerli": 5,
    "polygon-mainnet": 137,
    "polygon-mumbai": 80001,
    "bsc-mainnet": 56,
    "bsc-testnet": 97,
}


@router.post("/register")
@limiter.limit(settings.rate_limit_str())
async def register_wallet(request: Request, data: WalletRegisterRequest, db: Session = Depends(get_db)):
    # Validate address
    if not is_valid_address(data.address):
        raise HTTPException(status_code=400, detail="Alamat Ethereum tidak valid")
    
    # Determine Chain ID
    # Try exact match, then lowercase
    chain_id = NETWORK_CHAIN_IDS.get(data.network)
    if not chain_id:
        chain_id = NETWORK_CHAIN_IDS.get(data.network.lower())
    
    if not chain_id:
        # Default to Sepolia if unknown
        chain_id = 11155111

    # Find or Create Network
    # 1. Check by Chain ID (Primary Source of Truth)
    network = db.query(Network).filter(Network.chain_id == chain_id).first()
    
    if not network:
        # 2. If not found by Chain ID, check by Name
        # If name exists but has different Chain ID, we use that network (trusting DB over input/default)
        existing_name_net = db.query(Network).filter(Network.name == data.network).first()
        if existing_name_net:
            network = existing_name_net
        else:
            # Create new network
            network = Network(name=data.network, chain_id=chain_id, symbol_native="ETH")
            db.add(network)
            db.commit()
            db.refresh(network)
    
    # Upsert User
    user = db.query(User).filter(User.nama == data.owner_name).first()
    if not user:
        user = User(nama=data.owner_name)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Upsert Wallet
    wallet = db.query(Wallet).filter(Wallet.address == data.address, Wallet.network_id == network.network_id).first()
    if not wallet:
        wallet = Wallet(user_id=user.user_id, network_id=network.network_id, address=data.address, label=data.label)
        db.add(wallet)
    else:
        wallet.label = data.label
        wallet.user_id = user.user_id 
        db.add(wallet) # Ensure update is tracked
    
    db.commit()
    db.refresh(wallet)
    
    # Fetch Etherscan
    print(f"[Register] Fetching Etherscan for {data.address} on chain {network.chain_id}...")
    client = EtherscanClient(settings.ETHERSCAN_API_KEY)
    try:
        # Pass the network's chain_id to Etherscan client
        resp = await client.get_txlist(data.address, chain_id=network.chain_id)
    except Exception as e:
        # If fetch fails, we still return success for wallet creation, but warn?
        # Or fail? Let's just log and continue, maybe raise HTTP 500 if critical.
        # User said "fetch walletnya ... di upsert". Implies it's part of the process.
        print(f"Etherscan error: {e}")
        resp = {} # Empty response
        
    raw_list = resp.get("result", [])
    if isinstance(raw_list, list):
        tx_items = to_transaction_items(raw_list, data.address)
        print(f"[Register] Found {len(tx_items)} transactions from Etherscan.")
        
        count_added = 0
        for item in tx_items:
            # Check if tx exists for THIS wallet
            existing_tx = db.query(Transaction).filter(
                Transaction.tx_hash == item.tx_hash,
                Transaction.wallet_id == wallet.wallet_id
            ).first()
            
            if existing_tx:
                continue
                
            # Convert direction
            direction = DirectionEnum.self
            if item.from_address.lower() == data.address.lower() and item.to_address.lower() == data.address.lower():
                direction = DirectionEnum.self
            elif item.from_address.lower() == data.address.lower():
                direction = DirectionEnum.out
            elif item.to_address.lower() == data.address.lower():
                direction = DirectionEnum.in_
                
            new_tx = Transaction(
                network_id=network.network_id,
                wallet_id=wallet.wallet_id,
                tx_hash=item.tx_hash,
                block_number=item.block_number,
                time_stamp=datetime.fromisoformat(item.timestamp.replace("Z", "+00:00")),
                from_address=item.from_address,
                to_address=item.to_address,
                value_eth=item.value_eth,
                gas_used=item.gas_used,
                tx_fee_eth=0,
                direction=direction,
                status=item.status
            )
            db.add(new_tx)
            count_added += 1
        
        db.commit()
        print(f"[Register] Successfully added {count_added} new transactions.")
    else:
        print(f"[Register] Etherscan result is not a list: {raw_list}")
        count_added = 0

    return {
        "status": "success", 
        "wallet_id": wallet.wallet_id, 
        "address": wallet.address,
        "transactions_fetched": len(raw_list) if isinstance(raw_list, list) else 0,
        "transactions_added": count_added
    }


@router.get("/{address}")
async def get_wallet_info(address: str, db: Session = Depends(get_db), page: int = Query(1, ge=1), pageSize: int = Query(20, ge=1, le=100)):
    addr = address.strip()
    if not is_valid_address(addr):
        raise HTTPException(status_code=400, detail="Alamat Ethereum tidak valid (harus 0x dan 42 karakter)")

    # Try to find wallet by address directly (across any network)
    print(f"[GetInfo] Searching for wallet address: {addr}")
    wallet: Optional[Wallet] = (
        db.query(Wallet)
        .filter(Wallet.address == addr.lower())
        .order_by(Wallet.wallet_id.desc())
        .first()
    )

    if wallet:
        print(f"[GetInfo] Found wallet ID: {wallet.wallet_id} on network ID: {wallet.network_id}")
        network = db.query(Network).filter(Network.network_id == wallet.network_id).first()
    else:
        print(f"[GetInfo] Wallet not found in DB. Attempting fallback...")
        # Fallback: use default network (or first available)
        network = _get_eth_network(db)
        
        # Fallback: Try to fetch from Etherscan and auto-import
        client = EtherscanClient(settings.ETHERSCAN_API_KEY)
        try:
            resp = await client.get_txlist(addr, chain_id=network.chain_id)
        except Exception as e:
            # Only raise 404 if fetch also fails
            print(f"Etherscan fetch failed for {addr}: {e}")
            raise HTTPException(status_code=404, detail="Wallet tidak ditemukan di database dan gagal fetch dari Etherscan")
        
        raw_list = resp.get("result", [])
        if not isinstance(raw_list, list) or len(raw_list) == 0:
             # If no data found on Etherscan either, raise 404
             # But wait, maybe it's a valid wallet with 0 transactions?
             # For now, let's treat it as "New Wallet" and register it if Etherscan call was successful (status 1 or 0 with "No transactions found")
             # Actually, Etherscan returns "No transactions found" with status 0.
             msg = str(resp.get("message", ""))
             if "No transactions found" not in msg and str(resp.get("status", "0")) != "1":
                 raise HTTPException(status_code=404, detail="Wallet tidak ditemukan di database dan Etherscan")

        # Auto-create User (Unknown/Auto)
        user = db.query(User).filter(User.nama == "Auto-Detected Owner").first()
        if not user:
            user = User(nama="Auto-Detected Owner")
            db.add(user)
            db.commit()
            db.refresh(user)

        # Auto-create Wallet
        wallet = Wallet(
            user_id=user.user_id, 
            network_id=network.network_id, 
            address=addr.lower(), 
            label="Auto-Imported Wallet"
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        
        # Upsert Transactions
        if isinstance(raw_list, list):
            tx_items = to_transaction_items(raw_list, addr)
            for item in tx_items:
                direction = DirectionEnum.self
                if item.from_address.lower() == addr.lower() and item.to_address.lower() == addr.lower():
                    direction = DirectionEnum.self
                elif item.from_address.lower() == addr.lower():
                    direction = DirectionEnum.out
                elif item.to_address.lower() == addr.lower():
                    direction = DirectionEnum.in_
                
                new_tx = Transaction(
                    network_id=network.network_id,
                    wallet_id=wallet.wallet_id,
                    tx_hash=item.tx_hash,
                    block_number=item.block_number,
                    time_stamp=datetime.fromisoformat(item.timestamp.replace("Z", "+00:00")),
                    from_address=item.from_address,
                    to_address=item.to_address,
                    value_eth=item.value_eth,
                    gas_used=item.gas_used,
                    tx_fee_eth=0,
                    direction=direction,
                    status=item.status
                )
                db.add(new_tx)
            db.commit()

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

    wallet: Optional[Wallet] = (
        db.query(Wallet)
        .filter(Wallet.address == addr.lower())
        .order_by(Wallet.wallet_id.desc())
        .first()
    )

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet tidak ditemukan di database")

    network = db.query(Network).filter(Network.network_id == wallet.network_id).first()
    if not network:
        raise HTTPException(status_code=500, detail="Network data inconsistent")

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

