from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from redragon_monitor.domain.battery_status import BatteryStatus
from redragon_monitor.presentation.gui.battery_icon_painter import BatteryIconPainter
from redragon_monitor.presentation.text.status_text_formatter import StatusTextFormatter

DEFAULT_THRESHOLD = 20


class TrayIcon(QObject):
    show_requested = Signal()
    refresh_requested = Signal()
    quit_requested = Signal()

    def __init__(self, painter: BatteryIconPainter, text: StatusTextFormatter, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._painter = painter
        self._text = text
        self._threshold = DEFAULT_THRESHOLD
        self.icon = QSystemTrayIcon(painter.icon(None), self)
        self.icon.setToolTip("Mouse Redragon: consultando…")
        self.menu = self._build_menu()
        self.icon.setContextMenu(self.menu)
        self.icon.activated.connect(self._on_activated)

    @staticmethod
    def available() -> bool:
        return QSystemTrayIcon.isSystemTrayAvailable()

    def show(self) -> None:
        self.icon.show()

    def set_threshold(self, value: int) -> None:
        self._threshold = value

    def update_status(self, status: BatteryStatus, last_good: Optional[BatteryStatus]) -> None:
        self.icon.setToolTip(self._text.tooltip(status, last_good))
        self.status_action.setText(self._text.tray_menu_line(status, last_good))
        self.icon.setIcon(self._icon_for(status))

    def _icon_for(self, status: BatteryStatus):
        if not status.ok:
            return self._painter.icon(None)
        return self._painter.icon(status.reading.percent, status.reading.charging, self._threshold)

    def _build_menu(self) -> QMenu:
        menu = QMenu()
        self.status_action = QAction("Consultando…", menu)
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        menu.addSeparator()
        menu.addAction("Abrir", self.show_requested.emit)
        menu.addAction("Atualizar agora", self.refresh_requested.emit)
        menu.addSeparator()
        menu.addAction("Sair", self.quit_requested.emit)
        return menu

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason != QSystemTrayIcon.Trigger:
            return
        self.show_requested.emit()
