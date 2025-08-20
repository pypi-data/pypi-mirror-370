param(
    [string]$VMGuid = "{{ guid }}"
)

try {
    ConvertTo-Json -Compress (Get-VM -Id $VMGuid | Select `
        @{Name="startup";Expression={$_.MemoryStartup/1024}},
        @{Name="maximum";Expression={$_.MemoryMaximum/1024}},
        @{Name="demand";Expression={$_.MemoryDemand/1024}},
        @{Name="assigned";Expression={$_.MemoryAssigned/1024}}
    )
        
}
catch {
    $host.ui.WriteErrorLine($_.Exception.Message)
    exit 1
}