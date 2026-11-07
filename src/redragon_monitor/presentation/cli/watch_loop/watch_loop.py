import time
from typing import Callable

from redragon_monitor.alert.application.battery_monitor import BatteryMonitor
from redragon_monitor.battery.domain.battery_status import BatteryStatus

Render = Callable[[BatteryStatus, object], str]


class WatchLoop:
    def __init__(
        self,
        monitor: BatteryMonitor,
        render: Render,
        output: Callable[[str], None],
        sleep: Callable[[float], None] = time.sleep,
    ):
        self._monitor = monitor
        self._render = render
        self._output = output
        self._sleep = sleep

    def run(self, interval: float, notify: bool, max_cycles: int = 0) -> int:
        cycles = 0
        try:
            while max_cycles == 0 or cycles < max_cycles:
                status = self._monitor.check(notify)
                self._output(self._render(status, self._monitor.last_good))
                cycles += 1
                self._sleep(interval)
        except KeyboardInterrupt:
            return 0
        return 0
