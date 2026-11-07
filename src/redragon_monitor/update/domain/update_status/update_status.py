from enum import Enum


class UpdateStatus(str, Enum):
    AVAILABLE = "available"
    UP_TO_DATE = "up_to_date"
    FAILED = "failed"
