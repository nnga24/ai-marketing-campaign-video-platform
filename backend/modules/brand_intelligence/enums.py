from enum import Enum


class FactVerificationStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    PROPOSED = "PROPOSED"
    UNKNOWN = "UNKNOWN"