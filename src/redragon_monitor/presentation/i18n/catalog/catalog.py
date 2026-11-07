from redragon_monitor.presentation.i18n.language import Language

PT = {
    "status.ok": "Leitura obtida.",
    "status.unavailable": "Mouse indisponível (desligado ou em repouso). Mexa o mouse.",
    "status.not_found": "Nenhum Redragon M719RGB-PRO encontrado (receptor ou cabo).",
    "status.permission_denied": "Sem permissão para acessar o dispositivo. Instale a regra udev.",
    "status.invalid_response": "O mouse respondeu com dados inválidos; leitura descartada.",
    "status.error": "Erro inesperado ao consultar o dispositivo.",
    "charge.charging": "carregando",
    "charge.discharging": "na bateria",
    "connection.usb-c": "Cabo USB-C",
    "connection.receptor-2.4ghz": "Receptor 2.4 GHz",
    "summary.last_good": "{percent}% ({state}) às {time}",
    "tray.prefix": "Mouse Redragon: ",
    "tray.querying": "consultando…",
    "tray.last_reading": "Última leitura: {summary}",
    "tray.menu.open": "Abrir",
    "tray.menu.refresh": "Atualizar agora",
    "tray.menu.quit": "Sair",
    "cli.battery": "Bateria: {percent}% ({state})",
    "cli.voltage": "Tensão:  {voltage} mV",
    "cli.connection": "Conexão: {connection} ({device})",
    "cli.detail": "Detalhe: {detail}",
    "cli.last_good": "Última leitura válida: {percent}% às {time}",
    "cli.watch_last": "[última: {percent}% às {time}]",
    "cli.watch_min": "--watch precisa ser de pelo menos {seconds} segundos.",
    "cli.description": "Bateria do Redragon M719RGB-PRO (receptor 2.4 GHz ou USB-C).",
    "cli.help.json": "saída em JSON",
    "cli.help.watch": "consulta periodicamente (mínimo 5 s)",
    "cli.help.notify": "com --watch: notifica bateria baixa",
    "cli.help.threshold": "limite de bateria baixa em %% (padrão 20)",
    "cli.help.lang": "idioma: pt ou en (padrão: idioma do sistema)",
    "cli.help.verbose": "mostra detalhes de diagnóstico",
    "gui.help.minimized": "iniciar só na bandeja",
    "gui.help.export_icon": "salva o ícone do aplicativo em PNG e sai",
    "gui.missing_pyside": "PySide6 não está instalado. Rode: .venv/bin/pip install -e '.[gui]'",
    "window.querying": "Consultando…",
    "window.refresh": "Atualizar agora",
    "window.charging": "⚡ Carregando",
    "window.discharging": "Na bateria",
    "window.connection": "Conexão:",
    "window.voltage": "Tensão:",
    "window.updated": "Última consulta:",
    "window.last_good": "Última leitura válida:",
    "window.settings": "Configurações",
    "window.interval": "Intervalo de atualização:",
    "window.threshold": "Limite de bateria baixa:",
    "window.notify": "Notificar bateria baixa",
    "window.autostart": "Iniciar com o sistema",
    "window.language": "Idioma:",
    "window.language.auto": "Automático",
    "window.note": (
        "Valores informados pelo firmware do mouse. Desligado e em repouso "
        "não podem ser diferenciados: ambos aparecem como indisponível."
    ),
    "autostart.title": "Iniciar com o sistema",
    "autostart.error": "Não foi possível alterar: {error}",
    "notify.title": "Bateria do mouse baixa",
    "notify.body": "Redragon M719RGB-PRO com {percent}%. Conecte o cabo USB-C.",
}

EN = {
    "status.ok": "Reading obtained.",
    "status.unavailable": "Mouse unavailable (off or asleep). Move the mouse.",
    "status.not_found": "No Redragon M719RGB-PRO found (receiver or cable).",
    "status.permission_denied": "No permission to access the device. Install the udev rule.",
    "status.invalid_response": "The mouse sent invalid data; reading discarded.",
    "status.error": "Unexpected error while querying the device.",
    "charge.charging": "charging",
    "charge.discharging": "on battery",
    "connection.usb-c": "USB-C cable",
    "connection.receptor-2.4ghz": "2.4 GHz receiver",
    "summary.last_good": "{percent}% ({state}) at {time}",
    "tray.prefix": "Redragon mouse: ",
    "tray.querying": "querying…",
    "tray.last_reading": "Last reading: {summary}",
    "tray.menu.open": "Open",
    "tray.menu.refresh": "Refresh now",
    "tray.menu.quit": "Quit",
    "cli.battery": "Battery: {percent}% ({state})",
    "cli.voltage": "Voltage: {voltage} mV",
    "cli.connection": "Connection: {connection} ({device})",
    "cli.detail": "Detail: {detail}",
    "cli.last_good": "Last valid reading: {percent}% at {time}",
    "cli.watch_last": "[last: {percent}% at {time}]",
    "cli.watch_min": "--watch must be at least {seconds} seconds.",
    "cli.description": "Redragon M719RGB-PRO battery (2.4 GHz receiver or USB-C).",
    "cli.help.json": "JSON output",
    "cli.help.watch": "query periodically (minimum 5 s)",
    "cli.help.notify": "with --watch: notify when battery is low",
    "cli.help.threshold": "low battery threshold in %% (default 20)",
    "cli.help.lang": "language: pt or en (default: system language)",
    "cli.help.verbose": "show diagnostic details",
    "gui.help.minimized": "start in the tray only",
    "gui.help.export_icon": "save the application icon as PNG and exit",
    "gui.missing_pyside": "PySide6 is not installed. Run: .venv/bin/pip install -e '.[gui]'",
    "window.querying": "Querying…",
    "window.refresh": "Refresh now",
    "window.charging": "⚡ Charging",
    "window.discharging": "On battery",
    "window.connection": "Connection:",
    "window.voltage": "Voltage:",
    "window.updated": "Last query:",
    "window.last_good": "Last valid reading:",
    "window.settings": "Settings",
    "window.interval": "Refresh interval:",
    "window.threshold": "Low battery threshold:",
    "window.notify": "Notify low battery",
    "window.autostart": "Start with the system",
    "window.language": "Language:",
    "window.language.auto": "Automatic",
    "window.note": (
        "Values reported by the mouse firmware. Off and asleep cannot be "
        "told apart: both are shown as unavailable."
    ),
    "autostart.title": "Start with the system",
    "autostart.error": "Could not change it: {error}",
    "notify.title": "Mouse battery low",
    "notify.body": "Redragon M719RGB-PRO at {percent}%. Connect the USB-C cable.",
}

ENTRIES = {Language.PT: PT, Language.EN: EN}
FALLBACK = Language.EN


class Catalog:
    def template(self, language: Language, key: str) -> str:
        entries = ENTRIES.get(language, ENTRIES[FALLBACK])
        if key in entries:
            return entries[key]
        return ENTRIES[FALLBACK][key]

    @staticmethod
    def keys(language: Language) -> set[str]:
        return set(ENTRIES[language])
