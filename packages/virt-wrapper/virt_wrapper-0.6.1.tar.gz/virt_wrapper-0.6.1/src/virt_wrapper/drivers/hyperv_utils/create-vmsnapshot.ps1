param(
    [string]$VMGuid = "{{ guid }}",
    [string]$SnapName = "{{ snap_name }}"
)

try {
    $snap = Get-VM -Id $VMGuid | Checkpoint-VM -SnapshotName $SnapName -Passthru
    $snap | Select `
        @{Name='local_id';Expression={$_.Id.Guid}},
        @{Name='name';Expression={$_.Name}},
        @{Name='parent_name';Expression={$_.ParentSnapshotName}},
        @{Name='timestamp';Expression={[int64](($_.CreationTime.ToUniversalTime())-(Get-Date "1/1/1970")).TotalSeconds}},
        @{Name='is_applied';Expression={$_.Name -eq $vm.ParentSnapshotName}},
        @{Name='cpus'; Expression={$_.ProcessorCount}},
        @{Name='ram';Expression={$_.MemoryStartup / 1024 }} | ConvertTo-Json -Compress
}
catch {
    $host.ui.WriteErrorLine($_.Exception.Message)
    exit 1
}
