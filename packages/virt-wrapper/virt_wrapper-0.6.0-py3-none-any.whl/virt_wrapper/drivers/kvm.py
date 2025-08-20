"""KVM drivers"""

import os
from datetime import datetime
from random import randint
from xml.etree import ElementTree as ET

import libvirt

from .common import request_cred  # pylint: disable=relative-beyond-top-level

STATES = {
    libvirt.VIR_DOMAIN_RUNNING: "Running",
    libvirt.VIR_DOMAIN_BLOCKED: "Blocked",
    libvirt.VIR_DOMAIN_PAUSED: "Paused",
    libvirt.VIR_DOMAIN_SHUTDOWN: "Shutdown",
    libvirt.VIR_DOMAIN_SHUTOFF: "Shutoff",
    libvirt.VIR_DOMAIN_CRASHED: "Crashed",
    libvirt.VIR_DOMAIN_NOSTATE: "No state",
}


def libvirt_callback(userdata, err):  # pylint: disable=unused-argument
    """Avoid printing error messages"""


libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)


SSH_PRIVATE_KEY = os.environ.get("SSH_PRIVATE_KEY", os.path.join(os.path.expanduser("~"), ".ssh", "id_rsa"))


class KernelVirtualDriver:
    """Common class for connecting to KVM server"""

    def __init__(
        self,
        host: str,
        auth: tuple[str, str] = ("", ""),
        ssh_key: str = SSH_PRIVATE_KEY,
    ) -> None:
        self.host = host
        user, password = auth
        if password:
            authd = [
                [libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE],
                request_cred(user, password),
                None,
            ]
            self.conn = libvirt.openAuth(
                f"qemu+libssh2://{user}@{host}/system?sshauth=password&known_hosts_verify=auto",
                authd,
                0,
            )
        elif ssh_key:
            self.conn = libvirt.open(
                f"qemu+libssh2://{user}@{host}/system?sshauth=privkey&keyfile={ssh_key}&known_hosts_verify=auto"
            )
        else:
            raise ValueError("At least one SSH key or password is required")


