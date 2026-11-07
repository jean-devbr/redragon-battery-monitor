from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot
from PySide6.QtWidgets import QApplication, QMessageBox

from redragon_monitor.autostart.application.ports.autostart import Autostart
from redragon_monitor.battery.domain.battery_status import BatteryStatus
from redragon_monitor.presentation.gui.app_settings import AppSettings
from redragon_monitor.presentation.gui.battery_worker import BatteryWorker
from redragon_monitor.presentation.gui.main_window import MainWindow
from redragon_monitor.presentation.gui.tray_icon import TrayIcon
from redragon_monitor.presentation.i18n.language_detector import LanguageDetector
from redragon_monitor.presentation.gui.update_worker import UpdateWorker
from redragon_monitor.presentation.i18n.translator import Translator
from redragon_monitor.update.application.ports.update_launcher import UpdateLauncher
from redragon_monitor.update.domain.update_check import UpdateCheck

log = logging.getLogger(__name__)

THREAD_WAIT_MS = 5000
MS_PER_SECOND = 1000


class GuiController(QObject):
    poll_requested = Signal(bool)
    threshold_requested = Signal(int)
    update_check_requested = Signal()

    def __init__(
        self,
        app: QApplication,
        settings: AppSettings,
        worker: BatteryWorker,
        window: MainWindow,
        tray: Optional[TrayIcon],
        autostart: Autostart,
        translator: Translator,
        detector: LanguageDetector,
        update_worker: UpdateWorker,
        update_launcher: UpdateLauncher,
    ):
        super().__init__()
        self._app = app
        self._settings = settings
        self._worker = worker
        self._window = window
        self._tray = tray
        self._autostart = autostart
        self._translator = translator
        self._detector = detector
        self._update_worker = update_worker
        self._update_launcher = update_launcher
        self._update: Optional[UpdateCheck] = None
        self._busy = False
        self._thread = QThread(self)
        self._update_thread = QThread(self)
        self._timer = QTimer(self)

    @property
    def has_tray(self) -> bool:
        return self._tray is not None

    def start(self, minimized: bool) -> None:
        self._start_worker()
        self._connect_window()
        self._connect_tray()
        self._timer.timeout.connect(self.refresh)
        self._timer.start(self._settings.interval_s * MS_PER_SECOND)
        if not (minimized and self.has_tray):
            self.show_window()
        self.refresh()
        if self._settings.check_updates:
            self.check_update()

    def stop(self) -> None:
        self._timer.stop()
        self._thread.quit()
        self._update_thread.quit()
        self._thread.wait(THREAD_WAIT_MS)
        self._update_thread.wait(THREAD_WAIT_MS)

    @Slot()
    def check_update(self) -> None:
        self._window.show_update_checking()
        self.update_check_requested.emit()

    @Slot(object)
    def on_update_check(self, check: UpdateCheck) -> None:
        self._update = check
        self._window.show_update(check)
        if self._tray is None:
            return
        self._tray.show_update(check)

    @Slot()
    def install_update(self) -> None:
        if self._update is None or not self._update.available:
            return
        answer = QMessageBox.question(
            self._window,
            self._translator.t("update.confirm.title"),
            self._translator.t("update.confirm.body", version=str(self._update.latest)),
        )
        if answer != QMessageBox.Yes:
            return
        if self._update_launcher.launch(self._translator.language.value):
            self.quit()
            return
        QMessageBox.information(
            self._window,
            self._translator.t("update.manual.title"),
            self._translator.t("update.manual.body", command=self._update_launcher.manual_command()),
        )

    @Slot(bool)
    def on_check_updates(self, value: bool) -> None:
        self._settings.check_updates = value

    @Slot()
    def refresh(self) -> None:
        if self._busy:
            return
        self._busy = True
        self._window.set_busy(True)
        self.poll_requested.emit(self._settings.notify)

    @Slot(object, object)
    def on_status(self, status: BatteryStatus, last_good: Optional[BatteryStatus]) -> None:
        self._busy = False
        self._window.set_busy(False)
        self._window.show_status(status, last_good)
        if self._tray is None:
            return
        self._tray.update_status(status, last_good)

    @Slot(int)
    def on_interval(self, value: int) -> None:
        self._settings.interval_s = value
        self._timer.start(self._settings.interval_s * MS_PER_SECOND)

    @Slot(int)
    def on_threshold(self, value: int) -> None:
        self._settings.threshold = value
        self.threshold_requested.emit(self._settings.threshold)
        if self._tray is None:
            return
        self._tray.set_threshold(self._settings.threshold)

    @Slot(bool)
    def on_notify(self, value: bool) -> None:
        self._settings.notify = value

    @Slot(bool)
    def on_autostart(self, enabled: bool) -> None:
        try:
            self._apply_autostart(enabled)
        except OSError as error:
            QMessageBox.warning(
                self._window,
                self._translator.t("autostart.title"),
                self._translator.t("autostart.error", error=error),
            )
            self._window.set_autostart_checked(self._autostart.is_enabled())

    @Slot(str)
    def on_language(self, preference: str) -> None:
        self._settings.language = preference
        self._translator.set_language(self._detector.resolve(preference))
        self._window.retranslate()
        if self._tray is None:
            return
        self._tray.retranslate()

    @Slot()
    def show_window(self) -> None:
        self._window.show()
        self._window.raise_()
        self._window.activateWindow()

    @Slot()
    def quit(self) -> None:
        self.stop()
        self._app.quit()

    def _apply_autostart(self, enabled: bool) -> None:
        if not enabled:
            self._autostart.disable()
            return
        log.info("autostart criado em %s", self._autostart.enable())

    def _start_worker(self) -> None:
        self._worker.moveToThread(self._thread)
        self.poll_requested.connect(self._worker.poll)
        self.threshold_requested.connect(self._worker.change_threshold)
        self._worker.finished.connect(self.on_status)
        self._thread.start()
        self._update_worker.moveToThread(self._update_thread)
        self.update_check_requested.connect(self._update_worker.check)
        self._update_worker.finished.connect(self.on_update_check)
        self._update_thread.start()

    def _connect_window(self) -> None:
        self._window.refresh_requested.connect(self.refresh)
        self._window.interval_changed.connect(self.on_interval)
        self._window.threshold_changed.connect(self.on_threshold)
        self._window.notify_changed.connect(self.on_notify)
        self._window.autostart_changed.connect(self.on_autostart)
        self._window.language_changed.connect(self.on_language)
        self._window.check_update_requested.connect(self.check_update)
        self._window.install_update_requested.connect(self.install_update)
        self._window.check_updates_changed.connect(self.on_check_updates)

    def _connect_tray(self) -> None:
        if self._tray is None:
            log.warning("bandeja indisponível: fechar a janela encerra o programa")
            return
        self._tray.set_threshold(self._settings.threshold)
        self._tray.show_requested.connect(self.show_window)
        self._tray.refresh_requested.connect(self.refresh)
        self._tray.quit_requested.connect(self.quit)
        self._tray.update_requested.connect(self.install_update)
        self._tray.show()
