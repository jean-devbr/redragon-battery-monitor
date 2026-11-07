from typing import Optional

from redragon_monitor.battery.domain.battery_status import BatteryStatus
from redragon_monitor.presentation.text.status_text_formatter import StatusTextFormatter


class WatchLineFormatter:
    def __init__(self, text: StatusTextFormatter):
        self._text = text

    def format(self, status: BatteryStatus, last_good: Optional[BatteryStatus]) -> str:
        time = f"[{self._text.time(status)}]"
        if status.ok:
            reading = status.reading
            flag = " ⚡" if reading.charging else ""
            connection = self._text.connection_label(status)
            return f"{time} {reading.percent:3d}%{flag}  {reading.voltage_mv} mV  ({connection})"
        if last_good is None or not last_good.ok:
            return f"{time} {self._text.message(status)}"
        last = self._text.t("cli.watch_last", percent=last_good.reading.percent, time=self._text.time(last_good))
        return f"{time} {self._text.message(status)}  {last}"
