from enum import Enum


class MarketingDecisionStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    PROPOSED = "PROPOSED"
    UNKNOWN = "UNKNOWN"


class MarketingRequirementType(str, Enum):
    OBJECTIVE = "OBJECTIVE"
    TARGET_AUDIENCE = "TARGET_AUDIENCE"
    OFFER = "OFFER"
    CHANNEL = "CHANNEL"
    BUDGET = "BUDGET"
    TIMELINE = "TIMELINE"
    GEOGRAPHY = "GEOGRAPHY"
    CONSTRAINT = "CONSTRAINT"
    KPI = "KPI"