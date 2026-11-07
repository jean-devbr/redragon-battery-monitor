import logging

from PySide6.QtCore import QObject, Signal, Slot

from redragon_monitor.application.battery_monitor import BatteryMonitor
from redragon_monitor.application.ports.clock import Clock
from redragon_monitor.domain.battery_status import BatteryStatus
from redragon_monitor.domain.read_status import ReadStatus

log = logging.getLogger(__name__)


class BatteryWorker(QObject):
    finished = Signal(object, object)

    def __init__(self, monitor: BatteryMonitor, clock: Clock):
        super().__init__()
        self._monitor = monitor
        self._clock = clock

    @Slot(bool)
    def poll(self, notify: bool) -> None:
        try:
            status = self._monitor.check(notify)
        except Exception as error:
            log.exception("falha inesperada na consulta")
            status = BatteryStatus(ReadStatus.ERROR, self._clock.now(), detail=str(error))
        self.finished.emit(status, self._monitor.last_good)

    @Slot(int)
    def change_threshold(self, threshold: int) -> None:
        self._monitor.change_threshold(threshold)
