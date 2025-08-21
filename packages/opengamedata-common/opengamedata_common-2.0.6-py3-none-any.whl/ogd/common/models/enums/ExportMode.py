# import standard libraries
from enum import IntEnum

class ExportMode(IntEnum):
    SESSION = 1
    PLAYER = 2
    POPULATION = 3
    FEATURES = 4
    EVENTS = 5
    DETECTORS = 6

    def __str__(self):
        return self.name
