"""Module for managing the virtual machine disks"""

from dataclasses import InitVar, dataclass
from pathlib import Path

from .drivers.hyperv import HyperVirtualDiskDriver
from .drivers.kvm import KernelVirtualDiskDriver


@dataclass
class VirtualDisk:
    """Data structure that contains the virtual machine disk info"""

    driver: InitVar[HyperVirtualDiskDriver | KernelVirtualDiskDriver]
    name: str
    path: str | Path
    storage: str
    size: int
    used: int

    def __post_init__(self, driver):
        self.__driver = driver
        self.path = Path(self.path)

    def resize(self, required_size: int) -> None:
        """Resize the virtual disk"""
        self.size = self.__driver.resize(required_size)
