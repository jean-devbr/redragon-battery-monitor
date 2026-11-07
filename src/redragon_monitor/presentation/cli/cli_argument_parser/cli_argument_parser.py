import argparse
from typing import Optional

from redragon_monitor import __version__
from redragon_monitor.application.low_battery_policy.low_battery_policy import DEFAULT_THRESHOLD


class CliArgumentParser:
    def parse(self, argv: Optional[list[str]]) -> argparse.Namespace:
        return self._build().parse_args(argv)

    @staticmethod
    def _build() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="redragon-battery",
            description="Bateria do Redragon M719RGB-PRO (receptor 2.4 GHz ou USB-C).",
        )
        parser.add_argument("--json", action="store_true", help="saída em JSON")
        parser.add_argument("--watch", type=float, metavar="SEG", help="consulta periodicamente (mínimo 5 s)")
        parser.add_argument("--notify", action="store_true", help="com --watch: notifica bateria baixa")
        parser.add_argument(
            "--threshold", type=int, default=DEFAULT_THRESHOLD, help="limite de bateria baixa em %% (padrão 20)"
        )
        parser.add_argument("-v", "--verbose", action="store_true")
        parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
        return parser
