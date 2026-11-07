from dataclasses import dataclass

from redragon_monitor.device.domain.connection_type import ConnectionType


@dataclass(frozen=True)
class DeviceInterface:
    pid: int
    connection: ConnectionType
    hidraw_path: str
    sysfs_path: str
