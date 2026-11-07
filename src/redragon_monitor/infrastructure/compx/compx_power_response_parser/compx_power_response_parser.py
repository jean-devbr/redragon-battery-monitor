from redragon_monitor.domain.battery_reading import BatteryReading
from redragon_monitor.domain.protocol_error import ProtocolError
from redragon_monitor.infrastructure.compx.compx_checksum import CompxChecksum
from redragon_monitor.infrastructure.compx.compx_packet_layout import CompxPacketLayout as L


class CompxPowerResponseParser:
    def __init__(self, checksum: CompxChecksum):
        self._checksum = checksum

    def is_response(self, data: bytes) -> bool:
        return len(data) > L.INDEX_COMMAND and data[L.INDEX_REPORT_ID] == L.REPORT_ID and data[L.INDEX_COMMAND] == L.CMD_POWER

    def parse(self, data: bytes) -> BatteryReading:
        if len(data) < L.PACKET_LEN:
            raise ProtocolError(f"resposta curta: {len(data)} bytes")
        packet = bytes(data[: L.PACKET_LEN])
        self._validate(packet)
        flag = packet[L.INDEX_CHARGING]
        return BatteryReading(
            percent=packet[L.INDEX_PERCENT],
            charging=flag == L.CHARGING_FLAG,
            charging_raw=flag,
            voltage_mv=(packet[L.INDEX_VOLTAGE_HIGH] << 8) | packet[L.INDEX_VOLTAGE_LOW],
            raw=packet,
        )

    def _validate(self, packet: bytes) -> None:
        if not self.is_response(packet):
            raise ProtocolError(f"não é resposta ao comando 0x04: {packet[:2].hex(' ')}")
        if not self._checksum.is_valid(packet):
            raise ProtocolError(f"checksum inválido: {packet.hex(' ')}")
        if packet[L.INDEX_STATUS] != L.STATUS_OK:
            raise ProtocolError(f"status de erro 0x{packet[L.INDEX_STATUS]:02x}")
        if packet[L.INDEX_PERCENT] > L.MAX_PERCENT:
            raise ProtocolError(f"nível fora da faixa: {packet[L.INDEX_PERCENT]}")
        if packet[L.INDEX_CHARGING] > L.MAX_CHARGING_FLAG:
            raise ProtocolError(f"indicador de carga desconhecido: {packet[L.INDEX_CHARGING]}")
