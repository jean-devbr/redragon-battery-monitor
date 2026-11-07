from typing import Iterator

from redragon_monitor.device.infrastructure.hid.hid_item_tags import HidItemTags as T


class HidItemReader:
    def items(self, descriptor: bytes) -> Iterator[tuple[int, int, int]]:
        i = 0
        while i < len(descriptor):
            prefix = descriptor[i]
            if prefix == T.LONG_ITEM and i + 2 >= len(descriptor):
                return
            if prefix == T.LONG_ITEM:
                i += 3 + descriptor[i + 1]
                continue
            size = T.SIZES[prefix & 0x03]
            value = int.from_bytes(descriptor[i + 1 : i + 1 + size], "little")
            yield (prefix >> 2) & 0x03, prefix >> 4, value
            i += 1 + size
