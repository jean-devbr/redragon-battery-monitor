import argparse
from typing import Optional


class GuiArgumentParser:
    def parse(self, argv: Optional[list[str]]) -> argparse.Namespace:
        parser = argparse.ArgumentParser(prog="redragon-battery-gui")
        parser.add_argument("--minimized", action="store_true", help="iniciar só na bandeja")
        parser.add_argument("--export-icon", metavar="ARQUIVO", help="salva o ícone do aplicativo em PNG e sai")
        parser.add_argument("-v", "--verbose", action="store_true")
        return parser.parse_known_args(argv)[0]
