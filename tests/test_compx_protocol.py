import pytest

from redragon_monitor.domain.protocol_error import ProtocolError
from redragon_monitor.infrastructure.compx.compx_battery_protocol import CompxBatteryProtocol
from redragon_monitor.infrastructure.compx.compx_checksum import CompxChecksum
from redragon_monitor.infrastructure.compx.compx_power_query import CompxPowerQuery
from redragon_monitor.infrastructure.compx.compx_power_response_parser import CompxPowerResponseParser
from conftest import RESP_CHARGING, RESP_WIRELESS

CHECKSUM = CompxChecksum()
PROTOCOL = CompxBatteryProtocol(CompxPowerQuery(CHECKSUM), CompxPowerResponseParser(CHECKSUM))
VALIDATED_QUERY = "08 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 49"


def test_query_is_exactly_the_validated_packet():
    assert PROTOCOL.build_query().hex(" ") == VALIDATED_QUERY


def test_checksum_matches_real_responses():
    assert CHECKSUM.compute(RESP_WIRELESS[:16]) == 0xAA
    assert CHECKSUM.compute(RESP_CHARGING[:16]) == 0x7C


def test_checksum_requires_16_bytes():
    with pytest.raises(ValueError):
        CHECKSUM.compute(bytes(15))


def test_parse_real_wireless_response():
    reading = PROTOCOL.parse(RESP_WIRELESS)
    assert (reading.percent, reading.charging, reading.voltage_mv) == (100, False, 4137)


def test_parse_real_charging_response():
    reading = PROTOCOL.parse(RESP_CHARGING)
    assert (reading.percent, reading.charging, reading.charging_raw, reading.voltage_mv) == (95, True, 1, 4187)


def _with(packet: bytes, index: int, value: int, fix_checksum: bool = True) -> bytes:
    data = bytearray(packet)
    data[index] = value
    data[16] = CHECKSUM.compute(bytes(data[:16])) if fix_checksum else data[16]
    return bytes(data)


@pytest.mark.parametrize(
    "packet",
    [
        _with(RESP_WIRELESS, 16, 0xAB, fix_checksum=False),
        _with(RESP_WIRELESS, 2, 0x01),
        _with(RESP_WIRELESS, 6, 101),
        _with(RESP_WIRELESS, 7, 3),
        _with(RESP_WIRELESS, 1, 0x03),
        RESP_WIRELESS[:10],
    ],
)
def test_invalid_responses_are_rejected(packet):
    with pytest.raises(ProtocolError):
        PROTOCOL.parse(packet)


def test_is_response_ignores_mouse_reports():
    assert not PROTOCOL.is_response(bytes.fromhex("01 00 c0 00 0f 00 00 00"))
    assert PROTOCOL.is_response(RESP_WIRELESS)
