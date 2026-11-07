#!/usr/bin/env python3
import glob
import json
import os
import select
import sys
import time

VID = 0x3554
PIDS = {0xF55E: "usb-c", 0xF5D5: "receptor-2.4ghz"}
REPORT_ID = 0x08
CMD_POWER = 0x04
PKT_LEN = 17
TIMEOUT_S = 2.0


def checksum(first16: bytes) -> int:
    return (0x55 - sum(first16)) & 0xFF


QUERY = bytes([REPORT_ID, CMD_POWER]) + bytes(14)
QUERY += bytes([checksum(QUERY)])
assert QUERY.hex(" ") == "08 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 49"


def find_interfaces():
    found = []
    for dev in glob.glob("/sys/bus/hid/devices/0003:*"):
        parts = os.path.basename(dev).split(":")
        try:
            vid, pid = int(parts[1], 16), int(parts[2].split(".")[0], 16)
        except (IndexError, ValueError):
            continue
        if vid != VID or pid not in PIDS:
            continue
        try:
            with open(os.path.join(dev, "report_descriptor"), "rb") as f:
                desc = f.read()
        except OSError:
            continue
        if b"\x06\x02\xff" not in desc or b"\x85\x08" not in desc:
            continue
        for hr in glob.glob(os.path.join(dev, "hidraw", "hidraw*")):
            found.append((pid, "/dev/" + os.path.basename(hr)))
    order = list(PIDS)
    return sorted(found, key=lambda x: order.index(x[0]))


def parse(resp: bytes):
    if len(resp) < PKT_LEN or resp[0] != REPORT_ID or resp[1] != CMD_POWER:
        return None
    if checksum(resp[:16]) != resp[16]:
        return None
    if resp[2] != 0x00:
        return None
    level, charging = resp[6], resp[7]
    if level > 100 or charging > 2:
        return None
    return {
        "percent": level,
        "charging": charging == 1,
        "charging_raw": charging,
        "voltage_mv": (resp[8] << 8) | resp[9],
        "raw": resp[:PKT_LEN].hex(" "),
    }


def query(path: str):
    fd = os.open(path, os.O_RDWR)
    try:
        while select.select([fd], [], [], 0)[0]:
            os.read(fd, 64)
        os.write(fd, QUERY)
        end = time.monotonic() + TIMEOUT_S
        while (left := end - time.monotonic()) > 0:
            if not select.select([fd], [], [], left)[0]:
                break
            data = os.read(fd, 64)
            if len(data) > 1 and data[0] == REPORT_ID and data[1] == CMD_POWER:
                return parse(data)
        return None
    finally:
        os.close(fd)


def main():
    as_json = "--json" in sys.argv
    ifaces = find_interfaces()
    if not ifaces:
        msg = "Nenhum Redragon M719RGB-PRO (3554:f5d5 / 3554:f55e) encontrado."
        print(json.dumps({"status": "not_found", "message": msg}) if as_json else msg)
        return 1

    denied = []
    for pid, path in ifaces:
        try:
            result = query(path)
        except PermissionError:
            denied.append(path)
            continue
        except OSError:
            continue
        if result:
            result.update(status="ok", connection=PIDS[pid], device=path,
                          timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"))
            if as_json:
                print(json.dumps(result, ensure_ascii=False))
            else:
                state = "carregando" if result["charging"] else "na bateria"
                print(f"Bateria: {result['percent']}% ({state})")
                print(f"Tensão:  {result['voltage_mv']} mV")
                print(f"Conexão: {result['connection']} ({path})")
            return 0

    if denied and len(denied) == len(ifaces):
        msg = f"Sem permissão para {', '.join(denied)}. Rode com sudo."
        print(json.dumps({"status": "permission_denied", "message": msg}) if as_json else msg)
        return 1
    msg = "Mouse indisponível (desligado ou em repouso). Mexa o mouse e tente novamente."
    print(json.dumps({"status": "unavailable", "message": msg}) if as_json else msg)
    return 2


if __name__ == "__main__":
    sys.exit(main())