class KernelVirtualMachineDriver(KernelVirtualDriver):
    """Driver for managing the KVM virtual machine"""

    def __init__(self, id: str | None = None, **kwargs) -> None:
        KernelVirtualDriver.__init__(self, **kwargs)
        self.domain = self.conn.lookupByUUIDString(id)
        self.id = self.domain.UUIDString()

    def get_name(self) -> str:
        """Get the virtual machine name"""
        try:
            return self.domain.metadata(libvirt.VIR_DOMAIN_METADATA_TITLE, None)
        except libvirt.libvirtError:
            return self.domain.name()

    def get_state(self) -> str:
        """Get the virtual machine state"""
        state, _ = self.domain.state()
        return STATES[state]

    def set_name(self, name: str) -> None:
        """Change the virtual machine name"""
        self.domain.setMetadata(libvirt.VIR_DOMAIN_METADATA_TITLE, name, None, None)

    def get_description(self) -> str | None:
        """Get the virtual machine description"""
        try:
            return self.domain.metadata(libvirt.VIR_DOMAIN_METADATA_DESCRIPTION, None)
        except libvirt.libvirtError:
            return None

    def get_guest_os(self) -> str | None:
        """Get the name of the virtual machine guest operating system"""
        try:
            return self.domain.guestInfo().get("os.pretty-name")
        except libvirt.libvirtError:
            return None

    def get_memory_stat(self) -> dict[str, int]:
        """Get the memory statistic of the virtual machine"""
        if self.domain.state()[0] == libvirt.VIR_DOMAIN_SHUTOFF:
            actual = 0
            demand = 0
        else:
            actual = self.domain.memoryStats().get("actual")
            demand = actual - self.domain.memoryStats().get("unused", actual)

        return {
            "startup": self.domain.info()[2],
            "maximum": self.domain.maxMemory(),
            "demand": demand if demand >= 0 else 0,
            "assigned": actual,
        }

    def get_cpus(self) -> int:
        return self.domain.info()[3]

    def set_cpus(self, cpus: int) -> None:
        self.domain.setVcpusFlags(cpus, libvirt.VIR_DOMAIN_VCPU_MAXIMUM | libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        self.domain.setVcpusFlags(cpus, libvirt.VIR_DOMAIN_AFFECT_CONFIG)

    def get_snapshots(self) -> list:
        """Get the list of the virtual machine snapshots"""
        ret = []
        for snap in self.domain.listAllSnapshots():
            tree_snap = ET.fromstring(snap.getXMLDesc())

            cpus = tree_snap.find("domain/vcpu")
            ram = tree_snap.find("domain/currentMemory")
            description = tree_snap.find("description")
            timestamp = tree_snap.find("creationTime")
            try:
                parent = snap.getParent().getName()
            except libvirt.libvirtError:
                parent = None
            ret.append(
                {
                    "name": snap.getName(),
                    "description": description.text if description else None,
                    "local_id": snap.getName(),
                    "parent_name": parent,
                    "timestamp": int(timestamp.text) if timestamp is not None else 0,
                    "is_applied": snap.getName() == self.domain.snapshotCurrent().getName(),
                    "cpus": int(cpus.text) if cpus is not None else 0,
                    "ram": int(ram.text) if ram is not None else 0,
                    "driver": KernelVirtualSnapshotDriver(vm_id=self.id, snap_id=snap.getName(), conn=self.conn),
                }
            )

        return ret

    def get_disks(self) -> list[dict]:
        """Get the list of the virtual machine connected disks"""
        ret = []
        for src in ET.fromstring(self.domain.XMLDesc()).findall("devices/disk/source"):
            try:
                if src.get("pool"):
                    storage_pool = self.conn.storagePoolLookupByName(src.get("pool"))
                    volume = storage_pool.storageVolLookupByName(src.get("volume"))
                else:
                    volume = self.conn.storageVolLookupByPath(src.get("file"))
                    storage_pool = volume.storagePoolLookupByVolume()
                _, size, used = volume.info()
                ret.append(
                    {
                        "driver": KernelVirtualDiskDriver(path=volume.path(), domain=self.domain),
                        "name": volume.name(),
                        "path": volume.path(),
                        "storage": storage_pool.name(),
                        "size": size,
                        "used": used,
                    }
                )
            except libvirt.libvirtError:
                continue
        return ret

    def get_networks(self) -> list:
        """Get the list of the virtual machine network adapters"""
        ret = []
        for interface in ET.fromstring(self.domain.XMLDesc()).findall("devices/interface"):
            mac = interface.find("mac").get("address", "")
            switch_name = interface.find("source").get("bridge", "")

            if self.domain.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
                try:
                    nets = self.domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT)
                except libvirt.libvirtError:
                    nets = self.domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_ARP)
                addresses = []
                for net in nets:
                    if nets[net].get("hwaddr") == mac:
                        addrs = nets[net].get("addrs")
                        address = [addr.get("addr") for addr in addrs]
                        addresses.extend(address)
                        break
            else:
                addresses = []

            ret.append({"mac": mac.upper(), "switch": switch_name, "addresses": addresses})
        return ret

    def get_displays(self) -> list[dict]:
        ret = []
        for display in ET.fromstring(self.domain.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE)).findall("devices/graphics"):
            ret.append(
                {
                    "Type": display.get("type"),
                    "Port": display.get("port"),
                    "Password": display.get("passwd"),
                }
            )
        return ret

    def run(self) -> None:
        """Power on the virtual machine"""
        self.domain.create()

    def shutdown(self) -> None:
        """Shutdown the virtual machine"""
        self.domain.shutdown()

    def poweroff(self) -> None:
        """Force off the virtual machine"""
        self.domain.destroy()

    def save(self) -> None:
        """Pause the virtual machine and temporarily saving its memory state to a file"""
        self.domain.managedSave()

    def suspend(self) -> None:
        """Pause the virtual machine and temporarily saving its memory state"""
        self.domain.suspend()

    def resume(self) -> None:
        """Unpause the suspended virtual machine"""
        self.domain.resume()

    def snapshot_create(self, name: str) -> dict:
        """Create a new snapshot of virtual machine"""
        snapshot_xml_template = f"""<domainsnapshot><name>{name}</name></domainsnapshot>"""
        self.domain.snapshotCreateXML(snapshot_xml_template, libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_ATOMIC)
        for snap in self.get_snapshots():
            if snap["name"] == name:
                return snap
        raise Exception("Created snapshot wasn't found")

    def export(self, storage: str) -> str:
        """Export the virtual machine to a storage destination"""
        pool = self.conn.storagePoolLookupByName(storage)
        pool_path = ET.fromstring(pool.XMLDesc()).find("target/path").text
        target_pool_path = os.path.join(pool_path, self.get_name())
        target_pool_name = f"export_{self.get_name()}"

        xml_pool = f"""<pool type='dir'>
  <name>{target_pool_name}</name>
  <target>
    <path>{target_pool_path}</path>
    <permissions>
      <mode>0777</mode>
    </permissions>
  </target>
</pool>
"""
        target_pool = self.domain.connect().storagePoolCreateXML(xml_pool, libvirt.VIR_STORAGE_POOL_CREATE_WITH_BUILD)
        try:
            for disk in self.get_disks():
                volume = self.conn.storageVolLookupByPath(disk["path"])
                xml_vol = f"""<volume>
  <name>{volume.name()}</name>
  <target>
    <permissions>
      <mode>0644</mode>
      <label>virt_image_t</label>
    </permissions>
  </target>
</volume>"""
                target_pool.createXMLFrom(xml_vol, volume, 0)
        finally:
            target_pool.destroy()

        with open(os.path.join(target_pool_path, "config.xml"), "w", encoding="utf-8") as config:
            config.write(
                self.domain.XMLDesc(
                    libvirt.VIR_DOMAIN_XML_INACTIVE
                    | libvirt.VIR_DOMAIN_XML_UPDATE_CPU
                    | libvirt.VIR_DOMAIN_XML_MIGRATABLE
                )
            )
        return target_pool_path


