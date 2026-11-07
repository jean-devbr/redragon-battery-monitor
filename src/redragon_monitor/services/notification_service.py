"""Política de bateria baixa e envio de notificações do desktop (notify-send / libnotify)."""
from __future__ import annotations

import logging
import shutil
import subprocess
from typing import Optional

from redragon_monitor.services.battery_service import BatteryStatus

log = logging.getLogger(__name__)

DEFAULT_THRESHOLD = 20
DEFAULT_REARM_MARGIN = 5


class LowBatteryPolicy:
    """Dispara uma vez por ciclo de descarga.

    - Dispara quando: leitura válida, fora da carga, percent <= threshold e armado.
    - Rearma quando: começa a carregar ou percent >= threshold + margem.
    - Leituras indisponíveis/invalidas não alteram o estado (não inventa nada).
    """

    def __init__(self, threshold: int = DEFAULT_THRESHOLD, rearm_margin: int = DEFAULT_REARM_MARGIN):
        if not 1 <= threshold <= 99:
            raise ValueError("threshold deve estar entre 1 e 99")
        self.threshold = threshold
        self.rearm_margin = rearm_margin
        self._armed = True

    def update(self, status: BatteryStatus) -> bool:
        r = status.reading
        if not status.ok or r is None:
            return False
        if r.charging or r.percent >= self.threshold + self.rearm_margin:
            self._armed = True
            return False
        if r.percent <= self.threshold and self._armed:
            self._armed = False
            return True
        return False


class DesktopNotifier:
    APP_NAME = "Redragon Battery Monitor"

    def __init__(self, command: Optional[str] = None):
        self._cmd = command or shutil.which("notify-send")
        if not self._cmd:
            log.warning("notify-send não encontrado (pacote libnotify-bin); notificações desativadas")

    @property
    def available(self) -> bool:
        return self._cmd is not None

    def send(self, title: str, body: str, urgency: str = "normal", icon: str = "battery-low") -> bool:
        if not self._cmd:
            return False
        try:
            subprocess.run(
                [self._cmd, "-a", self.APP_NAME, "-u", urgency, "-i", icon, title, body],
                check=True,
                timeout=5,
            )
            return True
        except (OSError, subprocess.SubprocessError) as e:
            log.warning("falha ao notificar: %s", e)
            return False

    def low_battery(self, percent: int) -> bool:
        return self.send(
            "Bateria do mouse baixa",
            f"Redragon M719RGB-PRO com {percent}%. Conecte o cabo USB-C.",
            urgency="critical",
        )
