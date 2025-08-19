from enum import Enum


class ModelFormat(str, Enum):
    """Enumeration of all supported formats."""

    AQ_MODEL = "AQ_MODEL"
    LP = "LP"
    QUBO = "QUBO_MATRIX"
    CQM = "CQM"
    BQM = "BQM"
