from PySide6.QtCore import QObject, Signal, Slot

from redragon_monitor.update.application.check_for_update import CheckForUpdateUseCase


class UpdateWorker(QObject):
    finished = Signal(object)

    def __init__(self, check_for_update: CheckForUpdateUseCase):
        super().__init__()
        self._check_for_update = check_for_update

    @Slot()
    def check(self) -> None:
        self.finished.emit(self._check_for_update.execute())
