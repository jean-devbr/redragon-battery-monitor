from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent, QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from redragon_monitor.battery.domain.battery_status import BatteryStatus
from redragon_monitor.presentation.gui.app_settings import AppSettings
from redragon_monitor.presentation.gui.battery_icon_painter import BatteryIconPainter
from redragon_monitor.presentation.text.status_text_formatter import StatusTextFormatter
from redragon_monitor.update.domain.update_check import UpdateCheck
from redragon_monitor.update.domain.update_status import UpdateStatus

EMPTY = "—"
ICON_SIZE = 72
MIN_WIDTH = 380
LANGUAGE_OPTIONS = (("auto", None), ("pt", "Português"), ("en", "English"))
LANGUAGE_TOGGLE = {"pt": ("en", "🌐 English"), "en": ("pt", "🌐 Português")}
UPDATE_KEYS = {
    UpdateStatus.AVAILABLE: "update.available",
    UpdateStatus.UP_TO_DATE: "update.up_to_date",
    UpdateStatus.FAILED: "update.failed",
}


class MainWindow(QWidget):
    refresh_requested = Signal()
    interval_changed = Signal(int)
    threshold_changed = Signal(int)
    notify_changed = Signal(bool)
    autostart_changed = Signal(bool)
    language_changed = Signal(str)
    check_update_requested = Signal()
    install_update_requested = Signal()
    check_updates_changed = Signal(bool)

    def __init__(
        self,
        settings: AppSettings,
        painter: BatteryIconPainter,
        text: StatusTextFormatter,
        autostart_enabled: bool,
        hide_on_close: bool,
        installed_version: str = "",
    ):
        super().__init__()
        self._painter = painter
        self._text = text
        self._hide_on_close = hide_on_close
        self._threshold = settings.threshold
        self._busy = False
        self._status: Optional[BatteryStatus] = None
        self._last_good: Optional[BatteryStatus] = None
        self._installed_version = installed_version
        self._update: Optional[UpdateCheck] = None
        self._update_checking = False
        self.setWindowTitle(f"Redragon Battery Monitor {installed_version}".strip())
        self.setMinimumWidth(MIN_WIDTH)
        self._build_status_widgets()
        self._build_settings_widgets(settings, autostart_enabled)
        self._build_update_widgets(settings)
        self._build_layout()
        self.retranslate()
        self._set_icon(None, False)

    def retranslate(self) -> None:
        t = self._text.t
        self.refresh_button.setText(t("window.querying") if self._busy else t("window.refresh"))
        self.connection_caption.setText(t("window.connection"))
        self.voltage_caption.setText(t("window.voltage"))
        self.updated_caption.setText(t("window.updated"))
        self.last_good_caption.setText(t("window.last_good"))
        self.settings_box.setTitle(t("window.settings"))
        self.interval_caption.setText(t("window.interval"))
        self.threshold_caption.setText(t("window.threshold"))
        self.language_caption.setText(t("window.language"))
        self.notify_check.setText(t("window.notify"))
        self.autostart_check.setText(t("window.autostart"))
        self.note_label.setText(t("window.note"))
        self.language_combo.setItemText(0, t("window.language.auto"))
        self.language_button.setText(LANGUAGE_TOGGLE.get(self._text.language, LANGUAGE_TOGGLE["pt"])[1])
        self.update_box.setTitle(t("update.section"))
        self.version_label.setText(t("update.installed", version=self._installed_version))
        self.check_update_button.setText(t("update.check"))
        self.install_update_button.setText(t("update.install"))
        self.check_updates_check.setText(t("update.auto"))
        self._render()
        self._render_update()

    def set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.refresh_button.setEnabled(not busy)
        self.refresh_button.setText(self._text.t("window.querying" if busy else "window.refresh"))

    def show_status(self, status: BatteryStatus, last_good: Optional[BatteryStatus]) -> None:
        self._status = status
        self._last_good = last_good
        self._render()

    def show_update_checking(self) -> None:
        self._update_checking = True
        self._render_update()

    def show_update(self, check: UpdateCheck) -> None:
        self._update_checking = False
        self._update = check
        self._render_update()

    def set_autostart_checked(self, checked: bool) -> None:
        self.autostart_check.blockSignals(True)
        self.autostart_check.setChecked(checked)
        self.autostart_check.blockSignals(False)

    def closeEvent(self, event: QCloseEvent) -> None:
        if not self._hide_on_close:
            event.accept()
            return
        event.ignore()
        self.hide()

    def _render(self) -> None:
        if self._status is None:
            self.state_label.setText(self._text.t("window.querying"))
            return
        status = self._status
        self.updated_value.setText(self._text.time(status))
        self.last_good_value.setText(self._text.last_good(self._last_good))
        self.connection_value.setText(self._text.connection_label(status))
        if status.ok:
            self._show_reading(status)
            return
        self._show_unavailable(status)

    def _render_update(self) -> None:
        self.check_update_button.setEnabled(not self._update_checking)
        self.install_update_button.setVisible(self._update is not None and self._update.available)
        if self._update_checking:
            self.update_status_label.setText(self._text.t("update.checking"))
            return
        if self._update is None:
            self.update_status_label.setText("")
            return
        latest = str(self._update.latest) if self._update.latest else ""
        self.update_status_label.setText(self._text.t(UPDATE_KEYS[self._update.status], version=latest))

    def _toggle_language(self) -> None:
        target = LANGUAGE_TOGGLE.get(self._text.language, LANGUAGE_TOGGLE["pt"])[0]
        self.language_combo.setCurrentIndex(self.language_combo.findData(target))

    def _show_reading(self, status: BatteryStatus) -> None:
        reading = status.reading
        self.percent_label.setText(f"{reading.percent}%")
        self.state_label.setText(self._text.t("window.charging" if reading.charging else "window.discharging"))
        self.bar.setEnabled(True)
        self.bar.setValue(reading.percent)
        self.voltage_value.setText(f"{reading.voltage_mv} mV")
        self._set_icon(reading.percent, reading.charging)

    def _show_unavailable(self, status: BatteryStatus) -> None:
        self.percent_label.setText(EMPTY)
        self.state_label.setText(self._text.message_with_detail(status))
        self.bar.setEnabled(False)
        self.bar.setValue(0)
        self.voltage_value.setText(EMPTY)
        self._set_icon(None, False)

    def _on_threshold(self, value: int) -> None:
        self._threshold = value
        self.threshold_changed.emit(value)

    def _on_language(self, index: int) -> None:
        self.language_changed.emit(self.language_combo.itemData(index))

    def _set_icon(self, percent: Optional[int], charging: bool) -> None:
        self.icon_label.setPixmap(self._painter.pixmap(percent, charging, self._threshold, ICON_SIZE))

    @staticmethod
    def _bold_font(points: int) -> QFont:
        font = QFont()
        font.setPointSize(points)
        font.setBold(True)
        return font

    def _build_status_widgets(self) -> None:
        self.title_label = QLabel("Redragon M719RGB-PRO")
        self.title_label.setFont(self._bold_font(13))
        self.icon_label = QLabel()
        self.percent_label = QLabel(EMPTY)
        self.percent_label.setFont(self._bold_font(30))
        self.state_label = QLabel()
        self.state_label.setWordWrap(True)
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self.connection_caption, self.connection_value = QLabel(), QLabel(EMPTY)
        self.voltage_caption, self.voltage_value = QLabel(), QLabel(EMPTY)
        self.updated_caption, self.updated_value = QLabel(), QLabel(EMPTY)
        self.last_good_caption, self.last_good_value = QLabel(), QLabel(EMPTY)
        self.refresh_button = QPushButton()
        self.refresh_button.clicked.connect(self.refresh_requested)

    def _build_settings_widgets(self, settings: AppSettings, autostart_enabled: bool) -> None:
        self.interval_caption = QLabel()
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(AppSettings.INTERVAL_MIN, AppSettings.INTERVAL_MAX)
        self.interval_spin.setSuffix(" s")
        self.interval_spin.setValue(settings.interval_s)
        self.interval_spin.valueChanged.connect(self.interval_changed)
        self.threshold_caption = QLabel()
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(AppSettings.THRESHOLD_MIN, AppSettings.THRESHOLD_MAX)
        self.threshold_spin.setSuffix(" %")
        self.threshold_spin.setValue(settings.threshold)
        self.threshold_spin.valueChanged.connect(self._on_threshold)
        self.language_caption = QLabel()
        self.language_combo = QComboBox()
        for code, name in LANGUAGE_OPTIONS:
            self.language_combo.addItem(name or code, code)
        self.language_combo.setCurrentIndex(self.language_combo.findData(settings.language))
        self.language_combo.currentIndexChanged.connect(self._on_language)
        self.notify_check = QCheckBox()
        self.notify_check.setChecked(settings.notify)
        self.notify_check.toggled.connect(self.notify_changed)
        self.autostart_check = QCheckBox()
        self.autostart_check.setChecked(autostart_enabled)
        self.autostart_check.toggled.connect(self.autostart_changed)

    def _build_update_widgets(self, settings: AppSettings) -> None:
        self.header_version_label = QLabel(f"v{self._installed_version}" if self._installed_version else "")
        self.header_version_label.setStyleSheet("color: palette(placeholder-text); font-size: 10pt;")
        self.language_button = QPushButton()
        self.language_button.setFlat(True)
        self.language_button.clicked.connect(self._toggle_language)
        self.version_label = QLabel()
        self.update_status_label = QLabel()
        self.update_status_label.setWordWrap(True)
        self.check_update_button = QPushButton()
        self.check_update_button.clicked.connect(self.check_update_requested)
        self.install_update_button = QPushButton()
        self.install_update_button.setVisible(False)
        self.install_update_button.clicked.connect(self.install_update_requested)
        self.check_updates_check = QCheckBox()
        self.check_updates_check.setChecked(settings.check_updates)
        self.check_updates_check.toggled.connect(self.check_updates_changed)

    def _build_update_box(self) -> QGroupBox:
        buttons = QHBoxLayout()
        buttons.addWidget(self.check_update_button)
        buttons.addWidget(self.install_update_button)
        layout = QVBoxLayout()
        layout.addWidget(self.version_label)
        layout.addWidget(self.update_status_label)
        layout.addLayout(buttons)
        layout.addWidget(self.check_updates_check)
        self.update_box = QGroupBox()
        self.update_box.setLayout(layout)
        return self.update_box

    def _build_layout(self) -> None:
        title_row = QHBoxLayout()
        title_row.addWidget(self.title_label)
        title_row.addWidget(self.header_version_label)
        title_row.addStretch(1)
        title_row.addWidget(self.language_button)
        head = QHBoxLayout()
        head.addWidget(self.icon_label)
        column = QVBoxLayout()
        column.addWidget(self.percent_label)
        column.addWidget(self.state_label)
        head.addLayout(column, 1)
        info = QFormLayout()
        info.addRow(self.connection_caption, self.connection_value)
        info.addRow(self.voltage_caption, self.voltage_value)
        info.addRow(self.updated_caption, self.updated_value)
        info.addRow(self.last_good_caption, self.last_good_value)
        config = QFormLayout()
        config.addRow(self.interval_caption, self.interval_spin)
        config.addRow(self.threshold_caption, self.threshold_spin)
        config.addRow(self.language_caption, self.language_combo)
        config.addRow(self.notify_check)
        config.addRow(self.autostart_check)
        self.settings_box = QGroupBox()
        self.settings_box.setLayout(config)
        self.note_label = QLabel()
        self.note_label.setWordWrap(True)
        self.note_label.setStyleSheet("color: palette(placeholder-text); font-size: 9pt;")
        root = QVBoxLayout(self)
        root.addLayout(title_row)
        root.addLayout(head)
        root.addWidget(self.bar)
        root.addLayout(info)
        root.addWidget(self.refresh_button)
        root.addWidget(self.settings_box)
        root.addWidget(self._build_update_box())
        root.addWidget(self.note_label)
