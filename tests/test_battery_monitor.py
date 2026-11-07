import pytest

from redragon_monitor.alert.application.battery_monitor import BatteryMonitor
from redragon_monitor.alert.domain.low_battery_policy import LowBatteryPolicy
from redragon_monitor.battery.domain.battery_reading import BatteryReading
from redragon_monitor.battery.domain.battery_status import BatteryStatus
from redragon_monitor.battery.domain.read_status import ReadStatus
from fakes import FIXED_TIME, RECEIVER, RecordingNotifier


def ok(percent, charging=False):
    reading = BatteryReading(percent, charging, int(charging), 3700, b"")
    return BatteryStatus(ReadStatus.OK, FIXED_TIME, reading=reading, interface=RECEIVER)


UNAVAILABLE = BatteryStatus(ReadStatus.UNAVAILABLE, FIXED_TIME)


class ScriptedReader:
    def __init__(self, statuses):
        self._statuses = list(statuses)
        self.last_good = None

    def execute(self):
        return self._statuses.pop(0)


def test_policy_fires_once_per_discharge():
    policy = LowBatteryPolicy(threshold=20)
    assert [policy.should_alert(ok(v)) for v in (30, 20, 15, 10)] == [False, True, False, False]


def test_policy_rearms_after_charging():
    policy = LowBatteryPolicy(threshold=20)
    assert policy.should_alert(ok(20))
    assert not policy.should_alert(ok(20, charging=True))
    assert policy.should_alert(ok(19))


def test_policy_rearms_only_above_margin():
    policy = LowBatteryPolicy(threshold=20, rearm_margin=5)
    assert policy.should_alert(ok(20))
    assert not policy.should_alert(ok(24))
    assert not policy.should_alert(ok(20))
    assert not policy.should_alert(ok(25))
    assert policy.should_alert(ok(20))


def test_policy_ignores_unavailable():
    policy = LowBatteryPolicy(threshold=20)
    assert not policy.should_alert(UNAVAILABLE)
    assert policy.should_alert(ok(10))


def test_policy_rejects_invalid_threshold():
    with pytest.raises(ValueError):
        LowBatteryPolicy(threshold=0)


def test_change_threshold_rearms():
    policy = LowBatteryPolicy(threshold=20)
    assert policy.should_alert(ok(15))
    policy.change_threshold(30)
    assert policy.threshold == 30
    assert policy.should_alert(ok(15))


def test_monitor_notifies_only_when_enabled():
    notifier = RecordingNotifier()
    monitor = BatteryMonitor(ScriptedReader([ok(10)]), LowBatteryPolicy(20), notifier)
    monitor.check(notify=False)
    assert notifier.alerts == []


def test_monitor_notifies_low_battery_once():
    notifier = RecordingNotifier()
    monitor = BatteryMonitor(ScriptedReader([ok(30), ok(15), ok(10)]), LowBatteryPolicy(20), notifier)
    for _ in range(3):
        monitor.check(notify=True)
    assert notifier.alerts == [15]
