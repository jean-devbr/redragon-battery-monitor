import os
from pathlib import Path
from typing import Optional

from redragon_monitor.autostart.infrastructure.desktop_entry import DesktopEntry
from redragon_monitor.autostart.infrastructure.gui_launch_command import GuiLaunchCommand

DESKTOP_FILE = "redragon-battery-monitor.desktop"


class XdgAutostart:
    def __init__(self, launch_command: GuiLaunchCommand, config_home: Optional[str] = None):
        self._launch_command = launch_command
        self._config_home = config_home

    @property
    def path(self) -> Path:
        base = self._config_home or os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
        return Path(base, "autostart", DESKTOP_FILE)

    def is_enabled(self) -> bool:
        return self.path.is_file()

    def enable(self) -> Path:
        path = self.path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(DesktopEntry(self._launch_command.build()).render(), encoding="utf-8")
        return path

    def disable(self) -> None:
        self.path.unlink(missing_ok=True)
