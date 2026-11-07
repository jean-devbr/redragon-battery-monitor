from redragon_monitor.presentation.i18n.translator import Translator


class NotificationTexts:
    def __init__(self, translator: Translator):
        self._translator = translator

    def low_battery(self, percent: int) -> tuple[str, str]:
        return self._translator.t("notify.title"), self._translator.t("notify.body", percent=percent)
