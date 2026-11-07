"""Modo terminal.

Códigos de saída (consulta única):
  0 = leitura obtida
  1 = dispositivo não encontrado, sem permissão ou resposta inválida
  2 = mouse não respondeu (desligado ou em repouso)
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time

from redragon_monitor import __version__
from redragon_monitor.services.battery_service import BatteryService, BatteryStatus, Status
from redragon_monitor.services.notification_service import (
    DEFAULT_THRESHOLD,
    DesktopNotifier,
    LowBatteryPolicy,
)

EXIT_CODES = {
    Status.OK: 0,
    Status.UNAVAILABLE: 2,
    Status.NOT_FOUND: 1,
    Status.PERMISSION_DENIED: 1,
    Status.INVALID_RESPONSE: 1,
    Status.ERROR: 1,
}


def to_dict(s: BatteryStatus) -> dict:
    d = {"status": s.status.value, "message": s.message, "timestamp": s.timestamp.isoformat(timespec="seconds")}
    if s.interface:
        d["connection"] = s.interface.connection.value
        d["device"] = s.interface.hidraw_path
    if s.reading:
        r = s.reading
        d.update(percent=r.percent, charging=r.charging, charging_raw=r.charging_raw,
                 voltage_mv=r.voltage_mv, raw=r.raw.hex(" "))
    if s.detail:
        d["detail"] = s.detail
    return d


def format_human(s: BatteryStatus, last_good: BatteryStatus | None = None) -> str:
    if s.ok and s.reading:
        r = s.reading
        state = "carregando" if r.charging else "na bateria"
        return (f"Bateria: {r.percent}% ({state})\n"
                f"Tensão:  {r.voltage_mv} mV\n"
                f"Conexão: {s.interface.connection.value} ({s.interface.hidraw_path})")
    text = s.message
    if s.detail:
        text += f"\nDetalhe: {s.detail}"
    if last_good and last_good.reading:
        text += (f"\nÚltima leitura válida: {last_good.reading.percent}% às "
                 f"{last_good.timestamp:%H:%M:%S}")
    return text


def format_line(s: BatteryStatus, last_good: BatteryStatus | None) -> str:
    ts = f"{s.timestamp:%H:%M:%S}"
    if s.ok and s.reading:
        r = s.reading
        flag = " ⚡" if r.charging else ""
        return f"[{ts}] {r.percent:3d}%{flag}  {r.voltage_mv} mV  ({s.interface.connection.value})"
    extra = ""
    if last_good and last_good.reading:
        extra = f"  [última: {last_good.reading.percent}% às {last_good.timestamp:%H:%M:%S}]"
    return f"[{ts}] {s.message}{extra}"


def run_watch(service: BatteryService, interval: float, as_json: bool, policy, notifier) -> int:
    try:
        while True:
            s = service.read()
            if as_json:
                print(json.dumps(to_dict(s), ensure_ascii=False), flush=True)
            else:
                print(format_line(s, service.last_good), flush=True)
            if policy and policy.update(s) and notifier:
                notifier.low_battery(s.reading.percent)
            time.sleep(interval)
    except KeyboardInterrupt:
        return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="redragon-battery",
                                description="Bateria do Redragon M719RGB-PRO (receptor 2.4 GHz ou USB-C).")
    p.add_argument("--json", action="store_true", help="saída em JSON")
    p.add_argument("--watch", type=float, metavar="SEG", help="consulta periodicamente (mínimo 5 s)")
    p.add_argument("--notify", action="store_true", help="com --watch: notifica bateria baixa")
    p.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD, help="limite de bateria baixa em %% (padrão 20)")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING,
                        format="%(levelname)s %(name)s: %(message)s")
    service = BatteryService()

    if args.watch is not None:
        if args.watch < 5:
            print("--watch precisa ser de pelo menos 5 segundos.", file=sys.stderr)
            return 1
        policy = LowBatteryPolicy(args.threshold) if args.notify else None
        notifier = DesktopNotifier() if args.notify else None
        return run_watch(service, args.watch, args.json, policy, notifier)

    s = service.read()
    print(json.dumps(to_dict(s), ensure_ascii=False) if args.json else format_human(s))
    return EXIT_CODES[s.status]


if __name__ == "__main__":
    sys.exit(main())
