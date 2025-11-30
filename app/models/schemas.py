from typing import List, Literal

from pydantic import BaseModel, Field


ADDRESS_REGEX = r"^0x[a-fA-F0-9]{40}$"


class TransactionItem(BaseModel):
    tx_hash: str
    block_number: int
    timestamp: str
    from_address: str = Field(alias="from")
    to_address: str = Field(alias="to")
    value_eth: float
    status: Literal["success", "failed"]
    gas_used: int

    model_config = {
        "populate_by_name": True,
    }


class Metadata(BaseModel):
    count: int
    wallet: str
    network: Literal["sepolia"]


class MonitorResponse(BaseModel):
    status: Literal["success", "error"]
    data: List[TransactionItem]
    metadata: Metadata

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success",
                    "data": [
                        {
                            "tx_hash": "0xabc",
                            "block_number": 123456,
                            "timestamp": "2025-11-27T12:00:00Z",
                            "from": "0x1111111111111111111111111111111111111111",
                            "to": "0x2222222222222222222222222222222222222222",
                            "value_eth": 0.001,
                            "status": "success",
                            "gas_used": 21000,
                        }
                    ],
                    "metadata": {
                        "count": 1,
                        "wallet": "0x1111111111111111111111111111111111111111",
                        "network": "sepolia",
                    },
                },
                {
                    "status": "error",
                    "data": [],
                    "metadata": {
                        "count": 0,
                        "wallet": "0xinvalid",
                        "network": "sepolia",
                    },
                },
            ]
        }
    }


class DbTransaction(BaseModel):
    network_id: int
    wallet_id: int
    tx_hash: str
    block_number: int
    time_stamp: str
    from_address: str
    to_address: str
    value_eth: float
    gas_used: int
    tx_fee_eth: float
    direction: Literal["in", "out", "self"]
    status: Literal["success", "failed"]

