"""Hyper-V drivers"""

import json
import os

import winrm
from jinja2 import Template

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
TEMPLATES_DIR = os.path.join(SCRIPT_PATH, "hyperv_utils")


class HyperVirtualDriver:
    """Common class for connecting to Hyper-V server"""

    def __init__(self, host: str, auth: tuple[str, str]) -> None:
        self.host = host
        self.auth = auth
        self.winrm_session = winrm.Session(
            target=f"https://{host}:5986/wsman",
            auth=auth,
            transport="basic",
            server_cert_validation="validate",
        )

    def exec_ps(self, filename: str = "common.ps1", **kwargs) -> str:
        """Execute powershell command or script on the Hyper-V server"""
        with open(os.path.join(TEMPLATES_DIR, filename), encoding="utf-8") as file:
            template = Template(file.read())

        script = template.render(**kwargs)
        result = self.winrm_session.run_ps(script)
        if result.status_code:
            raise ValueError(result.std_err.decode())
        return result.std_out.decode().strip()


class HyperVirtualMachineDriver(HyperVirtualDriver):
    """Driver for managing the Hyper-V virtual machine"""

    def __init__(self, id: str, **kwargs) -> None:
        HyperVirtualDriver.__init__(self, **kwargs)

        self.__name = self.exec_ps(command=f"Get-VM -Id {id} | Select -Expand Name")
        self.id = id

    def get_name(self) -> str:
        """Get the virtual machine name"""
        return self.__name

    def set_name(self, name: str) -> None:
        """Change the virtual machine name"""
        self.exec_ps(command=f"Get-VM -Id {self.id} | Rename-VM -NewName '{name}'")
        self.__name = name

    def get_state(self) -> str:
        """Get the virtual machine state"""
        return self.exec_ps(command=f"Get-VM -Id {self.id} | Select -Expand State")

    def get_description(self) -> str | None:
        """Get the virtual machine description"""
        return self.exec_ps(command=f"Get-VM -Id {self.id} | Select -Expand Notes") or None

    def get_guest_os(self) -> str | None:
        """Get the name of the virtual machine guest operating system"""
        return self.exec_ps(filename="get-vmguestos.ps1", guid=self.id) or None

    def get_memory_stat(self) -> dict[str, int]:
        """Get the memory statistic of the virtual machine"""
        return json.loads(self.exec_ps(filename="get-vmmem.ps1", guid=self.id))

    def get_cpus(self) -> int:
        return int(self.exec_ps(command=f"Get-VM -Id {self.id} | Select -Expand ProcessorCount"))

    def set_cpus(self, cpus: int) -> None:
        self.exec_ps(command=f"Get-VM -Id {self.id} | Set-VMProcessor -Count {cpus}")

    def get_snapshots(self):
        """Get the list of the virtual machine snapshots"""
        snapshots = json.loads(self.exec_ps(filename="get-vmsnapshots.ps1", guid=self.id))
        for s in snapshots:
            s["driver"] = HyperVirtualSnapshotDriver(
                vm_id=self.id,
                snap_id=s["local_id"],
                winrm_session=self.winrm_session,
            )
        return snapshots

    def get_disks(self) -> list:
        """Get the list of the virtual machine connected disks"""
        disks = json.loads(self.exec_ps(filename="get-vmdisks.ps1", guid=self.id))
        for disk in disks:
            disk["driver"] = HyperVirtualDiskDriver(path=disk["path"], winrm_session=self.winrm_session)
        return disks

    def get_networks(self) -> list:
        """Get the list of the virtual machine network adapters"""
        return json.loads(self.exec_ps(filename="get-vmnetworks.ps1", guid=self.id))

    def run(self) -> None:
        """Power on the virtual machine"""
        self.exec_ps(command=f"Get-VM -Id {self.id} | Start-VM")

    def shutdown(self) -> None:
        """Shutdown the virtual machine"""
        self.exec_ps(command=f"Get-VM -Id {self.id} | Stop-VM -Force")

    def poweroff(self) -> None:
        """Force off the virtual machine"""
        self.exec_ps(command=f"Get-VM -Id {self.id} | Stop-VM -TurnOff")

    def save(self) -> None:
        """Pause the virtual machine and temporarily saving its memory state to a file"""
        self.exec_ps(command=f"Get-VM -Id {self.id} | Save-VM")

    def suspend(self) -> None:
        """Pause the virtual machine and temporarily saving its memory state"""
        self.exec_ps(command=f"Get-VM -Id {self.id} | Suspend-VM")

    def resume(self) -> None:
        """Unpause the suspended virtual machine"""
        self.exec_ps(command=f"Get-VM -Id {self.id} | Resume-VM")

    def snapshot_create(self, name: str) -> dict:
        """Create a new snapshot of virtual machine"""
        snapshot = json.loads(self.exec_ps(filename="create-vmsnapshot.ps1", guid=self.id, snap_name=name))
        snapshot["driver"] = HyperVirtualSnapshotDriver(
            vm_id=self.id,
            snap_id=snapshot["local_id"],
            winrm_session=self.winrm_session,
        )
        return snapshot

    def export(self, storage: str) -> str:
        """Export the virtual machine to a storage destination"""
        destination_path = os.path.join(storage + ":", "hyperv", "export")
        self.exec_ps(command=f"Get-VM -Id {self.id} | Export-VM -Path '{destination_path}'")
        return os.path.join(destination_path, self.get_name())


