from typing import Optional

from redragon_monitor.alert.domain.low_battery_policy import LowBatteryPolicy
from redragon_monitor.alert.application.ports.notifier import Notifier
from redragon_monitor.battery.application.read_battery import ReadBatteryUseCase
from redragon_monitor.battery.domain.battery_status import BatteryStatus


class BatteryMonitor:
    def __init__(self, read_battery: ReadBatteryUseCase, policy: LowBatteryPolicy, notifier: Notifier):
        self._read_battery = read_battery
        self._policy = policy
        self._notifier = notifier

    @property
    def last_good(self) -> Optional[BatteryStatus]:
        return self._read_battery.last_good

    def change_threshold(self, threshold: int) -> None:
        self._policy.change_threshold(threshold)

    def check(self, notify: bool) -> BatteryStatus:
        status = self._read_battery.execute()
        if self._policy.should_alert(status) and notify:
            self._notifier.low_battery(status.reading.percent)
        return status
