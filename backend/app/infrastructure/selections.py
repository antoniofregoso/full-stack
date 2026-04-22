from enum import Enum


class OperationalStatus(str, Enum):
    AHEAD = "AHEAD"
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    CRITICAL = "CRITICAL"


OPERATIONAL_STATUS_META: dict[OperationalStatus, dict[str, str]] = {
    OperationalStatus.AHEAD: {
        "label": "Adelantado",
        "color": "blue",
    },
    OperationalStatus.ON_TRACK: {
        "label": "En tiempo y forma",
        "color": "green",
    },
    OperationalStatus.AT_RISK: {
        "label": "Atrasado",
        "color": "yellow",
    },
    OperationalStatus.CRITICAL: {
        "label": "Muy atrasado",
        "color": "red",
    },
}
