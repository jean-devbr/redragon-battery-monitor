from redragon_monitor.device.detector import ConnectionType, find_interfaces, has_vendor_report
from conftest import RECEIVER_IF0_DESC, RECEIVER_IF1_DESC, WIRED_IF1_DESC


def test_real_descriptors_have_vendor_report():
    assert has_vendor_report(RECEIVER_IF1_DESC)
    assert has_vendor_report(WIRED_IF1_DESC)


def test_keyboard_interface_is_not_selected():
    assert not has_vendor_report(RECEIVER_IF0_DESC)


def test_find_receiver_only(fake_sysfs):
    root = fake_sysfs({
        "0003:3554:F5D5.0001": (RECEIVER_IF0_DESC, "hidraw0"),
        "0003:3554:F5D5.0009": (RECEIVER_IF1_DESC, "hidraw1"),
    })
    found = find_interfaces(sysfs_root=root)
    assert [(f.hidraw_path, f.connection) for f in found] == [("/dev/hidraw1", ConnectionType.RECEIVER)]


def test_wired_is_preferred_over_receiver(fake_sysfs):
    root = fake_sysfs({
        "0003:3554:F5D5.0009": (RECEIVER_IF1_DESC, "hidraw1"),
        "0003:3554:F55E.000E": (WIRED_IF1_DESC, "hidraw3"),
    })
    found = find_interfaces(sysfs_root=root)
    assert [f.hidraw_path for f in found] == ["/dev/hidraw3", "/dev/hidraw1"]


def test_unknown_vendor_or_pid_ignored(fake_sysfs):
    root = fake_sysfs({
        "0003:046D:C52B.0002": (RECEIVER_IF1_DESC, "hidraw5"),
        "0003:3554:F507.0003": (RECEIVER_IF1_DESC, "hidraw6"),
    })
    assert find_interfaces(sysfs_root=root) == []


def test_missing_sysfs(tmp_path):
    assert find_interfaces(sysfs_root=str(tmp_path / "nada")) == []
