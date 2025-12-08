import asyncio
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add project root to python path
sys.path.append(os.getcwd())

from app.models.sql_models import Base, Wallet, Transaction, Network, User
from app.services.etherscan_client import EtherscanClient
from app.services.processor import to_transaction_items
from app.config import settings

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

ADDRESS = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" # Vitalik
NETWORK_NAME = "ethereum-mainnet"
CHAIN_ID = 1

async def debug_register():
    print(f"--- Debugging Registration for {ADDRESS} ---")
    
    # 1. Cleanup
    existing_wallet = db.query(Wallet).filter(Wallet.address == ADDRESS.lower()).first()
    if existing_wallet:
        print(f"Deleting existing wallet ID: {existing_wallet.wallet_id}")
        db.delete(existing_wallet)
        db.commit()
    
    # 2. Get/Create Network
    network = db.query(Network).filter(Network.chain_id == CHAIN_ID).first()
    if not network:
        print(f"Creating network {NETWORK_NAME}")
        network = Network(name=NETWORK_NAME, chain_id=CHAIN_ID, symbol_native="ETH")
        db.add(network)
        db.commit()
        db.refresh(network)
    else:
        print(f"Using network ID: {network.network_id}")

    # 3. Get/Create User
    user = db.query(User).filter(User.nama == "DebugUser").first()
    if not user:
        user = User(nama="DebugUser")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # 4. Create Wallet
    print("Creating wallet...")
    wallet = Wallet(
        user_id=user.user_id,
        network_id=network.network_id,
        address=ADDRESS.lower(),
        label="Debug Wallet"
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    print(f"Created Wallet ID: {wallet.wallet_id}")

    # 5. Fetch Etherscan
    print(f"Fetching Etherscan (Chain ID: {network.chain_id})...")
    client = EtherscanClient(settings.ETHERSCAN_API_KEY)
    try:
        resp = await client.get_txlist(ADDRESS, chain_id=network.chain_id)
        status = resp.get("status")
        message = resp.get("message")
        result = resp.get("result")
        print(f"Etherscan Response: status={status}, message={message}, result_type={type(result)}")
        
        if isinstance(result, list):
            print(f"Found {len(result)} raw transactions")
            
            tx_items = to_transaction_items(result, ADDRESS)
            print(f"Parsed {len(tx_items)} transaction items")
            
            count = 0
            for item in tx_items:
                # Check exist
                exists = db.query(Transaction).filter(
                    Transaction.tx_hash == item.tx_hash,
                    Transaction.wallet_id == wallet.wallet_id
                ).first()
                
                if exists:
                    print(f"Skipping existing: {item.tx_hash}")
                    continue
                
                direction = "self"
                if item.from_address.lower() == ADDRESS.lower():
                    direction = "out"
                elif item.to_address.lower() == ADDRESS.lower():
                    direction = "in"
                
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
                count += 1
            
            db.commit()
            print(f"Successfully inserted {count} transactions to DB")
            
            # 6. Verify DB
            count_db = db.query(Transaction).filter(Transaction.wallet_id == wallet.wallet_id).count()
            print(f"Final DB Count for Wallet {wallet.wallet_id}: {count_db}")
            
        else:
            print("Result is not a list!")
            
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_register())
