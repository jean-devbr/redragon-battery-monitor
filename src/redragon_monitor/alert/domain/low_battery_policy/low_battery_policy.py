from redragon_monitor.battery.domain.battery_status import BatteryStatus

DEFAULT_THRESHOLD = 20
DEFAULT_REARM_MARGIN = 5
MIN_THRESHOLD = 1
MAX_THRESHOLD = 99


class LowBatteryPolicy:
    def __init__(self, threshold: int = DEFAULT_THRESHOLD, rearm_margin: int = DEFAULT_REARM_MARGIN):
        self._validate(threshold)
        self._threshold = threshold
        self._rearm_margin = rearm_margin
        self._armed = True

    @property
    def threshold(self) -> int:
        return self._threshold

    def change_threshold(self, threshold: int) -> None:
        self._validate(threshold)
        self._threshold = threshold
        self._armed = True

    def should_alert(self, status: BatteryStatus) -> bool:
        if not status.ok:
            return False
        reading = status.reading
        if reading.charging or reading.percent >= self._threshold + self._rearm_margin:
            self._armed = True
            return False
        if reading.percent > self._threshold or not self._armed:
            return False
        self._armed = False
        return True

    @staticmethod
    def _validate(threshold: int) -> None:
        if not MIN_THRESHOLD <= threshold <= MAX_THRESHOLD:
            raise ValueError(f"threshold deve estar entre {MIN_THRESHOLD} e {MAX_THRESHOLD}")