class HyperVirtualHostDriver(HyperVirtualDriver):
    """Driver for managing Hyper-V server"""

    def get_vms_id(self) -> list[str]:
        """Get list of virtual machines on the hypervisor"""
        return self.exec_ps(command="Get-VM | Select -Expand Id | Select -Expand Guid").split()

    def import_vm(self, source: str, storage: str, name: str) -> str:
        """Import a virtual machine from the source"""
        virtual_machine_path = snapshot_file_path = os.path.join(storage + ":", "hyperv", name)
        vhd_destination_path = os.path.join(virtual_machine_path, "Virtual Hard Disks")

        return self.exec_ps(
            filename="import-vm.ps1",
            source_path=os.path.join(source, "Virtual Machines"),
            virtual_machine_path=virtual_machine_path,
            vhd_destination_path=vhd_destination_path,
            snapshot_file_path=snapshot_file_path,
            target_name=name,
        )

    def get_storages(self) -> list:
        """Get information about the host storage systems"""
        return json.loads(self.exec_ps(filename="get-storages.ps1"))


class HyperVirtualSnapshotDriver(HyperVirtualDriver):
    """Driver for managing the Hyper-V snapshot"""

    def __init__(self, vm_id: str, snap_id: str, winrm_session: winrm.Session) -> None:
        self.vm_id = vm_id
        self.snap_id = snap_id
        self.winrm_session = winrm_session

    def apply(self) -> None:
        """Apply the snapshot"""
        self.exec_ps(
            command=(
                f"Get-VM -Id {self.vm_id} | Get-VMSnapshot | "
                f"Where {{$_.Id.Guid -eq '{self.snap_id}'}} | Restore-VMSnapshot -Confirm:$false"
            )
        )

    def destroy(self) -> None:
        """Destroy the snapshot"""
        self.exec_ps(
            command=(
                f"Get-VM -Id {self.vm_id} | Get-VMSnapshot | "
                f"Where {{$_.Id.Guid -eq '{self.snap_id}'}} | Remove-VMSnapshot"
            )
        )


class HyperVirtualDiskDriver(HyperVirtualDriver):
    """Driver for managing the Hyper-V virtual disk"""

    def __init__(self, path: str, winrm_session: winrm.Session) -> None:
        self.path = path
        self.winrm_session = winrm_session

    def resize(self, required_size: int) -> int:
        """Resize the virtual disk"""
        new_size = self.exec_ps(
            command=(
                f"Resize-VHD -Path '{self.path}' -SizeBytes '{required_size}' ; if ($?) "
                f"{{ Get-VHD -Path '{self.path}' | Select -Expand Size }}"
            )
        )
        return int(new_size)
