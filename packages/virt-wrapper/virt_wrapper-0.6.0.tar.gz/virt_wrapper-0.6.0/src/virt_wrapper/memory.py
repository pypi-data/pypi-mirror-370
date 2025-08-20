"""Module for managing the virtual machine memory"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryStat:
    """Data structure that contains the virtual machine memory statistic"""

    startup: int
    maximum: int
    demand: int
    assigned: int
