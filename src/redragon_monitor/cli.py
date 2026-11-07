import sys
from typing import Optional

from redragon_monitor.bootstrap.container import Container


def main(argv: Optional[list[str]] = None) -> int:
    return Container().cli_app().run(argv)


if __name__ == "__main__":
    sys.exit(main())
