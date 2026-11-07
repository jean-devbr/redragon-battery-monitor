from dataclasses import dataclass
from typing import Optional

from redragon_monitor.update.domain.update_status import UpdateStatus
from redragon_monitor.update.domain.version import Version


@dataclass(frozen=True)
class UpdateCheck:
    status: UpdateStatus
    current: Version
    latest: Optional[Version] = None

    @property
    def available(self) -> bool:
        return self.status is UpdateStatus.AVAILABLE
