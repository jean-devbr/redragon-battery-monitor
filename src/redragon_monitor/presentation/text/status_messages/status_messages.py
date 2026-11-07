from redragon_monitor.battery.domain.battery_status import BatteryStatus
from redragon_monitor.presentation.i18n.translator import Translator


class StatusMessages:
    def __init__(self, translator: Translator):
        self._translator = translator

    def message(self, status: BatteryStatus) -> str:
        return self._translator.t(f"status.{status.status.value}")
