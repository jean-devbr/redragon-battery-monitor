import pytest

from redragon_monitor.device.battery_protocol import (
    ProtocolError,
    build_power_query,
    checksum,
    is_power_response,
    parse_power_response,
)
from conftest import RESP_CHARGING, RESP_WIRELESS


def test_query_is_exactly_the_validated_packet():
    assert build_power_query().hex(" ") == "08 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 49"


def test_checksum_matches_real_responses():
    assert checksum(RESP_WIRELESS[:16]) == 0xAA
    assert checksum(RESP_CHARGING[:16]) == 0x7C


def test_parse_real_wireless_response():
    r = parse_power_response(RESP_WIRELESS)
    assert (r.percent, r.charging, r.voltage_mv) == (100, False, 4137)


def test_parse_real_charging_response():
    r = parse_power_response(RESP_CHARGING)
    assert (r.percent, r.charging, r.charging_raw, r.voltage_mv) == (95, True, 1, 4187)


def _with(pkt: bytes, idx: int, val: int, fix_checksum=True) -> bytes:
    b = bytearray(pkt)
    b[idx] = val
    if fix_checksum:
        b[16] = checksum(bytes(b[:16]))
    return bytes(b)


@pytest.mark.parametrize(
    "pkt",
    [
        _with(RESP_WIRELESS, 16, 0xAB, fix_checksum=False),  # checksum errado
        _with(RESP_WIRELESS, 2, 0x01),  # status de erro
        _with(RESP_WIRELESS, 6, 101),  # nível impossível
        _with(RESP_WIRELESS, 7, 3),  # flag desconhecida
        _with(RESP_WIRELESS, 1, 0x03),  # outro comando
        RESP_WIRELESS[:10],  # curta
    ],
)
def test_invalid_responses_are_rejected(pkt):
    with pytest.raises(ProtocolError):
        parse_power_response(pkt)


def test_is_power_response_ignores_mouse_reports():
    assert not is_power_response(bytes.fromhex("01 00 c0 00 0f 00 00 00"))
    assert is_power_response(RESP_WIRELESS)
