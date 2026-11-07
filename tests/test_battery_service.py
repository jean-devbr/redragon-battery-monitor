from datetime import datetime

from redragon_monitor.device.detector import ConnectionType, DeviceInterface
from redragon_monitor.services.battery_service import BatteryService, Status
from conftest import RESP_CHARGING, RESP_WIRELESS

WIRED = DeviceInterface(0xF55E, ConnectionType.USB_C, "/dev/hidraw3", "")
RECV = DeviceInterface(0xF5D5, ConnectionType.RECEIVER, "/dev/hidraw1", "")


class FakeTransport:
    sent: list = []

    def __init__(self, behaviour):
        self.behaviour = behaviour

    def __call__(self, path):
        self.path = path
        return self

    def __enter__(self):
        b = self.behaviour.get(self.path)
        if isinstance(b, Exception):
            raise b
        return self

    def __exit__(self, *a):
        pass

    def transact(self, packet, match, timeout):
        FakeTransport.sent.append(packet)
        b = self.behaviour.get(self.path)
        return b if b is not None and match(b) else None


def service(interfaces, behaviour):
    return BatteryService(finder=lambda: interfaces, transport_factory=FakeTransport(behaviour),
                          clock=lambda: datetime(2026, 11, 6, 23, 0, 0))


def test_wireless_ok():
    s = service([RECV], {"/dev/hidraw1": RESP_WIRELESS}).read()
    assert s.status is Status.OK and s.reading.percent == 100
    assert s.interface.connection is ConnectionType.RECEIVER


def test_wired_ok_while_receiver_silent():
    s = service([WIRED, RECV], {"/dev/hidraw3": RESP_CHARGING, "/dev/hidraw1": None}).read()
    assert s.status is Status.OK and s.reading.charging
    assert s.interface is WIRED


def test_falls_back_to_receiver_when_wired_silent():
    s = service([WIRED, RECV], {"/dev/hidraw3": None, "/dev/hidraw1": RESP_WIRELESS}).read()
    assert s.ok and s.interface is RECV


def test_mouse_off_is_unavailable_without_number():
    svc = service([RECV], {"/dev/hidraw1": None})
    s = svc.read()
    assert s.status is Status.UNAVAILABLE and s.reading is None
    assert svc.last_good is None


def test_last_good_is_kept_but_not_reported_as_current():
    behaviour = {"/dev/hidraw1": RESP_WIRELESS}
    svc = service([RECV], behaviour)
    assert svc.read().ok
    behaviour["/dev/hidraw1"] = None
    s = svc.read()
    assert s.status is Status.UNAVAILABLE and s.reading is None
    assert svc.last_good.reading.percent == 100


def test_not_found():
    assert service([], {}).read().status is Status.NOT_FOUND


def test_permission_denied():
    s = service([RECV], {"/dev/hidraw1": PermissionError()}).read()
    assert s.status is Status.PERMISSION_DENIED


def test_invalid_response_gives_no_number():
    bad = bytearray(RESP_WIRELESS)
    bad[16] ^= 0xFF
    s = service([RECV], {"/dev/hidraw1": bytes(bad)}).read()
    assert s.status is Status.INVALID_RESPONSE and s.reading is None


def test_only_power_query_is_ever_sent():
    FakeTransport.sent.clear()
    service([WIRED, RECV], {"/dev/hidraw3": None, "/dev/hidraw1": None}).read()
    assert FakeTransport.sent and all(
        p.hex(" ") == "08 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 49" for p in FakeTransport.sent
    )
