import json

from redragon_monitor.application.battery_monitor import BatteryMonitor
from redragon_monitor.application.low_battery_policy import LowBatteryPolicy
from redragon_monitor.domain.battery_reading import BatteryReading
from redragon_monitor.domain.battery_status import BatteryStatus
from redragon_monitor.domain.read_status import ReadStatus
from redragon_monitor.presentation.cli.cli_app import CliApp
from redragon_monitor.presentation.cli.cli_argument_parser import CliArgumentParser
from redragon_monitor.presentation.cli.exit_codes import ExitCodes
from redragon_monitor.presentation.cli.human_status_formatter import HumanStatusFormatter
from redragon_monitor.presentation.cli.json_status_formatter import JsonStatusFormatter
from redragon_monitor.presentation.cli.watch_line_formatter import WatchLineFormatter
from redragon_monitor.presentation.cli.watch_loop import WatchLoop
from redragon_monitor.presentation.text.status_messages import StatusMessages
from redragon_monitor.presentation.text.status_text_formatter import StatusTextFormatter
from fakes import FIXED_TIME, RECEIVER, RecordingNotifier

READING = BatteryReading(100, False, 0, 4137, bytes(17))
OK = BatteryStatus(ReadStatus.OK, FIXED_TIME, reading=READING, interface=RECEIVER)
UNAVAILABLE = BatteryStatus(ReadStatus.UNAVAILABLE, FIXED_TIME, interface=RECEIVER)
MESSAGES = StatusMessages()
TEXT = StatusTextFormatter(MESSAGES)


class StaticReader:
    def __init__(self, status):
        self.status = status
        self.last_good = status if status.ok else None

    def execute(self):
        return self.status


def app(status, lines):
    reader = StaticReader(status)
    return CliApp(
        parser=CliArgumentParser(),
        read_battery=reader,
        monitor_factory=lambda threshold: BatteryMonitor(reader, LowBatteryPolicy(threshold), RecordingNotifier()),
        json_formatter=JsonStatusFormatter(MESSAGES),
        human_formatter=HumanStatusFormatter(TEXT),
        line_formatter=WatchLineFormatter(TEXT),
        exit_codes=ExitCodes(),
        output=lines.append,
    )


def test_human_output_and_exit_code():
    lines = []
    assert app(OK, lines).run([]) == 0
    assert lines[0].startswith("Bateria: 100% (na bateria)")


def test_json_output():
    lines = []
    assert app(OK, lines).run(["--json"]) == 0
    data = json.loads(lines[0])
    assert (data["status"], data["percent"], data["connection"]) == ("ok", 100, "receptor-2.4ghz")


def test_unavailable_exit_code_and_no_number():
    lines = []
    assert app(UNAVAILABLE, lines).run(["--json"]) == 2
    assert "percent" not in json.loads(lines[0])


def test_watch_interval_too_short():
    assert app(OK, []).run(["--watch", "3"]) == 1


def test_watch_loop_renders_each_cycle():
    lines = []
    reader = StaticReader(OK)
    monitor = BatteryMonitor(reader, LowBatteryPolicy(20), RecordingNotifier())
    loop = WatchLoop(monitor, WatchLineFormatter(TEXT).format, lines.append, sleep=lambda _s: None)
    assert loop.run(10, notify=False, max_cycles=2) == 0
    assert len(lines) == 2 and "100%" in lines[0]
