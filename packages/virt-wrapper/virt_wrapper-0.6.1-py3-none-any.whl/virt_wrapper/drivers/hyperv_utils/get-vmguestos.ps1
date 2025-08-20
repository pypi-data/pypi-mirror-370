param(
    [string]$VMGuid = "{{ guid }}"
)

try {
    (Get-WmiObject -Namespace root\virtualization\v2 -Query "Select * From Msvm_SummaryInformation Where Name='$VMGuid'").GuestOperatingSystem
}
catch {
    $host.ui.WriteErrorLine($_.Exception.Message)
    exit 1
}
