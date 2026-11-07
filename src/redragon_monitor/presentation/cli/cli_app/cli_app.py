import logging
import sys
from typing import Callable, Optional

from redragon_monitor.application.battery_monitor import BatteryMonitor
from redragon_monitor.application.read_battery import ReadBatteryUseCase
from redragon_monitor.presentation.cli.cli_argument_parser import CliArgumentParser
from redragon_monitor.presentation.cli.exit_codes import ExitCodes
from redragon_monitor.presentation.cli.human_status_formatter import HumanStatusFormatter
from redragon_monitor.presentation.cli.json_status_formatter import JsonStatusFormatter
from redragon_monitor.presentation.cli.watch_line_formatter import WatchLineFormatter
from redragon_monitor.presentation.cli.watch_loop import WatchLoop

MIN_WATCH_INTERVAL = 5
LOG_FORMAT = "%(levelname)s %(name)s: %(message)s"


class CliApp:
    def __init__(
        self,
        parser: CliArgumentParser,
        read_battery: ReadBatteryUseCase,
        monitor_factory: Callable[[int], BatteryMonitor],
        json_formatter: JsonStatusFormatter,
        human_formatter: HumanStatusFormatter,
        line_formatter: WatchLineFormatter,
        exit_codes: ExitCodes,
        output: Callable[[str], None] = print,
    ):
        self._parser = parser
        self._read_battery = read_battery
        self._monitor_factory = monitor_factory
        self._json = json_formatter
        self._human = human_formatter
        self._line = line_formatter
        self._exit_codes = exit_codes
        self._output = output

    def run(self, argv: Optional[list[str]] = None) -> int:
        args = self._parser.parse(argv)
        logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING, format=LOG_FORMAT)
        if args.watch is not None and args.watch < MIN_WATCH_INTERVAL:
            print(f"--watch precisa ser de pelo menos {MIN_WATCH_INTERVAL} segundos.", file=sys.stderr)
            return self._exit_codes.FAILURE
        if args.watch is not None:
            return self._watch(args)
        status = self._read_battery.execute()
        self._output(self._json.format(status) if args.json else self._human.format(status))
        return self._exit_codes.for_status(status.status)

    def _watch(self, args) -> int:
        render = (lambda status, _last: self._json.format(status)) if args.json else self._line.format
        loop = WatchLoop(self._monitor_factory(args.threshold), render, self._flushed_output)
        return loop.run(args.watch, notify=args.notify)

    def _flushed_output(self, text: str) -> None:
        self._output(text)
        sys.stdout.flush()
