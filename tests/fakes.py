from datetime import datetime

from redragon_monitor.domain.connection_type import ConnectionType
from redragon_monitor.domain.device_interface import DeviceInterface

FIXED_TIME = datetime(2026, 11, 6, 23, 0, 0)
WIRED = DeviceInterface(0xF55E, ConnectionType.USB_C, "/dev/hidraw3", "")
RECEIVER = DeviceInterface(0xF5D5, ConnectionType.RECEIVER, "/dev/hidraw1", "")


class FixedClock:
    def now(self) -> datetime:
        return FIXED_TIME


class FakeDetector:
    def __init__(self, interfaces):
        self.interfaces = interfaces

    def find(self):
        return list(self.interfaces)


class FakeTransportFactory:
    def __init__(self, behaviour):
        self.behaviour = behaviour
        self.sent: list[bytes] = []

    def __call__(self, path):
        return FakeTransport(self, path)


class FakeTransport:
    def __init__(self, factory, path):
        self._factory = factory
        self._path = path

    def __enter__(self):
        outcome = self._factory.behaviour.get(self._path)
        if isinstance(outcome, Exception):
            raise outcome
        return self

    def __exit__(self, *exc):
        return None

    def transact(self, packet, match, timeout):
        self._factory.sent.append(packet)
        outcome = self._factory.behaviour.get(self._path)
        if outcome is None or not match(outcome):
            return None
        return outcome


class RecordingNotifier:
    def __init__(self):
        self.alerts: list[int] = []

    def low_battery(self, percent):
        self.alerts.append(percent)
        return True
