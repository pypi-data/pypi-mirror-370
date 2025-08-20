"""Module for managing the hosts storages"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Storage:
    """Data structure that contains information about the host storage systems"""

    name: str
    size: int
    used: int
