from __future__ import annotations

from dataclasses import dataclass

REPORT_ID = 0x08
PACKET_LEN = 17
CHECKSUM_MAGIC = 0x55
CMD_POWER = 0x04

STATUS_OK = 0x00
MAX_PERCENT = 100
MAX_CHARGING_FLAG = 2


class ProtocolError(ValueError):
    pass


@dataclass(frozen=True)
class BatteryReading:
    percent: int
    charging: bool
    charging_raw: int
    voltage_mv: int
    raw: bytes


def checksum(first16: bytes) -> int:
    if len(first16) != PACKET_LEN - 1:
        raise ValueError("checksum exige exatamente 16 bytes")
    return (CHECKSUM_MAGIC - sum(first16)) & 0xFF


def build_power_query() -> bytes:
    body = bytes([REPORT_ID, CMD_POWER]) + bytes(PACKET_LEN - 3)
    return body + bytes([checksum(body)])


def is_power_response(data: bytes) -> bool:
    return len(data) >= 2 and data[0] == REPORT_ID and data[1] == CMD_POWER


def parse_power_response(data: bytes) -> BatteryReading:
    if len(data) < PACKET_LEN:
        raise ProtocolError(f"resposta curta: {len(data)} bytes")
    pkt = bytes(data[:PACKET_LEN])
    if not is_power_response(pkt):
        raise ProtocolError(f"não é resposta ao comando 0x04: {pkt[:2].hex(' ')}")
    if checksum(pkt[:16]) != pkt[16]:
        raise ProtocolError(f"checksum inválido: {pkt.hex(' ')}")
    if pkt[2] != STATUS_OK:
        raise ProtocolError(f"status de erro 0x{pkt[2]:02x}")
    percent, flag = pkt[6], pkt[7]
    if percent > MAX_PERCENT:
        raise ProtocolError(f"nível fora da faixa: {percent}")
    if flag > MAX_CHARGING_FLAG:
        raise ProtocolError(f"indicador de carga desconhecido: {flag}")
    return BatteryReading(
        percent=percent,
        charging=flag == 1,
        charging_raw=flag,
        voltage_mv=(pkt[8] << 8) | pkt[9],
        raw=pkt,
    )
