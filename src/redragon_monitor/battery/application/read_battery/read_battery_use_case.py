from __future__ import annotations

import logging
from typing import Optional

from redragon_monitor.battery.application.ports.battery_protocol import BatteryProtocol
from redragon_monitor.shared.application.ports.clock import Clock
from redragon_monitor.device.application.ports.device_detector import DeviceDetector
from redragon_monitor.battery.application.ports.transport_factory import TransportFactory
from redragon_monitor.battery.domain.battery_status import BatteryStatus
from redragon_monitor.device.domain.device_interface import DeviceInterface
from redragon_monitor.battery.domain.protocol_error import ProtocolError
from redragon_monitor.battery.domain.read_status import ReadStatus

log = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 2.0


class ReadBatteryUseCase:
    def __init__(
        self,
        detector: DeviceDetector,
        transport_factory: TransportFactory,
        protocol: BatteryProtocol,
        clock: Clock,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self._detector = detector
        self._transport_factory = transport_factory
        self._protocol = protocol
        self._clock = clock
        self._timeout = timeout
        self._last_good: Optional[BatteryStatus] = None

    @property
    def last_good(self) -> Optional[BatteryStatus]:
        return self._last_good

    def execute(self) -> BatteryStatus:
        interfaces = self._detector.find()
        if not interfaces:
            return self._status(ReadStatus.NOT_FOUND)
        failures: list[BatteryStatus] = []
        for interface in interfaces:
            status = self._query(interface)
            if status.ok:
                self._last_good = status
                return status
            failures.append(status)
        return self._summarize(failures, interfaces[0])

    def _query(self, interface: DeviceInterface) -> BatteryStatus:
        try:
            raw = self._exchange(interface)
        except PermissionError:
            return self._status(ReadStatus.PERMISSION_DENIED, interface=interface)
        except OSError as error:
            log.debug("falha em %s: %s", interface.hidraw_path, error)
            return self._status(ReadStatus.UNAVAILABLE, interface=interface)
        if raw is None:
            log.debug("sem resposta em %s", interface.hidraw_path)
            return self._status(ReadStatus.UNAVAILABLE, interface=interface)
        try:
            reading = self._protocol.parse(raw)
        except ProtocolError as error:
            log.warning("resposta inválida em %s: %s", interface.hidraw_path, error)
            return self._status(ReadStatus.INVALID_RESPONSE, interface=interface, detail=str(error))
        return self._status(ReadStatus.OK, interface=interface, reading=reading)

    def _exchange(self, interface: DeviceInterface) -> Optional[bytes]:
        with self._transport_factory(interface.hidraw_path) as transport:
            return transport.transact(self._protocol.build_query(), self._protocol.is_response, self._timeout)

    def _summarize(self, failures: list[BatteryStatus], first: DeviceInterface) -> BatteryStatus:
        if all(f.status is ReadStatus.PERMISSION_DENIED for f in failures):
            return self._status(ReadStatus.PERMISSION_DENIED)
        invalid = [f for f in failures if f.status is ReadStatus.INVALID_RESPONSE]
        if invalid:
            return invalid[-1]
        return self._status(ReadStatus.UNAVAILABLE, interface=first)

    def _status(self, status: ReadStatus, **fields) -> BatteryStatus:
        return BatteryStatus(status=status, timestamp=self._clock.now(), **fields)
