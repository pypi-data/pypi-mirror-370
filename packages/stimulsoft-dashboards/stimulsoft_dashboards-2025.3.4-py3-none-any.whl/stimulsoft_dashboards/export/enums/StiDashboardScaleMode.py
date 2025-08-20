from enum import Enum


class StiDashboardScaleMode(Enum):

    PAPER_SIZE = 0
    """Only for PDF export format."""

    VIEW_SIZE = 1
    DESIGN_SIZE = 2
    