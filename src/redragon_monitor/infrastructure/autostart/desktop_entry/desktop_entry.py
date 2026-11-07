class DesktopEntry:
    def __init__(self, exec_command: str):
        self._exec_command = exec_command

    def render(self) -> str:
        return (
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Redragon Battery Monitor\n"
            "Comment=Bateria do mouse Redragon M719RGB-PRO\n"
            f"Exec={self._exec_command}\n"
            "Icon=input-mouse\n"
            "Terminal=false\n"
            "X-GNOME-Autostart-enabled=true\n"
            "X-GNOME-Autostart-Delay=5\n"
        )
