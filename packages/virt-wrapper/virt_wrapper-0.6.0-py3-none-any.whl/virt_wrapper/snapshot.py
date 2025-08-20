"""Module for managing the virtual machine snapshots"""

from dataclasses import InitVar, dataclass, field
from datetime import datetime

from .drivers.hyperv import HyperVirtualSnapshotDriver
from .drivers.kvm import KernelVirtualSnapshotDriver


@dataclass
class VirtualSnapshot:
    """Data structure that contains the virtual machine snapshot info"""

    driver: InitVar[HyperVirtualSnapshotDriver | KernelVirtualSnapshotDriver]
    timestamp: InitVar[int]
    created_at: datetime = field(init=False)
    local_id: str
    name: str
    parent_name: str
    is_applied: bool
    cpus: int
    ram: int
    description: str | None = None

    def __post_init__(self, driver: HyperVirtualSnapshotDriver | KernelVirtualSnapshotDriver, timestamp: int):
        self.__driver = driver
        self.created_at = datetime.fromtimestamp(timestamp)

    def apply(self) -> None:
        """Apply the snapshot"""
        self.__driver.apply()

    def destroy(self) -> None:
        """Destroy the snapshot"""
        self.__driver.destroy()
