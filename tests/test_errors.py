import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.routers.monitor import monitor_wallet
from app.services.etherscan_client import EtherscanClient


class DummyError(Exception):
    pass


def test_network_error(monkeypatch):
    async def _fail(self, address: str):
        raise DummyError("network")

    monkeypatch.setattr(EtherscanClient, "get_txlist", _fail)
    client = TestClient(app)
    r = client.get("/monitor/wallet", params={"address": "0x1111111111111111111111111111111111111111"})
    assert r.status_code == 502
    body = r.json()
    assert body["status"] == "error"


def test_rate_limit_response(monkeypatch):
    async def _rl(self, address: str):
        return {"status": 0, "message": "NOTOK", "result": "Max rate limit reached"}

    monkeypatch.setattr(EtherscanClient, "get_txlist", _rl)
    client = TestClient(app)
    r = client.get("/monitor/wallet", params={"address": "0x1111111111111111111111111111111111111111"})
    assert r.status_code == 503
    body = r.json()
    assert body["status"] == "error"

