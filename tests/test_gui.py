import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from redragon_monitor.battery.domain.battery_reading import BatteryReading
from redragon_monitor.battery.domain.battery_status import BatteryStatus
from redragon_monitor.battery.domain.read_status import ReadStatus
from redragon_monitor.presentation.gui.app_settings import AppSettings
from redragon_monitor.presentation.gui.battery_icon_painter import BatteryIconPainter
from redragon_monitor.presentation.gui.main_window import MainWindow
from redragon_monitor.presentation.text.status_messages import StatusMessages
from redragon_monitor.presentation.text.status_text_formatter import StatusTextFormatter
from fakes import FIXED_TIME, RECEIVER, make_translator
from redragon_monitor.presentation.i18n.language import Language

TRANSLATOR = make_translator()
TEXT = StatusTextFormatter(StatusMessages(TRANSLATOR), TRANSLATOR)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def settings(tmp_path):
    return AppSettings(QSettings(str(tmp_path / "s.conf"), QSettings.IniFormat))


def ok(percent, charging=False):
    reading = BatteryReading(percent, charging, int(charging), 4137, b"")
    return BatteryStatus(ReadStatus.OK, FIXED_TIME, reading=reading, interface=RECEIVER)


def window(settings):
    return MainWindow(settings, BatteryIconPainter(), TEXT, False, hide_on_close=False)


def test_window_shows_reading(app, settings):
    w = window(settings)
    w.show_status(ok(80), None)
    assert w.percent_label.text() == "80%"
    assert w.bar.value() == 80
    assert w.connection_value.text() == "Receptor 2.4 GHz"


def test_window_never_shows_old_number_as_current(app, settings):
    w = window(settings)
    w.show_status(BatteryStatus(ReadStatus.UNAVAILABLE, FIXED_TIME, interface=RECEIVER), ok(80))
    assert w.percent_label.text() == "—"
    assert w.bar.value() == 0
    assert "80%" in w.last_good_value.text()


def test_tooltip():
    assert TEXT.tooltip(ok(55, True), None) == "Mouse Redragon: 55% (carregando)"
    tooltip = TEXT.tooltip(BatteryStatus(ReadStatus.UNAVAILABLE, FIXED_TIME), ok(55))
    assert "indisponível" in tooltip and "55%" in tooltip


def test_settings_clamped(settings):
    settings.interval_s = 1
    settings.threshold = 99
    assert settings.interval_s == 10 and settings.threshold == 50


def test_icon_painter_sizes(app):
    painter = BatteryIconPainter()
    assert painter.pixmap(50, size=22).width() == 22
    assert not painter.icon(None).isNull()
    assert painter.level_color(10).name() == "#d0342c"


def test_window_retranslates_to_english(app, settings):
    translator = make_translator()
    text = StatusTextFormatter(StatusMessages(translator), translator)
    w = MainWindow(settings, BatteryIconPainter(), text, False, hide_on_close=False)
    w.show_status(ok(80), None)
    assert w.state_label.text() == "Na bateria"
    translator.set_language(Language.EN)
    w.retranslate()
    assert w.state_label.text() == "On battery"
    assert w.refresh_button.text() == "Refresh now"
    assert w.connection_value.text() == "2.4 GHz receiver"
    assert w.settings_box.title() == "Settings"


def test_language_setting_defaults_to_auto(settings):
    assert settings.language == "auto"
    settings.language = "en"
    assert settings.language == "en"
    settings.language = "xx"
    assert settings.language == "auto"


def test_language_button_toggles_language(app, settings):
    translator = make_translator()
    text = StatusTextFormatter(StatusMessages(translator), translator)
    w = MainWindow(settings, BatteryIconPainter(), text, False, hide_on_close=False)
    chosen = []
    w.language_changed.connect(chosen.append)
    assert w.language_button.text() == "🌐 English"
    w.language_button.click()
    assert chosen == ["en"]


def test_update_section_states(app, settings):
    from redragon_monitor.update.domain.update_check import UpdateCheck
    from redragon_monitor.update.domain.update_status import UpdateStatus
    from redragon_monitor.update.domain.version import Version

    w = MainWindow(settings, BatteryIconPainter(), TEXT, False, hide_on_close=False, installed_version="0.4.0")
    assert w.version_label.text() == "Versão instalada: 0.4.0"
    assert w.windowTitle() == "Redragon Battery Monitor 0.4.0"
    w.show_update_checking()
    assert w.update_status_label.text() == "Verificando atualizações…"
    assert not w.check_update_button.isEnabled()
    w.show_update(UpdateCheck(UpdateStatus.AVAILABLE, Version(0, 4, 0), Version(0, 5, 0)))
    assert w.update_status_label.text() == "Nova versão disponível: 0.5.0"
    assert not w.install_update_button.isHidden()
    w.show_update(UpdateCheck(UpdateStatus.UP_TO_DATE, Version(0, 4, 0), Version(0, 4, 0)))
    assert w.install_update_button.isHidden()
    w.show_update(UpdateCheck(UpdateStatus.FAILED, Version(0, 4, 0)))
    assert "Não foi possível" in w.update_status_label.text()


def test_check_updates_setting(settings):
    assert settings.check_updates
    settings.check_updates = False
    assert not settings.check_updates


def test_github_button_requests_repository(app, settings):
    w = window(settings)
    requested = []
    w.repository_requested.connect(lambda: requested.append(True))
    assert w.github_button.text() == "GitHub"
    assert "GitHub" in w.github_button.toolTip()
    assert not w.github_button.icon().isNull()
    w.github_button.click()
    assert requested == [True]


def test_github_icon_renders(app):
    from PySide6.QtGui import QColor

    from redragon_monitor.presentation.gui.github_icon import GithubIcon

    image = GithubIcon().pixmap(QColor("#000000"), 32).toImage()
    opaque = sum(1 for x in range(32) for y in range(32) if image.pixelColor(x, y).alpha() > 0)
    assert 200 < opaque < 32 * 32


def test_unavailable_tells_user_to_press_refresh(app, settings):
    translator = make_translator()
    text = StatusTextFormatter(StatusMessages(translator), translator)
    w = MainWindow(settings, BatteryIconPainter(), text, False, hide_on_close=False)
    w.show_status(BatteryStatus(ReadStatus.UNAVAILABLE, FIXED_TIME, interface=RECEIVER), None)
    assert "Atualizar agora" in w.state_label.text() and "repouso" in w.state_label.text()
    translator.set_language(Language.EN)
    w.retranslate()
    assert "Refresh now" in w.state_label.text()


def test_other_failures_keep_their_message(app, settings):
    w = window(settings)
    w.show_status(BatteryStatus(ReadStatus.PERMISSION_DENIED, FIXED_TIME), None)
    assert "permissão" in w.state_label.text()
