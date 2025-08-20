param(
    [string]$VMGuid = "{{ guid }}"
)

try {
    function GetParentDisk ($Disk) {
        $CurrentDisk = $Disk
        while ($CurrentDisk.ParentPath) {
            $CurrentDisk = Get-VHD $CurrentDisk.ParentPath
        }
        return $CurrentDisk
    }

    $vhds = Get-VM -Id $VMGuid | Get-VMHardDiskDrive | Get-VHD

    $res = @()

    foreach($vhd in $vhds) {
        $vhd_folder = Split-Path -Parent -Resolve $vhd.Path
        $relative_disks = Get-VHD $(Join-Path -Path $vhd_folder -ChildPath "*") | Where-Object {$_.DiskIdentifier -eq $vhd.DiskIdentifier }
        $parent_disk = GetParentDisk $vhd

        $disk = @{}
        $disk.name = $parent_disk.Path | Split-Path -Leaf
        $disk.path = $parent_disk.Path
        $disk.storage = (Get-Item $vhd.Path).PSDrive.Name
        $disk.size = $vhd.Size
        $disk.used = ($relative_disks | ForEach-Object -MemberName FileSize | Measure-Object -Sum).Sum

        $res += $disk
    }
    ConvertTo-Json -Compress $res
}
catch {
    $host.ui.WriteErrorLine($_.Exception.Message)
    exit 1
}
