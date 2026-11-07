import os
from typing import Mapping, Optional

from redragon_monitor.presentation.i18n.language import Language

LOCALE_VARIABLES = ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG")
AUTO = "auto"


class LanguageDetector:
    def __init__(self, environ: Optional[Mapping[str, str]] = None):
        self._environ = os.environ if environ is None else environ

    def detect(self) -> Language:
        for variable in LOCALE_VARIABLES:
            value = self._environ.get(variable, "")
            if not value:
                continue
            return Language.PT if value.lower().startswith(Language.PT.value) else Language.EN
        return Language.EN

    def resolve(self, preference: str) -> Language:
        if preference in {language.value for language in Language}:
            return Language(preference)
        return self.detect()
