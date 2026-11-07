from typing import Optional

from redragon_monitor.battery.domain.battery_status import BatteryStatus
from redragon_monitor.presentation.text.status_text_formatter import StatusTextFormatter


class HumanStatusFormatter:
    def __init__(self, text: StatusTextFormatter):
        self._text = text

    def format(self, status: BatteryStatus, last_good: Optional[BatteryStatus] = None) -> str:
        if status.ok:
            return self._reading(status)
        lines = [self._text.message(status)]
        if status.detail:
            lines.append(self._text.t("cli.detail", detail=status.detail))
        if last_good is not None and last_good.ok:
            lines.append(
                self._text.t("cli.last_good", percent=last_good.reading.percent, time=self._text.time(last_good))
            )
        return "\n".join(lines)

    def _reading(self, status: BatteryStatus) -> str:
        reading = status.reading
        return "\n".join(
            [
                self._text.t("cli.battery", percent=reading.percent, state=self._text.charge_state(reading)),
                self._text.t("cli.voltage", voltage=reading.voltage_mv),
                self._text.t(
                    "cli.connection",
                    connection=self._text.connection_label(status),
                    device=status.interface.hidraw_path,
                ),
            ]
        )
