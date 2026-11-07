from __future__ import annotations

from PySide6.QtCore import QSettings

ORGANIZATION = "redragon-battery-monitor"
APPLICATION = "settings"
TRUE_VALUES = ("true", "1")
LANGUAGE_CHOICES = ("auto", "pt", "en")


class AppSettings:
    INTERVAL_MIN, INTERVAL_MAX, INTERVAL_DEFAULT = 10, 3600, 60
    THRESHOLD_MIN, THRESHOLD_MAX, THRESHOLD_DEFAULT = 5, 50, 20

    def __init__(self, store: QSettings | None = None):
        self._store = store or QSettings(ORGANIZATION, APPLICATION)

    @property
    def interval_s(self) -> int:
        return self._read_int("interval_s", self.INTERVAL_DEFAULT, self.INTERVAL_MIN, self.INTERVAL_MAX)

    @interval_s.setter
    def interval_s(self, value: int) -> None:
        self._store.setValue("interval_s", self._clamp(int(value), self.INTERVAL_MIN, self.INTERVAL_MAX))

    @property
    def threshold(self) -> int:
        return self._read_int("threshold", self.THRESHOLD_DEFAULT, self.THRESHOLD_MIN, self.THRESHOLD_MAX)

    @threshold.setter
    def threshold(self, value: int) -> None:
        self._store.setValue("threshold", self._clamp(int(value), self.THRESHOLD_MIN, self.THRESHOLD_MAX))

    @property
    def notify(self) -> bool:
        return str(self._store.value("notify", "true")).lower() in TRUE_VALUES

    @notify.setter
    def notify(self, value: bool) -> None:
        self._store.setValue("notify", "true" if value else "false")

    @property
    def language(self) -> str:
        value = str(self._store.value("language", LANGUAGE_CHOICES[0]))
        return value if value in LANGUAGE_CHOICES else LANGUAGE_CHOICES[0]

    @language.setter
    def language(self, value: str) -> None:
        self._store.setValue("language", value if value in LANGUAGE_CHOICES else LANGUAGE_CHOICES[0])

    def _read_int(self, key: str, default: int, low: int, high: int) -> int:
        try:
            return self._clamp(int(self._store.value(key, default)), low, high)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _clamp(value: int, low: int, high: int) -> int:
        return max(low, min(high, value))
