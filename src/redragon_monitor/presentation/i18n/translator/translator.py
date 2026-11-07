from redragon_monitor.presentation.i18n.catalog import Catalog
from redragon_monitor.presentation.i18n.language import Language


class Translator:
    def __init__(self, catalog: Catalog, language: Language):
        self._catalog = catalog
        self._language = language

    @property
    def language(self) -> Language:
        return self._language

    def set_language(self, language: Language) -> None:
        self._language = language

    def t(self, key: str, **values) -> str:
        template = self._catalog.template(self._language, key)
        if not values:
            return template
        return template.format(**values)
