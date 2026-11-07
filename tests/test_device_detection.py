from redragon_monitor.domain.connection_type import ConnectionType
from redragon_monitor.infrastructure.devices.redragon_m719 import RedragonM719
from redragon_monitor.infrastructure.hid.hid_item_reader import HidItemReader
from redragon_monitor.infrastructure.hid.vendor_report_matcher import VendorReportMatcher
from redragon_monitor.infrastructure.sysfs.sysfs_device_detector import SysfsDeviceDetector
from conftest import RECEIVER_IF0_DESC, RECEIVER_IF1_DESC, WIRED_IF1_DESC

SPEC = RedragonM719.spec()
MATCHER = VendorReportMatcher(HidItemReader(), SPEC.usage_page, SPEC.report_id, SPEC.report_bytes)


def detector(root):
    return SysfsDeviceDetector(SPEC, MATCHER, sysfs_root=root)


def test_real_descriptors_have_vendor_report():
    assert MATCHER.matches(RECEIVER_IF1_DESC)
    assert MATCHER.matches(WIRED_IF1_DESC)


def test_keyboard_interface_is_not_selected():
    assert not MATCHER.matches(RECEIVER_IF0_DESC)


def test_find_receiver_only(fake_sysfs):
    root = fake_sysfs({
        "0003:3554:F5D5.0001": (RECEIVER_IF0_DESC, "hidraw0"),
        "0003:3554:F5D5.0009": (RECEIVER_IF1_DESC, "hidraw1"),
    })
    found = detector(root).find()
    assert [(f.hidraw_path, f.connection) for f in found] == [("/dev/hidraw1", ConnectionType.RECEIVER)]


def test_wired_is_preferred_over_receiver(fake_sysfs):
    root = fake_sysfs({
        "0003:3554:F5D5.0009": (RECEIVER_IF1_DESC, "hidraw1"),
        "0003:3554:F55E.000E": (WIRED_IF1_DESC, "hidraw3"),
    })
    assert [f.hidraw_path for f in detector(root).find()] == ["/dev/hidraw3", "/dev/hidraw1"]


def test_unknown_vendor_or_pid_ignored(fake_sysfs):
    root = fake_sysfs({
        "0003:046D:C52B.0002": (RECEIVER_IF1_DESC, "hidraw5"),
        "0003:3554:F507.0003": (RECEIVER_IF1_DESC, "hidraw6"),
    })
    assert detector(root).find() == []


def test_missing_sysfs(tmp_path):
    assert detector(str(tmp_path / "nada")).find() == []
