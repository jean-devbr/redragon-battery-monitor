from typing import Optional

from redragon_monitor.battery.domain.battery_reading import BatteryReading
from redragon_monitor.battery.domain.battery_status import BatteryStatus
from redragon_monitor.device.domain.connection_type import ConnectionType
from redragon_monitor.presentation.text.status_messages import StatusMessages

EMPTY = "—"
TRAY_PREFIX = "Mouse Redragon: "
CONNECTION_LABELS = {
    ConnectionType.USB_C: "Cabo USB-C",
    ConnectionType.RECEIVER: "Receptor 2.4 GHz",
}


class StatusTextFormatter:
    def __init__(self, messages: StatusMessages):
        self._messages = messages

    def message(self, status: BatteryStatus) -> str:
        return self._messages.message(status)

    def message_with_detail(self, status: BatteryStatus) -> str:
        if not status.detail:
            return self.message(status)
        return f"{self.message(status)}\n{status.detail}"

    @staticmethod
    def charge_state(reading: BatteryReading) -> str:
        return "carregando" if reading.charging else "na bateria"

    @staticmethod
    def connection_label(status: BatteryStatus) -> str:
        if status.interface is None:
            return EMPTY
        return CONNECTION_LABELS.get(status.interface.connection, EMPTY)

    def last_good(self, last_good: Optional[BatteryStatus]) -> str:
        if last_good is None or not last_good.ok:
            return EMPTY
        reading = last_good.reading
        return f"{reading.percent}% ({self.charge_state(reading)}) às {last_good.timestamp:%H:%M:%S}"

    def tooltip(self, status: BatteryStatus, last_good: Optional[BatteryStatus]) -> str:
        if status.ok:
            return f"{TRAY_PREFIX}{status.reading.percent}% ({self.charge_state(status.reading)})"
        text = f"{TRAY_PREFIX}{self.message(status)}"
        if last_good is None or not last_good.ok:
            return text
        return f"{text}\nÚltima leitura: {self.last_good(last_good)}"

    def tray_menu_line(self, status: BatteryStatus, last_good: Optional[BatteryStatus]) -> str:
        return self.tooltip(status, last_good).splitlines()[0].replace(TRAY_PREFIX, "")
