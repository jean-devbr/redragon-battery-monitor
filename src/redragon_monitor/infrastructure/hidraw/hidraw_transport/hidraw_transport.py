from __future__ import annotations

import os
import select
import time
from typing import Callable, Optional

READ_SIZE = 64


class HidrawTransport:
    def __init__(self, path: str):
        self._path = path
        self._fd: Optional[int] = None

    def __enter__(self) -> HidrawTransport:
        self._fd = os.open(self._path, os.O_RDWR | os.O_CLOEXEC)
        return self

    def __exit__(self, *exc) -> None:
        if self._fd is None:
            return
        os.close(self._fd)
        self._fd = None

    def transact(self, packet: bytes, match: Callable[[bytes], bool], timeout: float) -> Optional[bytes]:
        fd = self._require_open()
        self._drain(fd)
        os.write(fd, packet)
        deadline = time.monotonic() + timeout
        while (left := deadline - time.monotonic()) > 0:
            if not select.select([fd], [], [], left)[0]:
                return None
            data = os.read(fd, READ_SIZE)
            if match(data):
                return data
        return None

    def _require_open(self) -> int:
        if self._fd is None:
            raise RuntimeError("transporte não aberto")
        return self._fd

    @staticmethod
    def _drain(fd: int) -> None:
        while select.select([fd], [], [], 0)[0]:
            if not os.read(fd, READ_SIZE):
                return
