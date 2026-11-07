import logging

from redragon_monitor.update.application.ports.release_source import ReleaseSource
from redragon_monitor.update.domain.update_check import UpdateCheck
from redragon_monitor.update.domain.update_status import UpdateStatus
from redragon_monitor.update.domain.version import Version

log = logging.getLogger(__name__)


class CheckForUpdateUseCase:
    def __init__(self, source: ReleaseSource, current: Version):
        self._source = source
        self._current = current

    @property
    def current(self) -> Version:
        return self._current

    def execute(self) -> UpdateCheck:
        try:
            latest = self._source.latest_version()
        except (OSError, ValueError) as error:
            log.info("não foi possível verificar atualizações: %s", error)
            return UpdateCheck(UpdateStatus.FAILED, self._current)
        status = UpdateStatus.AVAILABLE if latest > self._current else UpdateStatus.UP_TO_DATE
        return UpdateCheck(status, self._current, latest)
