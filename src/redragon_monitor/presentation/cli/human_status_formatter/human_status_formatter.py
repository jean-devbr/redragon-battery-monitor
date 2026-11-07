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
            lines.append(f"Detalhe: {status.detail}")
        if last_good is not None and last_good.ok:
            lines.append(f"Última leitura válida: {last_good.reading.percent}% às {last_good.timestamp:%H:%M:%S}")
        return "\n".join(lines)

    def _reading(self, status: BatteryStatus) -> str:
        reading = status.reading
        return (
            f"Bateria: {reading.percent}% ({self._text.charge_state(reading)})\n"
            f"Tensão:  {reading.voltage_mv} mV\n"
            f"Conexão: {status.interface.connection.value} ({status.interface.hidraw_path})"
        )
