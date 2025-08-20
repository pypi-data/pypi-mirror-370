param(
    [string]$SourcePath = "{{ source_path }}",
    [string]$VirtualMachinePath = "{{ virtual_machine_path }}",
    [string]$VhdDestinationPath = "{{ vhd_destination_path }}",
    [string]$SnapshotFilePath = "{{ snapshot_file_path }}",
    [string]$TargetName = "{{ target_name }}"
)

try {
    $vmcx = (Get-ChildItem -Path "$SourcePath" -Filter *.vmcx -Recurse).VersionInfo.FileName
    $TargetVM = Import-VM "$vmcx" -GenerateNewId -Copy -VirtualMachinePath "$TargetPath" `
        -VhdDestinationPath "$VhdDestinationPath" `
        -SnapshotFilePath "$SnapshotFilePath"
        
    Rename-VM -VM $TargetVM -NewName "$TargetName"
    $TargetVM.Id.Guid
}
catch {
    $host.ui.WriteErrorLine($_.Exception.Message)
    exit 1
}
