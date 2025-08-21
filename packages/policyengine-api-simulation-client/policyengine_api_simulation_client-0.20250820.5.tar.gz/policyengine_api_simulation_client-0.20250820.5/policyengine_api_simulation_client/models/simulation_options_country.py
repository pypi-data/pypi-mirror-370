from enum import Enum


class SimulationOptionsCountry(str, Enum):
    UK = "uk"
    US = "us"

    def __str__(self) -> str:
        return str(self.value)
