#!/usr/bin/env python3
import argparse
import glob
import os
import select
import sys
import time

VID = 0x3554
PIDS = {0xF5D5: "receptor 2.4 GHz", 0xF55E: "cabo USB-C"}
REPORT_ID = 0x08
PKT_LEN = 17
CMD_POWER = 0x04
CHECKSUM_MAGIC = 0x55


def checksum(first16: bytes) -> int:
    return (CHECKSUM_MAGIC - sum(first16)) & 0xFF


def build_power_query() -> bytes:
    body = bytes([REPORT_ID, CMD_POWER]) + bytes(14)
    pkt = body + bytes([checksum(body)])
    assert pkt.hex(" ") == "08 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 49"
    return pkt


def find_candidates():
    out = []
    for dev in glob.glob("/sys/bus/hid/devices/0003:*"):
        name = os.path.basename(dev)
        try:
            vid = int(name.split(":")[1], 16)
            pid = int(name.split(":")[2].split(".")[0], 16)
        except (IndexError, ValueError):
            continue
        if vid != VID or pid not in PIDS:
            continue
        try:
            with open(os.path.join(dev, "report_descriptor"), "rb") as f:
                desc = f.read()
        except OSError:
            continue
        if b"\x06\x02\xff" in desc and b"\x85\x08" in desc:
            for hr in glob.glob(os.path.join(dev, "hidraw", "hidraw*")):
                out.append(("/dev/" + os.path.basename(hr), pid, desc))
    return out


def decode_hypothesis(r: bytes) -> str:
    if len(r) < PKT_LEN:
        return f"resposta curta ({len(r)} bytes) — não decodificada"
    ck_ok = checksum(r[:16]) == r[16]
    level, flag = r[6], r[7]
    mv = (r[8] << 8) | r[9]
    lines = [
        f"  checksum válido (0x55): {ck_ok}",
        f"  byte[2] status:         0x{r[2]:02x} (0 = sucesso, segundo MouseBattery)",
        f"  byte[6] nível:          {level} {'(plausível 0-100)' if level <= 100 else '(FORA de 0-100!)'}",
        f"  byte[7] carregando:     {flag} (0 = bateria, 1 = carregando, 2 = cheio?)",
        f"  byte[8:10] tensão:      {mv} mV {'(plausível)' if 3000 <= mv <= 4400 else '(implausível p/ Li-ion)'}",
    ]
    return "\n".join(lines)


def read_reports(fd, seconds, want_cmd=None):
    got = []
    end = time.monotonic() + seconds
    while (left := end - time.monotonic()) > 0:
        r, _, _ = select.select([fd], [], [], left)
        if not r:
            break
        data = os.read(fd, 64)
        if not data or data[0] != REPORT_ID:
            continue
        ts = time.strftime("%H:%M:%S")
        print(f"[{ts}] RX ({len(data)}): {data.hex(' ')}")
        got.append(data)
        if want_cmd is not None and len(data) > 1 and data[1] == want_cmd:
            break
    return got


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Teste controlado do protocolo Compx (VID 0x3554).\n"
            "  --descriptor  somente leitura do sysfs\n"
            "  --listen N    leitura passiva por N segundos\n"
            "  --query       envia apenas 08 04 00 .. 00 49 (consulta de energia)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--descriptor", action="store_true")
    g.add_argument("--listen", type=float, metavar="SEG")
    g.add_argument("--query", action="store_true")
    ap.add_argument("--device", help="forçar /dev/hidrawN (padrão: autodetecção)")
    args = ap.parse_args()

    cands = find_candidates()
    if not cands:
        sys.exit("Nenhuma interface 3554:F5D5/F55E com Report 0x08 (Usage Page 0xFF02) encontrada.")
    for path, pid, desc in cands:
        print(f"Encontrado: {path}  3554:{pid:04x} ({PIDS[pid]})  descritor={len(desc)} bytes")
    if args.descriptor:
        for _, _, desc in cands:
            print(desc.hex(" "))
        return

    path = args.device or cands[0][0]
    if path not in [c[0] for c in cands]:
        sys.exit(f"{path} não é uma interface candidata; recusando por segurança.")

    try:
        fd = os.open(path, os.O_RDWR if args.query else os.O_RDONLY)
    except PermissionError:
        sys.exit(f"Sem permissão para {path}. Rode com sudo (ver instruções).")

    try:
        if args.listen:
            print(f"Escutando {path} por {args.listen}s (somente leitura). Relatórios ID != 0x08 são ignorados.")
            got = read_reports(fd, args.listen)
            print(f"Total de relatórios 0x08 recebidos: {len(got)}")
            return

        pkt = build_power_query()
        print(f"TX ({len(pkt)}): {pkt.hex(' ')}")
        os.write(fd, pkt)
        got = read_reports(fd, 2.0, want_cmd=CMD_POWER)
        resp = [r for r in got if len(r) > 1 and r[1] == CMD_POWER]
        if not resp:
            print("\nSem resposta ao comando 0x04 em 2 s.")
            print("Possíveis causas: mouse dormindo (mexa e repita), firmware não implementa o comando.")
            sys.exit(2)
        print("\nDecodificação HIPOTÉTICA (precisa ser validada contra o comportamento real):")
        print(decode_hypothesis(resp[-1]))
    finally:
        os.close(fd)


if __name__ == "__main__":
    main()
