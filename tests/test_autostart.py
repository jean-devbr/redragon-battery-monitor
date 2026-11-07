import sys

from redragon_monitor.infrastructure.autostart.gui_launch_command import GuiLaunchCommand
from redragon_monitor.infrastructure.autostart.xdg_autostart import XdgAutostart


def test_enable_disable_roundtrip(tmp_path):
    autostart = XdgAutostart(GuiLaunchCommand("/opt/venv/bin/python"), config_home=str(tmp_path))
    assert not autostart.is_enabled()
    path = autostart.enable()
    assert path == tmp_path / "autostart" / "redragon-battery-monitor.desktop"
    text = path.read_text()
    assert "Exec=/opt/venv/bin/python -m redragon_monitor.main --minimized" in text
    assert "Type=Application" in text
    assert autostart.is_enabled()
    autostart.disable()
    assert not autostart.is_enabled()
    autostart.disable()


def test_launch_command_uses_current_python():
    command = GuiLaunchCommand().build()
    assert command.startswith(sys.executable)
    assert command.endswith("-m redragon_monitor.main --minimized")


def test_launch_command_quotes_paths_with_spaces():
    assert GuiLaunchCommand("/opt/my venv/python").build().startswith('"/opt/my venv/python"')
