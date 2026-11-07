from typing import Optional

from redragon_monitor.battery.domain.battery_status import BatteryStatus
from redragon_monitor.presentation.text.status_text_formatter import StatusTextFormatter


class WatchLineFormatter:
    def __init__(self, text: StatusTextFormatter):
        self._text = text

    def format(self, status: BatteryStatus, last_good: Optional[BatteryStatus]) -> str:
        time = f"[{status.timestamp:%H:%M:%S}]"
        if status.ok:
            reading = status.reading
            flag = " ⚡" if reading.charging else ""
            return f"{time} {reading.percent:3d}%{flag}  {reading.voltage_mv} mV  ({status.interface.connection.value})"
        if last_good is None or not last_good.ok:
            return f"{time} {self._text.message(status)}"
        return (
            f"{time} {self._text.message(status)}"
            f"  [última: {last_good.reading.percent}% às {last_good.timestamp:%H:%M:%S}]"
        )
