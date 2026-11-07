from redragon_monitor.battery.infrastructure.compx.compx_packet_layout import CompxPacketLayout as L


class CompxChecksum:
    def compute(self, body: bytes) -> int:
        if len(body) != L.BODY_LEN:
            raise ValueError(f"checksum exige exatamente {L.BODY_LEN} bytes")
        return (L.CHECKSUM_MAGIC - sum(body)) & 0xFF

    def is_valid(self, packet: bytes) -> bool:
        return self.compute(packet[: L.BODY_LEN]) == packet[L.INDEX_CHECKSUM]
