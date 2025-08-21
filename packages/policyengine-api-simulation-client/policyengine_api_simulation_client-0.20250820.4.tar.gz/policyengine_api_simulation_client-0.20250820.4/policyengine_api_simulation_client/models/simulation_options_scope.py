from enum import Enum


class SimulationOptionsScope(str, Enum):
    HOUSEHOLD = "household"
    MACRO = "macro"

    def __str__(self) -> str:
        return str(self.value)
