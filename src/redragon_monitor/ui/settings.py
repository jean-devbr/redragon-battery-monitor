from __future__ import annotations

from PySide6.QtCore import QSettings

INTERVAL_MIN, INTERVAL_MAX, INTERVAL_DEFAULT = 10, 3600, 60
THRESHOLD_MIN, THRESHOLD_MAX, THRESHOLD_DEFAULT = 5, 50, 20


def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


class AppSettings:
    def __init__(self, qsettings: QSettings | None = None):
        self._s = qsettings or QSettings("redragon-battery-monitor", "settings")

    def _int(self, key: str, default: int, lo: int, hi: int) -> int:
        try:
            return _clamp(int(self._s.value(key, default)), lo, hi)
        except (TypeError, ValueError):
            return default

    @property
    def interval_s(self) -> int:
        return self._int("interval_s", INTERVAL_DEFAULT, INTERVAL_MIN, INTERVAL_MAX)

    @interval_s.setter
    def interval_s(self, v: int) -> None:
        self._s.setValue("interval_s", _clamp(int(v), INTERVAL_MIN, INTERVAL_MAX))

    @property
    def threshold(self) -> int:
        return self._int("threshold", THRESHOLD_DEFAULT, THRESHOLD_MIN, THRESHOLD_MAX)

    @threshold.setter
    def threshold(self, v: int) -> None:
        self._s.setValue("threshold", _clamp(int(v), THRESHOLD_MIN, THRESHOLD_MAX))

    @property
    def notify(self) -> bool:
        return str(self._s.value("notify", "true")).lower() in ("true", "1")

    @notify.setter
    def notify(self, v: bool) -> None:
        self._s.setValue("notify", "true" if v else "false")
