from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent, QFont
from PySide6.QtWidgets import (
    QCheckBox,
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

EMPTY = "—"
ICON_SIZE = 72
MIN_WIDTH = 380
NOTE = (
    "Valores informados pelo firmware do mouse. Desligado e em repouso "
    "não podem ser diferenciados: ambos aparecem como indisponível."
)


class MainWindow(QWidget):
    refresh_requested = Signal()
    interval_changed = Signal(int)
    threshold_changed = Signal(int)
    notify_changed = Signal(bool)
    autostart_changed = Signal(bool)

    def __init__(
        self,
        settings: AppSettings,
        painter: BatteryIconPainter,
        text: StatusTextFormatter,
        autostart_enabled: bool,
        hide_on_close: bool,
    ):
        super().__init__()
        self._painter = painter
        self._text = text
        self._hide_on_close = hide_on_close
        self._threshold = settings.threshold
        self.setWindowTitle("Redragon Battery Monitor")
        self.setMinimumWidth(MIN_WIDTH)
        self._build_status_widgets()
        self._build_settings_widgets(settings, autostart_enabled)
        self._build_layout()
        self._set_icon(None, False)

    def set_busy(self, busy: bool) -> None:
        self.refresh_button.setEnabled(not busy)
        self.refresh_button.setText("Consultando…" if busy else "Atualizar agora")

    def show_status(self, status: BatteryStatus, last_good: Optional[BatteryStatus]) -> None:
        self.updated_value.setText(f"{status.timestamp:%H:%M:%S}")
        self.last_good_value.setText(self._text.last_good(last_good))
        self.connection_value.setText(self._text.connection_label(status))
        if status.ok:
            self._show_reading(status)
            return
        self._show_unavailable(status)

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

    def _show_reading(self, status: BatteryStatus) -> None:
        reading = status.reading
        self.percent_label.setText(f"{reading.percent}%")
        self.state_label.setText("⚡ Carregando" if reading.charging else "Na bateria")
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
        self.state_label = QLabel("Consultando…")
        self.state_label.setWordWrap(True)
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self.connection_value = QLabel(EMPTY)
        self.voltage_value = QLabel(EMPTY)
        self.updated_value = QLabel(EMPTY)
        self.last_good_value = QLabel(EMPTY)
        self.refresh_button = QPushButton("Atualizar agora")
        self.refresh_button.clicked.connect(self.refresh_requested)

    def _build_settings_widgets(self, settings: AppSettings, autostart_enabled: bool) -> None:
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(AppSettings.INTERVAL_MIN, AppSettings.INTERVAL_MAX)
        self.interval_spin.setSuffix(" s")
        self.interval_spin.setValue(settings.interval_s)
        self.interval_spin.valueChanged.connect(self.interval_changed)
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(AppSettings.THRESHOLD_MIN, AppSettings.THRESHOLD_MAX)
        self.threshold_spin.setSuffix(" %")
        self.threshold_spin.setValue(settings.threshold)
        self.threshold_spin.valueChanged.connect(self._on_threshold)
        self.notify_check = QCheckBox("Notificar bateria baixa")
        self.notify_check.setChecked(settings.notify)
        self.notify_check.toggled.connect(self.notify_changed)
        self.autostart_check = QCheckBox("Iniciar com o sistema")
        self.autostart_check.setChecked(autostart_enabled)
        self.autostart_check.toggled.connect(self.autostart_changed)

    def _build_layout(self) -> None:
        head = QHBoxLayout()
        head.addWidget(self.icon_label)
        column = QVBoxLayout()
        column.addWidget(self.percent_label)
        column.addWidget(self.state_label)
        head.addLayout(column, 1)
        info = QFormLayout()
        info.addRow("Conexão:", self.connection_value)
        info.addRow("Tensão:", self.voltage_value)
        info.addRow("Última consulta:", self.updated_value)
        info.addRow("Última leitura válida:", self.last_good_value)
        config = QFormLayout()
        config.addRow("Intervalo de atualização:", self.interval_spin)
        config.addRow("Limite de bateria baixa:", self.threshold_spin)
        config.addRow(self.notify_check)
        config.addRow(self.autostart_check)
        box = QGroupBox("Configurações")
        box.setLayout(config)
        note = QLabel(NOTE)
        note.setWordWrap(True)
        note.setStyleSheet("color: palette(placeholder-text); font-size: 9pt;")
        root = QVBoxLayout(self)
        root.addWidget(self.title_label)
        root.addLayout(head)
        root.addWidget(self.bar)
        root.addLayout(info)
        root.addWidget(self.refresh_button)
        root.addWidget(box)
        root.addWidget(note)
