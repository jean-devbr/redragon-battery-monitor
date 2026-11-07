from dataclasses import dataclass, field

from redragon_monitor.device.domain.connection_type import ConnectionType


@dataclass(frozen=True)
class DeviceSpec:
    name: str
    vendor_id: int
    connections: dict[int, ConnectionType] = field(default_factory=dict)
    usage_page: int = 0
    report_id: int = 0
    report_bytes: int = 0

    def supports(self, vendor_id: int, product_id: int) -> bool:
        return vendor_id == self.vendor_id and product_id in self.connections

    def preference(self, product_id: int) -> int:
        return list(self.connections).index(product_id)
