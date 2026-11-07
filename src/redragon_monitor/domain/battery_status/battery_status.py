from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from redragon_monitor.domain.battery_reading import BatteryReading
from redragon_monitor.domain.device_interface import DeviceInterface
from redragon_monitor.domain.read_status import ReadStatus


@dataclass(frozen=True)
class BatteryStatus:
    status: ReadStatus
    timestamp: datetime
    reading: Optional[BatteryReading] = None
    interface: Optional[DeviceInterface] = None
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.status is ReadStatus.OK and self.reading is not None
