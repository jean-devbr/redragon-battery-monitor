import logging
import sys
from typing import Callable

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from redragon_monitor import __version__
from redragon_monitor.alert.application.battery_monitor import BatteryMonitor
from redragon_monitor.autostart.application.ports.autostart import Autostart
from redragon_monitor.shared.application.ports.clock import Clock
from redragon_monitor.presentation.gui.app_settings import AppSettings
from redragon_monitor.presentation.gui.battery_icon_painter import BatteryIconPainter
from redragon_monitor.presentation.gui.battery_worker import BatteryWorker
from redragon_monitor.presentation.gui.gui_controller import GuiController
from redragon_monitor.presentation.gui.main_window import MainWindow
from redragon_monitor.presentation.gui.single_instance import SingleInstance
from redragon_monitor.presentation.gui.tray_icon import TrayIcon
from redragon_monitor.presentation.i18n.language_detector import LanguageDetector
from redragon_monitor.presentation.i18n.translator import Translator
from redragon_monitor.presentation.gui.update_worker import UpdateWorker
from redragon_monitor.presentation.text.status_text_formatter import StatusTextFormatter
from redragon_monitor.update.application.check_for_update import CheckForUpdateUseCase
from redragon_monitor.update.application.ports.update_launcher import UpdateLauncher

log = logging.getLogger(__name__)

APP_NAME = "Redragon Battery Monitor"
DESKTOP_FILE_NAME = "redragon-battery-monitor"


class GuiApp:
    def __init__(
        self,
        monitor_factory: Callable[[int], BatteryMonitor],
        autostart: Autostart,
        clock: Clock,
        text: StatusTextFormatter,
        translator: Translator,
        detector: LanguageDetector,
        check_for_update: CheckForUpdateUseCase,
        update_launcher: UpdateLauncher,
        repository_url: str,
    ):
        self._monitor_factory = monitor_factory
        self._autostart = autostart
        self._clock = clock
        self._text = text
        self._translator = translator
        self._detector = detector
        self._check_for_update = check_for_update
        self._update_launcher = update_launcher
        self._repository_url = repository_url

    def run(self, minimized: bool) -> int:
        app = self._create_application()
        instance = SingleInstance()
        if instance.notify_running():
            log.info("já está em execução; janela existente foi trazida para frente")
            return 0
        controller = self._build_controller(app)
        app.setQuitOnLastWindowClosed(not controller.has_tray)
        app.aboutToQuit.connect(controller.stop)
        instance.listen(controller.show_window)
        controller.start(minimized)
        return app.exec()

    @staticmethod
    def export_icon(path: str) -> int:
        _app = QGuiApplication.instance() or QGuiApplication(sys.argv[:1])
        BatteryIconPainter().save_app_icon(path)
        return 0

    @staticmethod
    def _create_application() -> QApplication:
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(__version__)
        app.setDesktopFileName(DESKTOP_FILE_NAME)
        return app

    def _build_controller(self, app: QApplication) -> GuiController:
        settings = AppSettings()
        self._translator.set_language(self._detector.resolve(settings.language))
        painter = BatteryIconPainter()
        tray = TrayIcon(painter, self._text) if TrayIcon.available() else None
        window = MainWindow(
            settings,
            painter,
            self._text,
            self._autostart.is_enabled(),
            hide_on_close=tray is not None,
            installed_version=str(self._check_for_update.current),
        )
        window.setWindowIcon(painter.app_icon())
        worker = BatteryWorker(self._monitor_factory(settings.threshold), self._clock)
        return GuiController(
            app,
            settings,
            worker,
            window,
            tray,
            self._autostart,
            self._translator,
            self._detector,
            UpdateWorker(self._check_for_update),
            self._update_launcher,
            self._repository_url,
        )
