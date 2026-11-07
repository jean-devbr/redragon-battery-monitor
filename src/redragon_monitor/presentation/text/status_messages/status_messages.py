from redragon_monitor.battery.domain.battery_status import BatteryStatus
from redragon_monitor.battery.domain.read_status import ReadStatus

MESSAGES = {
    ReadStatus.OK: "Leitura obtida.",
    ReadStatus.UNAVAILABLE: "Mouse indisponível (desligado ou em repouso). Mexa o mouse.",
    ReadStatus.NOT_FOUND: "Nenhum Redragon M719RGB-PRO encontrado (receptor ou cabo).",
    ReadStatus.PERMISSION_DENIED: "Sem permissão para acessar o dispositivo. Instale a regra udev.",
    ReadStatus.INVALID_RESPONSE: "O mouse respondeu com dados inválidos; leitura descartada.",
    ReadStatus.ERROR: "Erro inesperado ao consultar o dispositivo.",
}


class StatusMessages:
    def message(self, status: BatteryStatus) -> str:
        return MESSAGES[status.status]
