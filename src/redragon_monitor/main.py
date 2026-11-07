import logging
import sys
from typing import Optional

LOG_FORMAT = "%(levelname)s %(name)s: %(message)s"


def main(argv: Optional[list[str]] = None) -> int:
    try:
        from redragon_monitor.presentation.gui.gui_argument_parser import GuiArgumentParser
        from redragon_monitor.presentation.gui.gui_app import GuiApp
    except ImportError:
        print("PySide6 não está instalado. Rode: .venv/bin/pip install -e '.[gui]'", file=sys.stderr)
        return 1
    from redragon_monitor.bootstrap.container import Container

    args = GuiArgumentParser().parse(sys.argv[1:] if argv is None else argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format=LOG_FORMAT)
    if args.export_icon:
        return GuiApp.export_icon(args.export_icon)
    return Container().gui_app().run(minimized=args.minimized)


if __name__ == "__main__":
    sys.exit(main())
