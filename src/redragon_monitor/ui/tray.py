from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from redragon_monitor.services.battery_service import BatteryStatus
from redragon_monitor.ui.icons import battery_icon
from redragon_monitor.ui.window import describe_last_good


def tooltip_text(s: BatteryStatus, last_good: Optional[BatteryStatus]) -> str:
    if s.ok and s.reading:
        state = "carregando" if s.reading.charging else "na bateria"
        return f"Mouse Redragon: {s.reading.percent}% ({state})"
    text = f"Mouse Redragon: {s.message}"
    if last_good and last_good.reading:
        text += f"\nÚltima leitura: {describe_last_good(last_good)}"
    return text


class Tray(QObject):
    show_requested = Signal()
    refresh_requested = Signal()
    quit_requested = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._threshold = 20
        self.icon = QSystemTrayIcon(battery_icon(None), self)
        self.icon.setToolTip("Mouse Redragon: consultando…")

        self.menu = QMenu()
        self.status_action = QAction("Consultando…", self.menu)
        self.status_action.setEnabled(False)
        self.menu.addAction(self.status_action)
        self.menu.addSeparator()
        self.menu.addAction("Abrir", self.show_requested.emit)
        self.menu.addAction("Atualizar agora", self.refresh_requested.emit)
        self.menu.addSeparator()
        self.menu.addAction("Sair", self.quit_requested.emit)
        self.icon.setContextMenu(self.menu)
        self.icon.activated.connect(self._on_activated)

    @staticmethod
    def available() -> bool:
        return QSystemTrayIcon.isSystemTrayAvailable()

    def show(self) -> None:
        self.icon.show()

    def set_threshold(self, value: int) -> None:
        self._threshold = value

    def update_status(self, s: BatteryStatus, last_good: Optional[BatteryStatus]) -> None:
        text = tooltip_text(s, last_good)
        self.icon.setToolTip(text)
        self.status_action.setText(text.splitlines()[0].replace("Mouse Redragon: ", ""))
        if s.ok and s.reading:
            self.icon.setIcon(battery_icon(s.reading.percent, s.reading.charging, self._threshold))
        else:
            self.icon.setIcon(battery_icon(None))

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.Trigger:
            self.show_requested.emit()
