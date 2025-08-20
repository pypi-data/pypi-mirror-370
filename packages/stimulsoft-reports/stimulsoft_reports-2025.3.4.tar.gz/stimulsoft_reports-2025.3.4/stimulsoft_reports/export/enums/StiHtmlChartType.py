from enum import Enum


class StiHtmlChartType(Enum):
    """Enumeration describes a type of the chart in the html exports."""

    IMAGE = 1
    VECTOR = 2
    ANIMATED_VECTOR = 3