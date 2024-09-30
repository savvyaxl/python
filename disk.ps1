$data = Get-WmiObject -Class Win32_LogicalDisk  | ? {$_.DriveType -eq 3} | select DeviceID, @{N="Size";E={$_.Size /1GB}}, @{N="Free";E={$_.FreeSpace /1GB}}
foreach ($i in $data ) {
'"' + $i.DeviceID.Replace(":", "_") + 'Total":' + [int]$i.Size + ',' | Write-Host -NoNewline 
'"' + $i.DeviceID.Replace(":", "_") + 'Free":' + [int]$i.Free | Write-Host -NoNewline 
if ($i -ne $data[-1] ){
','  | Write-Host -NoNewline 
}
}
