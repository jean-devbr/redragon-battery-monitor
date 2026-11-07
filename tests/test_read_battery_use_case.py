from redragon_monitor.battery.application.read_battery import ReadBatteryUseCase
from redragon_monitor.battery.domain.read_status import ReadStatus
from redragon_monitor.battery.infrastructure.compx.compx_battery_protocol import CompxBatteryProtocol
from redragon_monitor.battery.infrastructure.compx.compx_checksum import CompxChecksum
from redragon_monitor.battery.infrastructure.compx.compx_power_query import CompxPowerQuery
from redragon_monitor.battery.infrastructure.compx.compx_power_response_parser import CompxPowerResponseParser
from conftest import RESP_CHARGING, RESP_WIRELESS
from fakes import RECEIVER, WIRED, FakeDetector, FakeTransportFactory, FixedClock

CHECKSUM = CompxChecksum()
PROTOCOL = CompxBatteryProtocol(CompxPowerQuery(CHECKSUM), CompxPowerResponseParser(CHECKSUM))


def use_case(interfaces, behaviour):
    factory = FakeTransportFactory(behaviour)
    return ReadBatteryUseCase(FakeDetector(interfaces), factory, PROTOCOL, FixedClock()), factory


def test_wireless_ok():
    status = use_case([RECEIVER], {"/dev/hidraw1": RESP_WIRELESS})[0].execute()
    assert status.status is ReadStatus.OK and status.reading.percent == 100
    assert status.interface is RECEIVER


def test_wired_ok_while_receiver_silent():
    status = use_case([WIRED, RECEIVER], {"/dev/hidraw3": RESP_CHARGING, "/dev/hidraw1": None})[0].execute()
    assert status.ok and status.reading.charging and status.interface is WIRED


def test_falls_back_to_receiver_when_wired_silent():
    status = use_case([WIRED, RECEIVER], {"/dev/hidraw3": None, "/dev/hidraw1": RESP_WIRELESS})[0].execute()
    assert status.ok and status.interface is RECEIVER


def test_mouse_off_is_unavailable_without_number():
    reader = use_case([RECEIVER], {"/dev/hidraw1": None})[0]
    status = reader.execute()
    assert status.status is ReadStatus.UNAVAILABLE and status.reading is None
    assert reader.last_good is None


def test_last_good_is_kept_but_not_reported_as_current():
    behaviour = {"/dev/hidraw1": RESP_WIRELESS}
    reader = use_case([RECEIVER], behaviour)[0]
    assert reader.execute().ok
    behaviour["/dev/hidraw1"] = None
    status = reader.execute()
    assert status.status is ReadStatus.UNAVAILABLE and status.reading is None
    assert reader.last_good.reading.percent == 100


def test_not_found():
    assert use_case([], {})[0].execute().status is ReadStatus.NOT_FOUND


def test_permission_denied():
    status = use_case([RECEIVER], {"/dev/hidraw1": PermissionError()})[0].execute()
    assert status.status is ReadStatus.PERMISSION_DENIED


def test_os_error_is_unavailable():
    status = use_case([RECEIVER], {"/dev/hidraw1": OSError("removido")})[0].execute()
    assert status.status is ReadStatus.UNAVAILABLE


def test_invalid_response_gives_no_number():
    bad = bytearray(RESP_WIRELESS)
    bad[16] ^= 0xFF
    status = use_case([RECEIVER], {"/dev/hidraw1": bytes(bad)})[0].execute()
    assert status.status is ReadStatus.INVALID_RESPONSE and status.reading is None


def test_only_power_query_is_ever_sent():
    reader, factory = use_case([WIRED, RECEIVER], {"/dev/hidraw3": None, "/dev/hidraw1": None})
    reader.execute()
    assert factory.sent
    assert all(p.hex(" ") == "08 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 49" for p in factory.sent)
