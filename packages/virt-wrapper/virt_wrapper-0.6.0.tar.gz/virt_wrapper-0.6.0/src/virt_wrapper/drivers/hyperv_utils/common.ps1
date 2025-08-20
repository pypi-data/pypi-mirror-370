try {
    {{ command }}  
}
catch {
    $host.ui.WriteErrorLine($_.Exception.Message)
    exit 1
}
