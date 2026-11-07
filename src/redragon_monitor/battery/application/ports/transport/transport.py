from __future__ import annotations

from typing import Callable, Optional, Protocol


class Transport(Protocol):
    def __enter__(self) -> Transport: ...

    def __exit__(self, *exc) -> None: ...

    def transact(self, packet: bytes, match: Callable[[bytes], bool], timeout: float) -> Optional[bytes]: ...
