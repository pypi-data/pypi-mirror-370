try {
    $Disks = $(Get-WmiObject win32_logicaldisk | Where {$_.DriveType -eq '3'})
    $result = $Disks | Select @{Name='name';Expression={$_.DeviceID[0]}},
        @{Name='size';Expression={[Math]::Round($_.Size)}},
        @{Name='used';Expression={[Math]::Round($_.Size - $_.FreeSpace)}}
        
    ConvertTo-Json @(,$result)
}
catch {
    $host.ui.WriteErrorLine($_.Exception.Message)
    exit 1
}
