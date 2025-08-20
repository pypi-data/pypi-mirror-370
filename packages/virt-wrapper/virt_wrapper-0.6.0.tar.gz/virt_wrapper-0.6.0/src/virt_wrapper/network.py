"""Module for managing the virtual machine networks"""

from dataclasses import dataclass


@dataclass(frozen=True)
class VirtualNetwork:
    """Data structure that contains the virtual machine network info"""

    mac: str
    switch: str
    addresses: list[str]
