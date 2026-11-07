from typing import Optional

from redragon_monitor.battery.domain.battery_reading import BatteryReading
from redragon_monitor.battery.domain.battery_status import BatteryStatus
from redragon_monitor.presentation.i18n.translator import Translator
from redragon_monitor.presentation.text.status_messages import StatusMessages

EMPTY = "—"
TIME_FORMAT = "%H:%M:%S"


class StatusTextFormatter:
    def __init__(self, messages: StatusMessages, translator: Translator):
        self._messages = messages
        self._translator = translator

    @property
    def language(self) -> str:
        return self._translator.language.value

    def t(self, key: str, **values) -> str:
        return self._translator.t(key, **values)

    def message(self, status: BatteryStatus) -> str:
        return self._messages.message(status)

    def message_with_detail(self, status: BatteryStatus) -> str:
        if not status.detail:
            return self.message(status)
        return f"{self.message(status)}\n{status.detail}"

    def charge_state(self, reading: BatteryReading) -> str:
        return self.t("charge.charging" if reading.charging else "charge.discharging")

    def connection_label(self, status: BatteryStatus) -> str:
        if status.interface is None:
            return EMPTY
        return self.t(f"connection.{status.interface.connection.value}")

    @staticmethod
    def time(status: BatteryStatus) -> str:
        return status.timestamp.strftime(TIME_FORMAT)

    def last_good(self, last_good: Optional[BatteryStatus]) -> str:
        if last_good is None or not last_good.ok:
            return EMPTY
        reading = last_good.reading
        return self.t(
            "summary.last_good", percent=reading.percent, state=self.charge_state(reading), time=self.time(last_good)
        )

    def tooltip(self, status: BatteryStatus, last_good: Optional[BatteryStatus]) -> str:
        prefix = self.t("tray.prefix")
        if status.ok:
            return f"{prefix}{status.reading.percent}% ({self.charge_state(status.reading)})"
        text = f"{prefix}{self.message(status)}"
        if last_good is None or not last_good.ok:
            return text
        return f"{text}\n{self.t('tray.last_reading', summary=self.last_good(last_good))}"

    def tray_menu_line(self, status: BatteryStatus, last_good: Optional[BatteryStatus]) -> str:
        return self.tooltip(status, last_good).splitlines()[0].replace(self.t("tray.prefix"), "")

    def tray_querying(self) -> str:
        return f"{self.t('tray.prefix')}{self.t('tray.querying')}"
