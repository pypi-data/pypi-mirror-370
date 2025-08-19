from enum import Enum

class Direction(Enum):
    STOP    = "STOP"
    FORWARD = "FORWARD"
    REVERSE = "REVERSE"

class SpeedLevel(Enum):
    STOP    = "STOP"
    VERYLOW = "VERYLOW"
    LOW     = "LOW"
    MEDIUM  = "MEDIUM"
    HIGH    = "HIGH"