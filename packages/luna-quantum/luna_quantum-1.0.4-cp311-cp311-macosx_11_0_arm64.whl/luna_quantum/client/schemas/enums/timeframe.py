from enum import Enum


class TimeframeEnum(str, Enum):
    """Enum class for query filter timeframes."""

    today = "today"
    this_week = "last_week"
    this_month = "last_month"
    this_year = "last_year"
    all_time = "all_time"
