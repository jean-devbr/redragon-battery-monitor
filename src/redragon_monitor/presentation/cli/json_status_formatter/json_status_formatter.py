import json

from redragon_monitor.domain.battery_status import BatteryStatus
from redragon_monitor.presentation.text.status_messages import StatusMessages


class JsonStatusFormatter:
    def __init__(self, messages: StatusMessages):
        self._messages = messages

    def format(self, status: BatteryStatus) -> str:
        return json.dumps(self._to_dict(status), ensure_ascii=False)

    def _to_dict(self, status: BatteryStatus) -> dict:
        data = {
            "status": status.status.value,
            "message": self._messages.message(status),
            "timestamp": status.timestamp.isoformat(timespec="seconds"),
        }
        data.update(self._interface_fields(status))
        data.update(self._reading_fields(status))
        if status.detail:
            data["detail"] = status.detail
        return data

    @staticmethod
    def _interface_fields(status: BatteryStatus) -> dict:
        if status.interface is None:
            return {}
        return {"connection": status.interface.connection.value, "device": status.interface.hidraw_path}

    @staticmethod
    def _reading_fields(status: BatteryStatus) -> dict:
        if not status.ok:
            return {}
        reading = status.reading
        return {
            "percent": reading.percent,
            "charging": reading.charging,
            "charging_raw": reading.charging_raw,
            "voltage_mv": reading.voltage_mv,
            "raw": reading.raw.hex(" "),
        }
