from redragon_monitor.domain.battery_reading import BatteryReading
from redragon_monitor.infrastructure.compx.compx_power_query import CompxPowerQuery
from redragon_monitor.infrastructure.compx.compx_power_response_parser import CompxPowerResponseParser


class CompxBatteryProtocol:
    def __init__(self, query: CompxPowerQuery, parser: CompxPowerResponseParser):
        self._query = query
        self._parser = parser

    def build_query(self) -> bytes:
        return self._query.build()

    def is_response(self, data: bytes) -> bool:
        return self._parser.is_response(data)

    def parse(self, data: bytes) -> BatteryReading:
        return self._parser.parse(data)
