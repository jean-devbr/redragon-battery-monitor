"""Detecção do M719RGB-PRO pelo sysfs (não precisa de root e não abre o dispositivo)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

VENDOR_ID = 0x3554


class ConnectionType(str, Enum):
    USB_C = "usb-c"
    RECEIVER = "receptor-2.4ghz"


# Ordem = preferência. No modo cabo o receptor não responde, então o cabo vem primeiro.
SUPPORTED_PIDS: dict[int, ConnectionType] = {
    0xF55E: ConnectionType.USB_C,
    0xF5D5: ConnectionType.RECEIVER,
}

VENDOR_USAGE_PAGE = 0xFF02
VENDOR_REPORT_ID = 0x08
VENDOR_REPORT_BYTES = 16


@dataclass(frozen=True)
class DeviceInterface:
    pid: int
    connection: ConnectionType
    hidraw_path: str
    sysfs_path: str


def _items(desc: bytes):
    """Itera itens curtos de um descritor HID: (tipo, tag, valor_sem_sinal)."""
    i = 0
    while i < len(desc):
        prefix = desc[i]
        if prefix == 0xFE:  # item longo: pula
            if i + 2 >= len(desc):
                return
            i += 3 + desc[i + 1]
            continue
        size = (0, 1, 2, 4)[prefix & 0x03]
        value = int.from_bytes(desc[i + 1 : i + 1 + size], "little") if size else 0
        yield (prefix >> 2) & 0x03, prefix >> 4, value
        i += 1 + size


def has_vendor_report(
    desc: bytes,
    usage_page: int = VENDOR_USAGE_PAGE,
    report_id: int = VENDOR_REPORT_ID,
    length: int = VENDOR_REPORT_BYTES,
) -> bool:
    """True se o descritor tem Input e Output de `length` bytes no report/usage page dados."""
    g = {"page": 0, "id": 0, "size": 0, "count": 0}
    stack: list[dict] = []
    found_in = found_out = False
    for typ, tag, val in _items(desc):
        if typ == 1:  # global
            if tag == 0x0:
                g["page"] = val
            elif tag == 0x7:
                g["size"] = val
            elif tag == 0x8:
                g["id"] = val
            elif tag == 0x9:
                g["count"] = val
            elif tag == 0xA:
                stack.append(dict(g))
            elif tag == 0xB and stack:
                g = stack.pop()
        elif typ == 0 and tag in (0x8, 0x9):  # Input / Output
            if (
                g["page"] == usage_page
                and g["id"] == report_id
                and g["size"] * g["count"] == length * 8
            ):
                if tag == 0x8:
                    found_in = True
                else:
                    found_out = True
    return found_in and found_out


def find_interfaces(sysfs_root: str = "/sys", dev_root: str = "/dev") -> list[DeviceInterface]:
    found: list[DeviceInterface] = []
    hid_dir = Path(sysfs_root, "bus/hid/devices")
    if not hid_dir.is_dir():
        return found
    for dev in sorted(hid_dir.iterdir()):
        parts = dev.name.split(":")  # 0003:3554:F5D5.0009
        if len(parts) != 3 or parts[0] != "0003":
            continue
        try:
            vid = int(parts[1], 16)
            pid = int(parts[2].split(".")[0], 16)
        except ValueError:
            continue
        if vid != VENDOR_ID or pid not in SUPPORTED_PIDS:
            continue
        try:
            desc = (dev / "report_descriptor").read_bytes()
        except OSError:
            continue
        if not has_vendor_report(desc):
            continue
        hidraw_dir = dev / "hidraw"
        if not hidraw_dir.is_dir():
            continue
        for node in sorted(hidraw_dir.iterdir()):
            if node.name.startswith("hidraw"):
                found.append(
                    DeviceInterface(
                        pid=pid,
                        connection=SUPPORTED_PIDS[pid],
                        hidraw_path=os.path.join(dev_root, node.name),
                        sysfs_path=str(dev),
                    )
                )
    order = list(SUPPORTED_PIDS)
    return sorted(found, key=lambda d: order.index(d.pid))
