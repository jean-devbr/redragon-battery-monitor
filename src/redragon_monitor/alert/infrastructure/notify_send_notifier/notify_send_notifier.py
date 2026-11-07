import logging
import shutil
import subprocess
from typing import Callable, Optional

log = logging.getLogger(__name__)

APP_NAME = "Redragon Battery Monitor"
TIMEOUT_S = 5

LowBatteryTexts = Callable[[int], tuple[str, str]]


class NotifySendNotifier:
    def __init__(self, texts: LowBatteryTexts, command: Optional[str] = None):
        self._texts = texts
        self._command = command or shutil.which("notify-send")
        if not self._command:
            log.warning("notify-send não encontrado (pacote libnotify-bin); notificações desativadas")

    @property
    def available(self) -> bool:
        return self._command is not None

    def low_battery(self, percent: int) -> bool:
        title, body = self._texts(percent)
        return self._send(title, body, urgency="critical")

    def _send(self, title: str, body: str, urgency: str = "normal", icon: str = "battery-low") -> bool:
        if not self._command:
            return False
        try:
            subprocess.run(
                [self._command, "-a", APP_NAME, "-u", urgency, "-i", icon, title, body],
                check=True,
                timeout=TIMEOUT_S,
            )
        except (OSError, subprocess.SubprocessError) as error:
            log.warning("falha ao notificar: %s", error)
            return False
        return True
