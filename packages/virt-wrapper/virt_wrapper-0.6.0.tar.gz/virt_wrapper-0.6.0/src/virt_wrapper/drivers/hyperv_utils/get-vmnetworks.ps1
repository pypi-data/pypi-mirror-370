param(
    [string]$VMGuid = "{{ guid }}"
)

try {
    ConvertTo-Json @(Get-VM -Id $VMGuid | Get-VMNetworkAdapter | Select `
        @{Name='mac';Expression={($_.MacAddress -Split '(..)').Where({$_}) -Join ':'}},
        @{Name='switch';Expression={$_.SwitchName}},
        @{Name='addresses';Expression={$_.IPAddresses}}
    )
}
catch {
    $host.ui.WriteErrorLine($_.Exception.Message)
    exit 1
}