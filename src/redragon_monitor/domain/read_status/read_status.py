from enum import Enum


class ReadStatus(str, Enum):
    OK = "ok"
    UNAVAILABLE = "unavailable"
    NOT_FOUND = "not_found"
    PERMISSION_DENIED = "permission_denied"
    INVALID_RESPONSE = "invalid_response"
    ERROR = "error"
