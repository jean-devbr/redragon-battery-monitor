"""Iniciar com o sistema via ~/.config/autostart (padrão XDG, funciona no GNOME)."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

DESKTOP_FILE = "redragon-battery-monitor.desktop"


def autostart_file(config_home: Optional[str] = None) -> Path:
    base = config_home or os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return Path(base, "autostart", DESKTOP_FILE)


def default_exec() -> str:
    """Comando que abre a GUI minimizada na bandeja usando o mesmo Python (venv) atual."""
    py = sys.executable
    if any(c in py for c in ' "\\`$'):
        py = '"' + py.replace("\\", "\\\\").replace('"', '\\"').replace("`", "\\`").replace("$", "\\$") + '"'
    return f"{py} -m redragon_monitor.main --minimized"


def desktop_entry(exec_cmd: str) -> str:
    return (
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=Redragon Battery Monitor\n"
        "Comment=Bateria do mouse Redragon M719RGB-PRO\n"
        f"Exec={exec_cmd}\n"
        "Icon=input-mouse\n"
        "Terminal=false\n"
        "X-GNOME-Autostart-enabled=true\n"
        "X-GNOME-Autostart-Delay=5\n"
    )


def is_enabled(config_home: Optional[str] = None) -> bool:
    return autostart_file(config_home).is_file()


def enable(exec_cmd: Optional[str] = None, config_home: Optional[str] = None) -> Path:
    path = autostart_file(config_home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(desktop_entry(exec_cmd or default_exec()), encoding="utf-8")
    return path


def disable(config_home: Optional[str] = None) -> None:
    autostart_file(config_home).unlink(missing_ok=True)
