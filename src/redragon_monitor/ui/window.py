"""Janela principal."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
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

from redragon_monitor.device.detector import ConnectionType
from redragon_monitor.services.battery_service import BatteryStatus
from redragon_monitor.ui import settings as S
from redragon_monitor.ui.icons import battery_pixmap

CONNECTION_LABELS = {
    ConnectionType.USB_C: "Cabo USB-C",
    ConnectionType.RECEIVER: "Receptor 2.4 GHz",
}


def describe_last_good(last_good: Optional[BatteryStatus]) -> str:
    if not last_good or not last_good.reading:
        return "—"
    r = last_good.reading
    state = "carregando" if r.charging else "na bateria"
    return f"{r.percent}% ({state}) às {last_good.timestamp:%H:%M:%S}"


class MainWindow(QWidget):
    refresh_requested = Signal()
    interval_changed = Signal(int)
    threshold_changed = Signal(int)
    notify_changed = Signal(bool)
    autostart_changed = Signal(bool)

    def __init__(self, settings: S.AppSettings, autostart_enabled: bool, hide_on_close: bool):
        super().__init__()
        self._hide_on_close = hide_on_close
        self._threshold = settings.threshold
        self.setWindowTitle("Redragon Battery Monitor")
        self.setMinimumWidth(380)

        title = QLabel("Redragon M719RGB-PRO")
        tf = QFont()
        tf.setPointSize(13)
        tf.setBold(True)
        title.setFont(tf)

        self.icon_label = QLabel()
        self.percent_label = QLabel("—")
        pf = QFont()
        pf.setPointSize(30)
        pf.setBold(True)
        self.percent_label.setFont(pf)
        self.state_label = QLabel("Consultando…")
        self.state_label.setWordWrap(True)

        head = QHBoxLayout()
        head.addWidget(self.icon_label)
        col = QVBoxLayout()
        col.addWidget(self.percent_label)
        col.addWidget(self.state_label)
        head.addLayout(col, 1)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)

        self.connection_value = QLabel("—")
        self.voltage_value = QLabel("—")
        self.updated_value = QLabel("—")
        self.last_good_value = QLabel("—")
        info = QFormLayout()
        info.addRow("Conexão:", self.connection_value)
        info.addRow("Tensão:", self.voltage_value)
        info.addRow("Última consulta:", self.updated_value)
        info.addRow("Última leitura válida:", self.last_good_value)

        self.refresh_button = QPushButton("Atualizar agora")
        self.refresh_button.clicked.connect(self.refresh_requested)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(S.INTERVAL_MIN, S.INTERVAL_MAX)
        self.interval_spin.setSuffix(" s")
        self.interval_spin.setValue(settings.interval_s)
        self.interval_spin.valueChanged.connect(self.interval_changed)

        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(S.THRESHOLD_MIN, S.THRESHOLD_MAX)
        self.threshold_spin.setSuffix(" %")
        self.threshold_spin.setValue(settings.threshold)
        self.threshold_spin.valueChanged.connect(self._on_threshold)

        self.notify_check = QCheckBox("Notificar bateria baixa")
        self.notify_check.setChecked(settings.notify)
        self.notify_check.toggled.connect(self.notify_changed)

        self.autostart_check = QCheckBox("Iniciar com o sistema")
        self.autostart_check.setChecked(autostart_enabled)
        self.autostart_check.toggled.connect(self.autostart_changed)

        cfg = QFormLayout()
        cfg.addRow("Intervalo de atualização:", self.interval_spin)
        cfg.addRow("Limite de bateria baixa:", self.threshold_spin)
        cfg.addRow(self.notify_check)
        cfg.addRow(self.autostart_check)
        box = QGroupBox("Configurações")
        box.setLayout(cfg)

        note = QLabel("Valores informados pelo firmware do mouse. Desligado e em repouso "
                      "não podem ser diferenciados: ambos aparecem como indisponível.")
        note.setWordWrap(True)
        note.setStyleSheet("color: palette(placeholder-text); font-size: 9pt;")

        root = QVBoxLayout(self)
        root.addWidget(title)
        root.addLayout(head)
        root.addWidget(self.bar)
        root.addLayout(info)
        root.addWidget(self.refresh_button)
        root.addWidget(box)
        root.addWidget(note)
        self._set_icon(None, False)

    def _on_threshold(self, v: int) -> None:
        self._threshold = v
        self.threshold_changed.emit(v)

    def _set_icon(self, percent: Optional[int], charging: bool) -> None:
        self.icon_label.setPixmap(battery_pixmap(percent, charging, self._threshold, 72))

    def set_busy(self, busy: bool) -> None:
        self.refresh_button.setEnabled(not busy)
        self.refresh_button.setText("Consultando…" if busy else "Atualizar agora")

    def show_status(self, s: BatteryStatus, last_good: Optional[BatteryStatus]) -> None:
        self.updated_value.setText(f"{s.timestamp:%H:%M:%S}")
        self.last_good_value.setText(describe_last_good(last_good))
        if s.ok and s.reading:
            r = s.reading
            self.percent_label.setText(f"{r.percent}%")
            self.state_label.setText("⚡ Carregando" if r.charging else "Na bateria")
            self.bar.setEnabled(True)
            self.bar.setValue(r.percent)
            self.voltage_value.setText(f"{r.voltage_mv} mV")
            self.connection_value.setText(CONNECTION_LABELS.get(s.interface.connection, "—"))
            self._set_icon(r.percent, r.charging)
        else:
            # sem leitura atual: não mostra número como se fosse atual
            self.percent_label.setText("—")
            self.state_label.setText(s.message + (f"\n{s.detail}" if s.detail else ""))
            self.bar.setEnabled(False)
            self.bar.setValue(0)
            self.voltage_value.setText("—")
            self.connection_value.setText(
                CONNECTION_LABELS.get(s.interface.connection, "—") if s.interface else "—"
            )
            self._set_icon(None, False)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._hide_on_close:
            event.ignore()
            self.hide()
        else:
            event.accept()
