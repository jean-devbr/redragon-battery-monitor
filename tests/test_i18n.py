import pytest

from redragon_monitor.alert.infrastructure.notify_send_notifier import NotifySendNotifier
from redragon_monitor.presentation.i18n.catalog import Catalog
from redragon_monitor.presentation.i18n.language import Language
from redragon_monitor.presentation.i18n.language_detector import LanguageDetector
from redragon_monitor.presentation.i18n.notification_texts import NotificationTexts
from fakes import make_translator


def test_catalogs_have_the_same_keys():
    assert Catalog.keys(Language.PT) == Catalog.keys(Language.EN)


@pytest.mark.parametrize(
    "environ, expected",
    [
        ({"LANG": "pt_BR.UTF-8"}, Language.PT),
        ({"LANG": "en_US.UTF-8"}, Language.EN),
        ({"LANGUAGE": "pt_BR:pt:en", "LANG": "en_US.UTF-8"}, Language.PT),
        ({"LC_ALL": "C"}, Language.EN),
        ({}, Language.EN),
        ({"LANG": "es_ES.UTF-8"}, Language.EN),
    ],
)
def test_detects_system_language(environ, expected):
    assert LanguageDetector(environ).detect() is expected


def test_explicit_preference_overrides_system():
    detector = LanguageDetector({"LANG": "pt_BR.UTF-8"})
    assert detector.resolve("en") is Language.EN
    assert detector.resolve("auto") is Language.PT


def test_translator_formats_and_switches():
    translator = make_translator(Language.PT)
    assert translator.t("cli.battery", percent=50, state="x") == "Bateria: 50% (x)"
    translator.set_language(Language.EN)
    assert translator.t("cli.battery", percent=50, state="x") == "Battery: 50% (x)"


def test_notification_uses_current_language():
    translator = make_translator(Language.EN)
    sent = []
    notifier = NotifySendNotifier(NotificationTexts(translator).low_battery, command="/bin/true")
    notifier._send = lambda title, body, urgency: sent.append((title, body)) or True
    notifier.low_battery(15)
    assert sent == [("Mouse battery low", "Redragon M719RGB-PRO at 15%. Connect the USB-C cable.")]
