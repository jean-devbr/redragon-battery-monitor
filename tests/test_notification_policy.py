from datetime import datetime

from redragon_monitor.device.battery_protocol import BatteryReading
from redragon_monitor.services.battery_service import BatteryStatus, Status
from redragon_monitor.services.notification_service import LowBatteryPolicy

NOW = datetime(2026, 11, 6)


def ok(percent, charging=False):
    r = BatteryReading(percent, charging, int(charging), 3700, b"")
    return BatteryStatus(Status.OK, NOW, reading=r)


UNAVAILABLE = BatteryStatus(Status.UNAVAILABLE, NOW)


def test_fires_once_per_discharge():
    p = LowBatteryPolicy(threshold=20)
    assert [p.update(ok(v)) for v in (30, 20, 15, 10)] == [False, True, False, False]


def test_rearms_after_charging():
    p = LowBatteryPolicy(threshold=20)
    assert p.update(ok(20))
    assert not p.update(ok(20, charging=True))
    assert p.update(ok(19))


def test_rearms_only_above_margin():
    p = LowBatteryPolicy(threshold=20, rearm_margin=5)
    assert p.update(ok(20))
    assert not p.update(ok(24))
    assert not p.update(ok(20))
    assert not p.update(ok(25))
    assert p.update(ok(20))


def test_unavailable_never_fires_nor_changes_state():
    p = LowBatteryPolicy(threshold=20)
    assert not p.update(UNAVAILABLE)
    assert p.update(ok(10))
