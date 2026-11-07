from dataclasses import dataclass


@dataclass(frozen=True)
class BatteryReading:
    percent: int
    charging: bool
    charging_raw: int
    voltage_mv: int
    raw: bytes
