from redragon_monitor.battery.infrastructure.compx.compx_checksum import CompxChecksum
from redragon_monitor.battery.infrastructure.compx.compx_packet_layout import CompxPacketLayout as L


class CompxPowerQuery:
    def __init__(self, checksum: CompxChecksum):
        self._checksum = checksum

    def build(self) -> bytes:
        body = bytes([L.REPORT_ID, L.CMD_POWER]) + bytes(L.BODY_LEN - 2)
        return body + bytes([self._checksum.compute(body)])
