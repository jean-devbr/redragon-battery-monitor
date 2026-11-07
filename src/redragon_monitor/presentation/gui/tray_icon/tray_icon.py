from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from redragon_monitor.battery.domain.battery_status import BatteryStatus
from redragon_monitor.presentation.gui.battery_icon_painter import BatteryIconPainter
from redragon_monitor.presentation.text.status_text_formatter import StatusTextFormatter
from redragon_monitor.update.domain.update_check import UpdateCheck

DEFAULT_THRESHOLD = 20


class TrayIcon(QObject):
    show_requested = Signal()
    refresh_requested = Signal()
    quit_requested = Signal()
    update_requested = Signal()

    def __init__(self, painter: BatteryIconPainter, text: StatusTextFormatter, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._painter = painter
        self._text = text
        self._threshold = DEFAULT_THRESHOLD
        self._status: Optional[BatteryStatus] = None
        self._last_good: Optional[BatteryStatus] = None
        self._update: Optional[UpdateCheck] = None
        self.icon = QSystemTrayIcon(painter.icon(None), self)
        self.menu = self._build_menu()
        self.icon.setContextMenu(self.menu)
        self.icon.activated.connect(self._on_activated)
        self.retranslate()

    @staticmethod
    def available() -> bool:
        return QSystemTrayIcon.isSystemTrayAvailable()

    def show(self) -> None:
        self.icon.show()

    def set_threshold(self, value: int) -> None:
        self._threshold = value

    def retranslate(self) -> None:
        self.open_action.setText(self._text.t("tray.menu.open"))
        self.refresh_action.setText(self._text.t("tray.menu.refresh"))
        self.quit_action.setText(self._text.t("tray.menu.quit"))
        self._render_text()
        self._render_update()

    def show_update(self, check: UpdateCheck) -> None:
        self._update = check
        self._render_update()

    def _render_update(self) -> None:
        available = self._update is not None and self._update.available
        self.update_action.setVisible(available)
        if not available:
            return
        self.update_action.setText(self._text.t("update.tray", version=str(self._update.latest)))

    def update_status(self, status: BatteryStatus, last_good: Optional[BatteryStatus]) -> None:
        self._status = status
        self._last_good = last_good
        self._render_text()
        self.icon.setIcon(self._icon_for(status))

    def _render_text(self) -> None:
        if self._status is None:
            self.icon.setToolTip(self._text.tray_querying())
            self.status_action.setText(self._text.t("window.querying"))
            return
        self.icon.setToolTip(self._text.tooltip(self._status, self._last_good))
        self.status_action.setText(self._text.tray_menu_line(self._status, self._last_good))

    def _icon_for(self, status: BatteryStatus):
        if not status.ok:
            return self._painter.icon(None)
        return self._painter.icon(status.reading.percent, status.reading.charging, self._threshold)

    def _build_menu(self) -> QMenu:
        menu = QMenu()
        self.status_action = QAction(menu)
        self.status_action.setEnabled(False)
        self.open_action = QAction(menu)
        self.open_action.triggered.connect(self.show_requested)
        self.refresh_action = QAction(menu)
        self.refresh_action.triggered.connect(self.refresh_requested)
        self.update_action = QAction(menu)
        self.update_action.setVisible(False)
        self.update_action.triggered.connect(self.update_requested)
        self.quit_action = QAction(menu)
        self.quit_action.triggered.connect(self.quit_requested)
        menu.addAction(self.status_action)
        menu.addSeparator()
        menu.addAction(self.open_action)
        menu.addAction(self.refresh_action)
        menu.addAction(self.update_action)
        menu.addSeparator()
        menu.addAction(self.quit_action)
        return menu

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason != QSystemTrayIcon.Trigger:
            return
        self.show_requested.emit()
