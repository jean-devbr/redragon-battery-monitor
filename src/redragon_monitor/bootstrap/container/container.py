from __future__ import annotations

from typing import Optional

from redragon_monitor.alert.application.battery_monitor import BatteryMonitor
from redragon_monitor.alert.domain.low_battery_policy import LowBatteryPolicy
from redragon_monitor.alert.infrastructure.notify_send_notifier import NotifySendNotifier
from redragon_monitor.autostart.infrastructure.gui_launch_command import GuiLaunchCommand
from redragon_monitor.autostart.infrastructure.xdg_autostart import XdgAutostart
from redragon_monitor.battery.application.read_battery import ReadBatteryUseCase
from redragon_monitor.battery.infrastructure.compx.compx_battery_protocol import CompxBatteryProtocol
from redragon_monitor.battery.infrastructure.compx.compx_checksum import CompxChecksum
from redragon_monitor.battery.infrastructure.compx.compx_power_query import CompxPowerQuery
from redragon_monitor.battery.infrastructure.compx.compx_power_response_parser import CompxPowerResponseParser
from redragon_monitor.battery.infrastructure.hidraw.hidraw_transport import HidrawTransport
from redragon_monitor.device.infrastructure.hid.hid_item_reader import HidItemReader
from redragon_monitor.device.infrastructure.hid.vendor_report_matcher import VendorReportMatcher
from redragon_monitor.device.infrastructure.models.redragon_m719 import RedragonM719
from redragon_monitor.device.infrastructure.sysfs.sysfs_device_detector import SysfsDeviceDetector
from redragon_monitor.presentation.cli.cli_app import CliApp
from redragon_monitor.presentation.cli.cli_argument_parser import CliArgumentParser
from redragon_monitor.presentation.cli.exit_codes import ExitCodes
from redragon_monitor.presentation.cli.human_status_formatter import HumanStatusFormatter
from redragon_monitor.presentation.cli.json_status_formatter import JsonStatusFormatter
from redragon_monitor.presentation.cli.watch_line_formatter import WatchLineFormatter
from redragon_monitor.presentation.i18n.catalog import Catalog
from redragon_monitor.presentation.i18n.language_detector import LanguageDetector
from redragon_monitor.presentation.i18n.notification_texts import NotificationTexts
from redragon_monitor.presentation.i18n.translator import Translator
from redragon_monitor.presentation.text.status_messages import StatusMessages
from redragon_monitor.presentation.text.status_text_formatter import StatusTextFormatter
from redragon_monitor.shared.infrastructure.system_clock import SystemClock
from redragon_monitor import __version__
from redragon_monitor.update.application.check_for_update import CheckForUpdateUseCase
from redragon_monitor.update.domain.version import Version
from redragon_monitor.update.infrastructure.github_stable_ref_source import GitHubStableRefSource
from redragon_monitor.update.infrastructure.terminal_update_launcher import TerminalUpdateLauncher

REPOSITORY_URL = "https://github.com/jean-devbr/redragon-battery-monitor"
INSTALLER_URL = "https://raw.githubusercontent.com/jean-devbr/redragon-battery-monitor/main/get.sh"


class Container:
    def __init__(self):
        self._clock = SystemClock()
        self._detector = LanguageDetector()
        self._translator = Translator(Catalog(), self._detector.detect())
        self._messages = StatusMessages(self._translator)
        self._text = StatusTextFormatter(self._messages, self._translator)
        self._read_battery: Optional[ReadBatteryUseCase] = None

    @property
    def translator(self) -> Translator:
        return self._translator

    def read_battery(self) -> ReadBatteryUseCase:
        if self._read_battery is None:
            self._read_battery = self._build_read_battery()
        return self._read_battery

    def battery_monitor(self, threshold: int) -> BatteryMonitor:
        notifier = NotifySendNotifier(NotificationTexts(self._translator).low_battery)
        return BatteryMonitor(self.read_battery(), LowBatteryPolicy(threshold), notifier)

    def autostart(self) -> XdgAutostart:
        return XdgAutostart(GuiLaunchCommand())

    def cli_app(self) -> CliApp:
        return CliApp(
            parser=CliArgumentParser(self._translator),
            read_battery=self.read_battery(),
            monitor_factory=self.battery_monitor,
            json_formatter=JsonStatusFormatter(self._messages),
            human_formatter=HumanStatusFormatter(self._text),
            line_formatter=WatchLineFormatter(self._text),
            exit_codes=ExitCodes(),
            translator=self._translator,
        )

    def check_for_update(self) -> CheckForUpdateUseCase:
        return CheckForUpdateUseCase(GitHubStableRefSource(INSTALLER_URL), Version.parse(__version__))

    def update_launcher(self) -> TerminalUpdateLauncher:
        return TerminalUpdateLauncher(INSTALLER_URL)

    def gui_argument_parser(self):
        from redragon_monitor.presentation.gui.gui_argument_parser import GuiArgumentParser

        return GuiArgumentParser(self._translator)

    def gui_app(self):
        from redragon_monitor.presentation.gui.gui_app import GuiApp

        return GuiApp(
            self.battery_monitor,
            self.autostart(),
            self._clock,
            self._text,
            self._translator,
            self._detector,
            self.check_for_update(),
            self.update_launcher(),
            REPOSITORY_URL,
        )

    def _build_read_battery(self) -> ReadBatteryUseCase:
        spec = RedragonM719.spec()
        matcher = VendorReportMatcher(HidItemReader(), spec.usage_page, spec.report_id, spec.report_bytes)
        checksum = CompxChecksum()
        protocol = CompxBatteryProtocol(CompxPowerQuery(checksum), CompxPowerResponseParser(checksum))
        return ReadBatteryUseCase(SysfsDeviceDetector(spec, matcher), HidrawTransport, protocol, self._clock)
