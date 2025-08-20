"""Essential classes for managing hypervisors and virtual machines"""

import enum

from .drivers.hyperv import HyperVirtualHostDriver, HyperVirtualMachineDriver
from .drivers.kvm import KernelVirtualHostDriver, KernelVirtualMachineDriver


@enum.unique
class HypervisorType(enum.Enum):
    KVM = "kvm"
    HYPERV = "hyperv"


class Base:
    def __init__(self, host: str, type: HypervisorType, auth: tuple[str, str]):
        if type == HypervisorType.KVM:
            self._host_driver = KernelVirtualHostDriver
            self._vm_driver = KernelVirtualMachineDriver
        elif type == HypervisorType.HYPERV:
            self._host_driver = HyperVirtualHostDriver
            self._vm_driver = HyperVirtualMachineDriver
        else:
            raise Exception("Unknown type")

        self.host = host
        self.type = type
        self.auth = auth
