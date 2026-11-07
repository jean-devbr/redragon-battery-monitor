import os
from datetime import datetime

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from redragon_monitor.device.battery_protocol import BatteryReading
from redragon_monitor.device.detector import ConnectionType, DeviceInterface
from redragon_monitor.services.battery_service import BatteryStatus, Status
from redragon_monitor.ui.settings import AppSettings
from redragon_monitor.ui.tray import tooltip_text
from redragon_monitor.ui.window import MainWindow

T = datetime(2026, 11, 6, 23, 0, 0)
RECV = DeviceInterface(0xF5D5, ConnectionType.RECEIVER, "/dev/hidraw1", "")


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def settings(tmp_path):
    return AppSettings(QSettings(str(tmp_path / "s.conf"), QSettings.IniFormat))


def ok(pct, charging=False):
    return BatteryStatus(Status.OK, T, BatteryReading(pct, charging, int(charging), 4137, b""), RECV)


def test_window_shows_reading(app, settings):
    w = MainWindow(settings, False, hide_on_close=False)
    w.show_status(ok(80), None)
    assert w.percent_label.text() == "80%"
    assert w.bar.value() == 80
    assert w.connection_value.text() == "Receptor 2.4 GHz"


def test_window_never_shows_old_number_as_current(app, settings):
    w = MainWindow(settings, False, hide_on_close=False)
    good = ok(80)
    w.show_status(BatteryStatus(Status.UNAVAILABLE, T, interface=RECV), good)
    assert w.percent_label.text() == "—"
    assert w.bar.value() == 0
    assert "80%" in w.last_good_value.text()


def test_tooltip(app):
    assert tooltip_text(ok(55, True), None) == "Mouse Redragon: 55% (carregando)"
    t = tooltip_text(BatteryStatus(Status.UNAVAILABLE, T), ok(55))
    assert "indisponível" in t and "55%" in t


def test_settings_clamped(settings):
    settings.interval_s = 1
    settings.threshold = 99
    assert settings.interval_s == 10 and settings.threshold == 50
