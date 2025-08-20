import enum
from uuid import UUID

from .base import Base, HypervisorType
from .disk import VirtualDisk
from .memory import MemoryStat
from .network import VirtualNetwork
from .snapshot import VirtualSnapshot


@enum.unique
class VirtualMachineState(enum.Enum):
    # Common states
    RUNNING = "Running"
    PAUSED = "Paused"
    # KVM states

    BLOCKED = "Blocked"
    SHUTDOWN = "Shutdown"
    SHUTOFF = "Shutoff"
    CRASHED = "Crashed"
    NOSTATE = "No state"

    # Hyper-V states
    OTHER = "Other"
    OFF = "Off"
    STOPPING = "Stopping"
    SAVED = "Saved"
    STARTING = "Starting"
    RESET = "Reset"
    SAVING = "Saving"
    PAUSING = "Pausing"
    RESUMING = "Resuming"
    FAST_SAVED = "FastSaved"
    FAST_SAVING = "FastSaving"
    FORCE_SHUTDOWN = "ForceShutdown"
    FORCE_REBOOT = "ForceReboot"
    HIBERNATED = "Hibernated"
    RUNNING_CRITICAL = "RunningCritical"
    OFF_CRITICAL = "OffCritical"
    STOPPING_CRITICAL = "StoppingCritical"
    SAVED_CRITICAL = "SavedCritical"
    PAUSED_CRITICAL = "PausedCritical"
    STARTING_CRITICAL = "StartingCritical"
    RESET_CRITICAL = "ResetCritical"
    SAVING_CRITICAL = "SavingCritical"
    PAUSING_CRITICAL = "PausingCritical"
    RESUMING_CRITICAL = "ResumingCritical"
    FAST_SAVED_CRITICAL = "FastSavedCritical"
    FAST_SAVING_CRITICAL = "FastSavingCritical"


class VirtualMachine(Base):
    """Essential class for managing the virtual machine"""

    def __init__(self, host: str, id: str, type: HypervisorType, auth: tuple[str, str]) -> None:
        Base.__init__(self, host, type, auth)
        self.driver = self._vm_driver(host=host, id=id, auth=auth)

    @property
    def id(self) -> UUID:
        """Get the virtual machine identifier"""
        return UUID(self.driver.id)

    def name(self) -> str:
        """Get the virtual machine name"""
        return self.driver.get_name()

    def set_name(self, name: str) -> None:
        """Set new the virtual machine name"""
        self.driver.set_name(name=name)

    def state(self) -> VirtualMachineState:
        """Get the virtual machine state"""
        return VirtualMachineState(self.driver.get_state())

    def description(self) -> str | None:
        """Get the virtual machine description"""
        return self.driver.get_description()

    def guest_os(self) -> str | None:
        """Get the name of the virtual machine guest operating system"""
        return self.driver.get_guest_os()

    def memory_stat(self) -> MemoryStat:
        """Get the memory statistic of the virtual machine"""
        return MemoryStat(**self.driver.get_memory_stat())

    def cpus(self) -> int:
        """Get cores number"""
        return self.driver.get_cpus()

    def set_cpus(self, cpus: int) -> None:
        """Change number of cores"""
        self.driver.set_cpus(cpus=cpus)

    def snapshots(self) -> list[VirtualSnapshot]:
        """Get the list of the virtual machine snapshots"""
        return [VirtualSnapshot(**snapshot) for snapshot in self.driver.get_snapshots()]

    def disks(self) -> list[VirtualDisk]:
        """Get the list of the virtual machine connected disks"""
        return [VirtualDisk(**disk) for disk in self.driver.get_disks()]

    def networks(self) -> list[VirtualNetwork]:
        """Get the list of the virtual machine network adapters"""
        return [VirtualNetwork(**net) for net in self.driver.get_networks()]

    def run(self) -> None:
        """Power on the virtual machine"""
        self.driver.run()

    def shutdown(self) -> None:
        """Shutdown the virtual machine"""
        self.driver.shutdown()

    def poweroff(self) -> None:
        """Force off the virtual machine"""
        self.driver.poweroff()

    def save(self) -> None:
        """Pause the virtual machine and temporarily saving its memory state to a file"""
        self.driver.save()

    def suspend(self) -> None:
        """Pause the virtual machine and temporarily saving its memory state"""
        self.driver.suspend()

    def resume(self) -> None:
        """Unpause the suspended virtual machine"""
        self.driver.resume()

    def snap_create(self, name: str) -> VirtualSnapshot:
        """Create a new snapshot of virtual machine"""
        snapshot = self.driver.snapshot_create(name=name)
        return VirtualSnapshot(**snapshot)

    def export(self, storage: str) -> str:
        """Export the virtual machine to a storage destination"""
        return self.driver.export(storage=storage)
