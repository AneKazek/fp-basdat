from app.services.processor import to_transaction_items


def _make_item(ts: int, value_wei: int, is_error: str = "0"):
    return {
        "hash": f"0x{ts:x}",
        "blockNumber": str(100000 + ts),
        "timeStamp": str(ts),
        "from": "0x1111111111111111111111111111111111111111",
        "to": "0x2222222222222222222222222222222222222222",
        "value": str(value_wei),
        "gasUsed": "21000",
        "isError": is_error,
    }


def test_transform_limit_and_sort():
    items = [_make_item(ts, ts * 10) for ts in range(1, 61)]
    res = to_transaction_items(items, "0x1111111111111111111111111111111111111111")
    assert len(res) == 60
    assert res[0].block_number > res[-1].block_number


def test_transform_limit_500():
    items = [_make_item(ts, ts * 10) for ts in range(1, 601)]
    res = to_transaction_items(items, "0x1111111111111111111111111111111111111111")
    assert len(res) == 500


def test_wei_to_eth_and_status():
    items = [_make_item(100, 1000000000000000000, "0"), _make_item(99, 500000000000000000, "1")]
    res = to_transaction_items(items, "0x1111111111111111111111111111111111111111")
    assert res[0].value_eth == 1.0
    assert res[0].status == "success"
    assert res[1].value_eth == 0.5
    assert res[1].status == "failed"

