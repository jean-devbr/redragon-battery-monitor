from redragon_monitor.domain.read_status import ReadStatus

SUCCESS = 0
FAILURE = 1
UNAVAILABLE = 2

CODES = {
    ReadStatus.OK: SUCCESS,
    ReadStatus.UNAVAILABLE: UNAVAILABLE,
    ReadStatus.NOT_FOUND: FAILURE,
    ReadStatus.PERMISSION_DENIED: FAILURE,
    ReadStatus.INVALID_RESPONSE: FAILURE,
    ReadStatus.ERROR: FAILURE,
}


class ExitCodes:
    SUCCESS = SUCCESS
    FAILURE = FAILURE

    def for_status(self, status: ReadStatus) -> int:
        return CODES[status]
