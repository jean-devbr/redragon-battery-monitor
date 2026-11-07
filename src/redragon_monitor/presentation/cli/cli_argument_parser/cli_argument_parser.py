import argparse
from typing import Optional

from redragon_monitor import __version__
from redragon_monitor.alert.domain.low_battery_policy.low_battery_policy import DEFAULT_THRESHOLD
from redragon_monitor.presentation.i18n.language import Language
from redragon_monitor.presentation.i18n.translator import Translator


class CliArgumentParser:
    def __init__(self, translator: Translator):
        self._translator = translator

    def parse(self, argv: Optional[list[str]]) -> argparse.Namespace:
        return self._build().parse_args(argv)

    def _build(self) -> argparse.ArgumentParser:
        t = self._translator.t
        parser = argparse.ArgumentParser(prog="redragon-battery", description=t("cli.description"))
        parser.add_argument("--json", action="store_true", help=t("cli.help.json"))
        parser.add_argument("--watch", type=float, metavar="SEG", help=t("cli.help.watch"))
        parser.add_argument("--notify", action="store_true", help=t("cli.help.notify"))
        parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD, help=t("cli.help.threshold"))
        parser.add_argument("--lang", choices=[language.value for language in Language], help=t("cli.help.lang"))
        parser.add_argument("-v", "--verbose", action="store_true", help=t("cli.help.verbose"))
        parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
        return parser
