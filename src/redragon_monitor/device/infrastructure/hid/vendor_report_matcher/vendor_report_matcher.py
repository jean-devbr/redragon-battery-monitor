from redragon_monitor.device.infrastructure.hid.hid_item_reader import HidItemReader
from redragon_monitor.device.infrastructure.hid.hid_item_tags import HidItemTags as T


class VendorReportMatcher:
    def __init__(self, reader: HidItemReader, usage_page: int, report_id: int, report_bytes: int):
        self._reader = reader
        self._usage_page = usage_page
        self._report_id = report_id
        self._report_bits = report_bytes * 8

    def matches(self, descriptor: bytes) -> bool:
        state = {"page": 0, "id": 0, "size": 0, "count": 0}
        stack: list[dict] = []
        found_in = found_out = False
        for kind, tag, value in self._reader.items(descriptor):
            if kind == T.TYPE_GLOBAL and tag in T.GLOBAL_FIELDS:
                state[T.GLOBAL_FIELDS[tag]] = value
                continue
            if kind == T.TYPE_GLOBAL and tag == T.GLOBAL_PUSH:
                stack.append(dict(state))
                continue
            if kind == T.TYPE_GLOBAL and tag == T.GLOBAL_POP and stack:
                state = stack.pop()
                continue
            if kind != T.TYPE_MAIN or tag not in (T.MAIN_INPUT, T.MAIN_OUTPUT):
                continue
            if not self._is_target(state):
                continue
            found_in = found_in or tag == T.MAIN_INPUT
            found_out = found_out or tag == T.MAIN_OUTPUT
        return found_in and found_out

    def _is_target(self, state: dict) -> bool:
        return (
            state["page"] == self._usage_page
            and state["id"] == self._report_id
            and state["size"] * state["count"] == self._report_bits
        )
