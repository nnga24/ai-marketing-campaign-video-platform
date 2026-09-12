from enum import Enum


class EntityStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class SourceType(str, Enum):
    USER_PROVIDED = "USER_PROVIDED"
    AI_SUGGESTED = "AI_SUGGESTED"
    IMPORTED_DATA = "IMPORTED_DATA"
    SYSTEM_GENERATED = "SYSTEM_GENERATED"