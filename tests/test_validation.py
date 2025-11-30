from app.services.processor import is_valid_address


def test_valid_address():
    assert is_valid_address("0x" + "a" * 40)
    assert is_valid_address("0x" + "A" * 40)
    assert is_valid_address("0x1234567890abcdef1234567890abcdef12345678")


def test_invalid_address_prefix():
    assert not is_valid_address("1x" + "a" * 40)


def test_invalid_address_length():
    assert not is_valid_address("0x" + "a" * 39)
    assert not is_valid_address("0x" + "a" * 41)


def test_invalid_address_chars():
    assert not is_valid_address("0x" + "z" * 40)

