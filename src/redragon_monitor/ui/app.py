from __future__ import annotations

import logging
import os
from datetime import datetime
import sys
from typing import Optional

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication, QMessageBox

from redragon_monitor import __version__
from redragon_monitor.services import autostart
from redragon_monitor.services.battery_service import BatteryService, BatteryStatus, Status
from redragon_monitor.services.notification_service import DesktopNotifier, LowBatteryPolicy
from redragon_monitor.ui.icons import app_icon
from redragon_monitor.ui.settings import AppSettings
from redragon_monitor.ui.tray import Tray
from redragon_monitor.ui.window import MainWindow

log = logging.getLogger(__name__)
INSTANCE_KEY = f"redragon-battery-monitor-{os.getuid()}"


class BatteryWorker(QObject):
    finished = Signal(object, object)

    def __init__(self, service: BatteryService):
        super().__init__()
        self._service = service

    @Slot()
    def poll(self) -> None:
        try:
            s = self._service.read()
        except Exception as e:
            log.exception("falha inesperada na consulta")
            s = BatteryStatus(Status.ERROR, datetime.now(), detail=str(e))
        self.finished.emit(s, self._service.last_good)


class Controller(QObject):
    poll_requested = Signal()

    def __init__(self, app: QApplication, minimized: bool):
        super().__init__()
        self.app = app
        self.settings = AppSettings()
        self.policy = LowBatteryPolicy(self.settings.threshold)
        self.notifier = DesktopNotifier()
        self._busy = False

        self.tray: Optional[Tray] = Tray(self) if Tray.available() else None
        if self.tray is None:
            log.warning("bandeja indisponível: fechar a janela encerra o programa")
        self.window = MainWindow(self.settings, autostart.is_enabled(), hide_on_close=self.tray is not None)
        self.window.setWindowIcon(app_icon())

        self.thread = QThread(self)
        self.worker = BatteryWorker(BatteryService())
        self.worker.moveToThread(self.thread)
        self.poll_requested.connect(self.worker.poll)
        self.worker.finished.connect(self.on_status)
        self.thread.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(self.settings.interval_s * 1000)

        w = self.window
        w.refresh_requested.connect(self.refresh)
        w.interval_changed.connect(self.on_interval)
        w.threshold_changed.connect(self.on_threshold)
        w.notify_changed.connect(self.on_notify)
        w.autostart_changed.connect(self.on_autostart)

        if self.tray:
            self.tray.set_threshold(self.settings.threshold)
            self.tray.show_requested.connect(self.show_window)
            self.tray.refresh_requested.connect(self.refresh)
            self.tray.quit_requested.connect(self.quit)
            self.tray.show()

        if not (minimized and self.tray):
            self.show_window()
        self.refresh()

    @Slot()
    def refresh(self) -> None:
        if self._busy:
            return
        self._busy = True
        self.window.set_busy(True)
        self.poll_requested.emit()

    @Slot(object, object)
    def on_status(self, s: BatteryStatus, last_good: Optional[BatteryStatus]) -> None:
        self._busy = False
        self.window.set_busy(False)
        self.window.show_status(s, last_good)
        if self.tray:
            self.tray.update_status(s, last_good)
        if s.ok:
            log.debug("bateria %s%%", s.reading.percent)
        if self.policy.update(s) and self.settings.notify:
            self.notifier.low_battery(s.reading.percent)

    @Slot(int)
    def on_interval(self, v: int) -> None:
        self.settings.interval_s = v
        self.timer.start(self.settings.interval_s * 1000)

    @Slot(int)
    def on_threshold(self, v: int) -> None:
        self.settings.threshold = v
        self.policy = LowBatteryPolicy(self.settings.threshold)
        if self.tray:
            self.tray.set_threshold(self.settings.threshold)

    @Slot(bool)
    def on_notify(self, v: bool) -> None:
        self.settings.notify = v

    @Slot(bool)
    def on_autostart(self, v: bool) -> None:
        try:
            if v:
                path = autostart.enable()
                log.info("autostart criado em %s", path)
            else:
                autostart.disable()
        except OSError as e:
            QMessageBox.warning(self.window, "Iniciar com o sistema", f"Não foi possível alterar: {e}")
            self.window.autostart_check.blockSignals(True)
            self.window.autostart_check.setChecked(autostart.is_enabled())
            self.window.autostart_check.blockSignals(False)

    @Slot()
    def show_window(self) -> None:
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    @Slot()
    def quit(self) -> None:
        self.timer.stop()
        self.thread.quit()
        self.thread.wait(5000)
        self.app.quit()


def _signal_running_instance() -> bool:
    sock = QLocalSocket()
    sock.connectToServer(INSTANCE_KEY)
    if sock.waitForConnected(300):
        sock.write(b"show")
        sock.waitForBytesWritten(300)
        sock.disconnectFromServer()
        return True
    return False


def run(minimized: bool = False) -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Redragon Battery Monitor")
    app.setApplicationVersion(__version__)
    app.setDesktopFileName("redragon-battery-monitor")

    if _signal_running_instance():
        log.info("já está em execução; janela existente foi trazida para frente")
        return 0

    QLocalServer.removeServer(INSTANCE_KEY)
    server = QLocalServer()
    server.listen(INSTANCE_KEY)

    controller = Controller(app, minimized)
    app.setQuitOnLastWindowClosed(controller.tray is None)
    app.aboutToQuit.connect(lambda: (controller.thread.quit(), controller.thread.wait(5000)))

    def on_new_connection():
        conn = server.nextPendingConnection()
        if conn:
            conn.readyRead.connect(lambda: (conn.readAll(), controller.show_window()))
            conn.disconnected.connect(conn.deleteLater)

    server.newConnection.connect(on_new_connection)
    return app.exec()
