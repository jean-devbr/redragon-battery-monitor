from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from redragon_monitor.device.domain.device_interface import DeviceInterface
from redragon_monitor.device.domain.device_spec import DeviceSpec
from redragon_monitor.device.infrastructure.hid.vendor_report_matcher import VendorReportMatcher

USB_BUS = "0003"
HID_DEVICES = "bus/hid/devices"
HIDRAW_PREFIX = "hidraw"


class SysfsDeviceDetector:
    def __init__(self, spec: DeviceSpec, matcher: VendorReportMatcher, sysfs_root: str = "/sys", dev_root: str = "/dev"):
        self._spec = spec
        self._matcher = matcher
        self._hid_dir = Path(sysfs_root, HID_DEVICES)
        self._dev_root = dev_root

    def find(self) -> list[DeviceInterface]:
        if not self._hid_dir.is_dir():
            return []
        found: list[DeviceInterface] = []
        for device in sorted(self._hid_dir.iterdir()):
            found.extend(self._interfaces_of(device))
        return sorted(found, key=lambda d: self._spec.preference(d.pid))

    def _interfaces_of(self, device: Path) -> list[DeviceInterface]:
        product_id = self._supported_product_id(device.name)
        if product_id is None or not self._has_battery_report(device):
            return []
        return [
            DeviceInterface(
                pid=product_id,
                connection=self._spec.connections[product_id],
                hidraw_path=os.path.join(self._dev_root, node),
                sysfs_path=str(device),
            )
            for node in self._hidraw_nodes(device)
        ]

    def _supported_product_id(self, name: str) -> Optional[int]:
        parts = name.split(":")
        if len(parts) != 3 or parts[0] != USB_BUS:
            return None
        try:
            vendor_id = int(parts[1], 16)
            product_id = int(parts[2].split(".")[0], 16)
        except ValueError:
            return None
        if not self._spec.supports(vendor_id, product_id):
            return None
        return product_id

    def _has_battery_report(self, device: Path) -> bool:
        try:
            descriptor = (device / "report_descriptor").read_bytes()
        except OSError:
            return False
        return self._matcher.matches(descriptor)

    @staticmethod
    def _hidraw_nodes(device: Path) -> list[str]:
        hidraw_dir = device / HIDRAW_PREFIX
        if not hidraw_dir.is_dir():
            return []
        return sorted(n.name for n in hidraw_dir.iterdir() if n.name.startswith(HIDRAW_PREFIX))
