from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Enum, BigInteger, CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base

class DirectionEnum(enum.Enum):
    in_ = "in"
    out = "out"
    self = "self"

class Network(Base):
    __tablename__ = "network"

    network_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    chain_id = Column(Integer, nullable=False, unique=True)
    symbol_native = Column(String(10), default="eth")
    explorer_url = Column(String(200))
    api_base_url = Column(String(200))

    wallets = relationship("Wallet", back_populates="network")
    transactions = relationship("Transaction", back_populates="network")
    sync_logs = relationship("SyncLog", back_populates="network")

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nrp = Column(String(20), unique=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100))
    created_at = Column(DateTime, default=func.now())

    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")

class Wallet(Base):
    __tablename__ = "wallet"

    wallet_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    network_id = Column(Integer, ForeignKey("network.network_id"), nullable=False)
    address = Column(CHAR(42), nullable=False)
    label = Column(String(100), default="main wallet")
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="wallets")
    network = relationship("Network", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet", cascade="all, delete-orphan")
    sync_logs = relationship("SyncLog", back_populates="wallet", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transaction"

    tx_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    network_id = Column(Integer, ForeignKey("network.network_id"), nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallet.wallet_id", ondelete="CASCADE"), nullable=False)
    tx_hash = Column(CHAR(66), nullable=False, index=True)
    block_number = Column(BigInteger, nullable=False)
    time_stamp = Column(DateTime, nullable=False, index=True)
    from_address = Column(CHAR(42), nullable=False)
    to_address = Column(CHAR(42))
    value_eth = Column(DECIMAL(38, 18), default=0)
    gas_used = Column(BigInteger, default=0)
    tx_fee_eth = Column(DECIMAL(38, 18), default=0)
    direction = Column(Enum(DirectionEnum), nullable=False)
    status = Column(String(20), default="success")

    network = relationship("Network", back_populates="transactions")
    wallet = relationship("Wallet", back_populates="transactions")

class SyncLog(Base):
    __tablename__ = "sync_log"

    sync_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    wallet_id = Column(Integer, ForeignKey("wallet.wallet_id", ondelete="CASCADE"), nullable=False)
    network_id = Column(Integer, ForeignKey("network.network_id"), nullable=False)
    synced_at = Column(DateTime, default=func.now())
    from_block = Column(BigInteger)
    to_block = Column(BigInteger)
    new_tx_count = Column(Integer, default=0)
    status = Column(String(50), default="success")

    wallet = relationship("Wallet", back_populates="sync_logs")
    network = relationship("Network", back_populates="sync_logs")
