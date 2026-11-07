import logging
import shlex
import shutil
import subprocess
from typing import Callable, Optional

log = logging.getLogger(__name__)

TERMINALS = (
    ("gnome-terminal", ("--",)),
    ("x-terminal-emulator", ("-e",)),
    ("konsole", ("-e",)),
    ("xterm", ("-e",)),
)
GUI_PATH = '"${XDG_DATA_HOME:-$HOME/.local/share}/redragon-battery-monitor/venv/bin/redragon-battery-gui"'
PROMPTS = {"pt": "Pressione Enter para fechar.", "en": "Press Enter to close."}


class TerminalUpdateLauncher:
    def __init__(
        self,
        installer_url: str,
        which: Callable[[str], Optional[str]] = shutil.which,
        spawn: Callable[[list[str]], object] = subprocess.Popen,
    ):
        self._installer_url = installer_url
        self._which = which
        self._spawn = spawn

    def manual_command(self) -> str:
        return f"curl -fsSL {self._installer_url} | bash"

    def launch(self, language: str) -> bool:
        terminal = self._find_terminal()
        if terminal is None:
            log.warning("nenhum terminal encontrado para atualizar")
            return False
        path, separator = terminal
        try:
            self._spawn([path, *separator, "bash", "-c", self.script(language)])
        except OSError as error:
            log.warning("falha ao abrir o terminal: %s", error)
            return False
        return True

    def script(self, language: str) -> str:
        prompt = shlex.quote(PROMPTS.get(language, PROMPTS["en"]))
        url = shlex.quote(self._installer_url)
        return (
            f"curl -fsSL {url} | REDRAGON_LANG={shlex.quote(language)} bash;"
            f" setsid -f {GUI_PATH} >/dev/null 2>&1; echo; read -rp {prompt} _"
        )

    def _find_terminal(self):
        for name, separator in TERMINALS:
            path = self._which(name)
            if path:
                return path, separator
        return None
