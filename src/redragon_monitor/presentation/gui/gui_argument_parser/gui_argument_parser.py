import argparse
from typing import Optional

from redragon_monitor.presentation.i18n.translator import Translator


class GuiArgumentParser:
    def __init__(self, translator: Translator):
        self._translator = translator

    def parse(self, argv: Optional[list[str]]) -> argparse.Namespace:
        t = self._translator.t
        parser = argparse.ArgumentParser(prog="redragon-battery-gui")
        parser.add_argument("--minimized", action="store_true", help=t("gui.help.minimized"))
        parser.add_argument("--export-icon", metavar="PNG", help=t("gui.help.export_icon"))
        parser.add_argument("-v", "--verbose", action="store_true", help=t("cli.help.verbose"))
        return parser.parse_known_args(argv)[0]
