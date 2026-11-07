from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Optional

from redragon_monitor.device.battery_protocol import (
    BatteryReading,
    ProtocolError,
    build_power_query,
    is_power_response,
    parse_power_response,
)
from redragon_monitor.device.detector import DeviceInterface, find_interfaces
from redragon_monitor.device.hidraw_transport import HidrawTransport

log = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 2.0


class Status(str, Enum):
    OK = "ok"
    UNAVAILABLE = "unavailable"
    NOT_FOUND = "not_found"
    PERMISSION_DENIED = "permission_denied"
    INVALID_RESPONSE = "invalid_response"
    ERROR = "error"


MESSAGES = {
    Status.OK: "Leitura obtida.",
    Status.UNAVAILABLE: "Mouse indisponível (desligado ou em repouso). Mexa o mouse.",
    Status.NOT_FOUND: "Nenhum Redragon M719RGB-PRO encontrado (receptor ou cabo).",
    Status.PERMISSION_DENIED: "Sem permissão para acessar o dispositivo. Instale a regra udev.",
    Status.INVALID_RESPONSE: "O mouse respondeu com dados inválidos; leitura descartada.",
    Status.ERROR: "Erro inesperado ao consultar o dispositivo.",
}


@dataclass(frozen=True)
class BatteryStatus:
    status: Status
    timestamp: datetime
    reading: Optional[BatteryReading] = None
    interface: Optional[DeviceInterface] = None
    detail: str = ""
    message: str = field(default="")

    def __post_init__(self):
        if not self.message:
            object.__setattr__(self, "message", MESSAGES[self.status])

    @property
    def ok(self) -> bool:
        return self.status is Status.OK


Finder = Callable[[], list[DeviceInterface]]
TransportFactory = Callable[[str], HidrawTransport]


class BatteryService:
    def __init__(
        self,
        finder: Finder = find_interfaces,
        transport_factory: TransportFactory = HidrawTransport,
        timeout: float = DEFAULT_TIMEOUT,
        clock: Callable[[], datetime] = datetime.now,
    ):
        self._finder = finder
        self._transport_factory = transport_factory
        self._timeout = timeout
        self._clock = clock
        self.last_good: Optional[BatteryStatus] = None

    def read(self) -> BatteryStatus:
        interfaces = self._finder()
        if not interfaces:
            return self._result(Status.NOT_FOUND)

        denied = 0
        invalid: Optional[BatteryStatus] = None
        query = build_power_query()
        for iface in interfaces:
            try:
                with self._transport_factory(iface.hidraw_path) as t:
                    raw = t.transact(query, is_power_response, self._timeout)
            except PermissionError:
                denied += 1
                continue
            except OSError as e:
                log.debug("falha em %s: %s", iface.hidraw_path, e)
                continue
            if raw is None:
                log.debug("sem resposta em %s", iface.hidraw_path)
                continue
            try:
                reading = parse_power_response(raw)
            except ProtocolError as e:
                log.warning("resposta inválida em %s: %s", iface.hidraw_path, e)
                invalid = self._result(Status.INVALID_RESPONSE, interface=iface, detail=str(e))
                continue
            result = self._result(Status.OK, reading=reading, interface=iface)
            self.last_good = result
            return result

        if denied == len(interfaces):
            return self._result(Status.PERMISSION_DENIED)
        if invalid is not None:
            return invalid
        return self._result(Status.UNAVAILABLE, interface=interfaces[0])

    def _result(self, status: Status, **kw) -> BatteryStatus:
        return BatteryStatus(status=status, timestamp=self._clock(), **kw)
