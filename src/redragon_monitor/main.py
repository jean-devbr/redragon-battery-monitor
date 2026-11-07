import logging
import sys
from typing import Optional

from redragon_monitor.bootstrap.container import Container

LOG_FORMAT = "%(levelname)s %(name)s: %(message)s"


def main(argv: Optional[list[str]] = None) -> int:
    container = Container()
    try:
        from redragon_monitor.presentation.gui.gui_app import GuiApp
    except ImportError:
        print(container.translator.t("gui.missing_pyside"), file=sys.stderr)
        return 1
    args = container.gui_argument_parser().parse(sys.argv[1:] if argv is None else argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format=LOG_FORMAT)
    if args.export_icon:
        return GuiApp.export_icon(args.export_icon)
    return container.gui_app().run(minimized=args.minimized)


if __name__ == "__main__":
    sys.exit(main())