class KernelVirtualHostDriver(KernelVirtualDriver):
    """Driver for managing KVM server"""

    def __init__(self, **kwargs) -> None:
        KernelVirtualDriver.__init__(self, **kwargs)
        # self.host = kwarhost

    def get_vms_id(self) -> list[str]:
        """Get list of virtual machines on the hypervisor"""
        return [domain.UUIDString() for domain in self.conn.listAllDomains()]

    def import_vm(self, source: str, storage: str, name: str) -> str:
        """Import a virtual machine from the source"""
        xml_pool = f"""<pool type='dir'>
  <name>import_{name}</name>
  <target>
    <path>{source}</path>
  </target>
</pool>"""
        root = ET.parse(os.path.join(source, "config.xml")).getroot()

        uuid = root.find("uuid")
        if uuid is not None:
            root.remove(uuid)

        xml_name = root.find("name")
        if xml_name is None:
            xml_name = ET.SubElement(root, xml_name)
            root.insert(3, xml_name)
        xml_name.text = name

        xml_title = root.find("title")
        if xml_title is None:
            xml_title = ET.SubElement(root, xml_title)
            root.insert(3, xml_title)
        xml_title.text = name

        def random_suffix():
            return "_%s_%s" % (
                int((datetime.now() - datetime(1970, 1, 1)).total_seconds()),
                "".join(["%02x" % randint(0x00, 0xFF) for _ in range(10)]),
            )

        target_pool = self.conn.storagePoolLookupByName(storage)
        import_pool = self.conn.storagePoolCreateXML(xml_pool, libvirt.VIR_STORAGE_POOL_CREATE_WITH_BUILD)
        imported_volumes = []
        try:
            for src in root.iterfind("devices/disk/source"):
                orig_filename = os.path.basename(src.get("file") or src.get("volume"))
                import_vol = import_pool.storageVolLookupByName(orig_filename)

                disk_suffix = random_suffix()
                filename = orig_filename
                while filename in target_pool.listVolumes():
                    filename = name + disk_suffix + os.path.splitext(orig_filename)[-1]
                    disk_suffix = random_suffix()

                xml_vol = f"""<volume>
  <name>{filename}</name>
  <target>
    <format type='qcow2'/>
    <permissions>
      <mode>0600</mode>
      <label>virt_image_t</label>
    </permissions>
  </target>
</volume>"""
                target_vol = target_pool.createXMLFrom(xml_vol, import_vol, 0)
                if src.get("file"):
                    src.set("file", target_vol.path())
                elif src.get("volume"):
                    src.set("pool", target_pool.name())
                    src.set("volume", target_vol.name())

                imported_volumes.append(target_vol)
        except Exception as e:
            for volume in imported_volumes:
                volume.destroy()
            raise e
        finally:
            import_pool.destroy()

        for interface in root.findall("devices/interface"):
            for remove_target in (
                "mac",
                "address",
            ):  # Remove some options, they will be chosen automatically
                try:
                    interface.remove(interface.find(remove_target))
                except TypeError:
                    continue

        result_domain = self.conn.defineXML(ET.tostring(root, encoding="unicode"))
        return result_domain.UUIDString()

    def get_storages(self) -> list:
        """Get information about the host storage systems"""
        result = []
        for pool in self.conn.listAllStoragePools():
            info = pool.info()
            result.append(
                {
                    "name": pool.name(),
                    "size": info[1],
                    "used": info[1] - info[3],
                }
            )
        return result


class KernelVirtualSnapshotDriver:
    """Driver for managing the KVM snapshot"""

    def __init__(self, vm_id: str, snap_id: str, conn: libvirt.virConnect) -> None:
        self.domain = conn.lookupByUUIDString(vm_id)
        self.snap_id = snap_id

    def apply(self) -> None:
        """Apply the snapshot"""
        snap = self.domain.snapshotLookupByName(self.snap_id)
        self.domain.revertToSnapshot(snap)

    def destroy(self) -> None:
        """Destroy the snapshot"""
        snap = self.domain.snapshotLookupByName(self.snap_id)
        snap.delete()


class KernelVirtualDiskDriver:
    """Driver for managing the KVM virtual disk"""

    def __init__(self, path: str, domain: libvirt.virDomain) -> None:
        self.domain = domain
        self.volume = domain.connect().storageVolLookupByPath(path)

    def resize(self, required_size: int) -> int:
        """Resize the virtual disk"""
        if self.domain.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
            self.domain.blockResize(self.volume.path(), required_size)
        else:
            self.volume.resize(required_size, libvirt.VIR_STORAGE_VOL_RESIZE_SHRINK)

        return self.volume.info()[1]
