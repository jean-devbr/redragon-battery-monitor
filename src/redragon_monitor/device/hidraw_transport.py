from __future__ import annotations

import os
import select
import time
from typing import Callable, Optional

READ_SIZE = 64


class HidrawTransport:
    def __init__(self, path: str):
        self.path = path
        self._fd: Optional[int] = None

    def open(self) -> "HidrawTransport":
        self._fd = os.open(self.path, os.O_RDWR | os.O_CLOEXEC)
        return self

    def close(self) -> None:
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None

    def __enter__(self) -> "HidrawTransport":
        return self.open()

    def __exit__(self, *exc) -> None:
        self.close()

    @property
    def fd(self) -> int:
        if self._fd is None:
            raise RuntimeError("transporte não aberto")
        return self._fd

    def drain(self) -> None:
        while select.select([self.fd], [], [], 0)[0]:
            if not os.read(self.fd, READ_SIZE):
                break

    def transact(
        self,
        packet: bytes,
        match: Callable[[bytes], bool],
        timeout: float,
    ) -> Optional[bytes]:
        self.drain()
        os.write(self.fd, packet)
        deadline = time.monotonic() + timeout
        while (left := deadline - time.monotonic()) > 0:
            if not select.select([self.fd], [], [], left)[0]:
                return None
            data = os.read(self.fd, READ_SIZE)
            if match(data):
                return data
        return None
