import sys

SPECIAL_CHARS = ' "\\`$'
GUI_MODULE = "redragon_monitor.main"


class GuiLaunchCommand:
    def __init__(self, python: str = sys.executable):
        self._python = python

    def build(self) -> str:
        return f"{self._quoted(self._python)} -m {GUI_MODULE} --minimized"

    @staticmethod
    def _quoted(path: str) -> str:
        if not any(c in path for c in SPECIAL_CHARS):
            return path
        escaped = path.replace("\\", "\\\\").replace('"', '\\"').replace("`", "\\`").replace("$", "\\$")
        return f'"{escaped}"'
