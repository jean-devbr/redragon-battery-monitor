"""Aplicação gráfica (PySide6).

A consulta HID roda numa QThread para não travar a interface (pode levar até ~2 s
por interface quando o mouse está dormindo).
"""
from __future__ import annotations

import argparse
import logging
import sys
from typing import Optional


def _parse_args(argv):
    p = argparse.ArgumentParser(prog="redragon-battery-gui")
    p.add_argument("--minimized", action="store_true", help="iniciar só na bandeja")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_known_args(argv)[0]


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    try:
        from PySide6.QtWidgets import QApplication  # noqa: F401
    except ImportError:
        print("PySide6 não está instalado. Rode: .venv/bin/pip install -e '.[gui]'", file=sys.stderr)
        return 1
    from redragon_monitor.ui.app import run

    return run(minimized=args.minimized)


if __name__ == "__main__":
    sys.exit(main())
