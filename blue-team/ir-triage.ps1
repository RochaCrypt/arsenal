<#
.SYNOPSIS
    ir-triage.ps1 — read-only Windows host snapshot for incident response.

.DESCRIPTION
    Collects volatile and configuration data useful during triage WITHOUT
    modifying the system: processes, services, network connections, scheduled
    tasks, local users and startup items. Output is written to a timestamped
    folder for later review.

    Author : Alexandre Rocha (github.com/RochaCrypt)
    License: MIT

.NOTES
    DEFENSIVE / AUTHORISED USE ONLY. Run on hosts you own or are authorised to
    investigate. This script only READS state; it makes no changes.
    Run in an elevated PowerShell for complete results.

.EXAMPLE
    .\ir-triage.ps1
    .\ir-triage.ps1 -OutDir C:\Triage
#>
param(
    [string]$OutDir = "triage_$(Get-Date -Format yyyyMMdd_HHmmss)"
)

New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
Write-Host "[*] Collecting read-only triage data into $OutDir"

function Save($name, $data) {
    $path = Join-Path $OutDir "$name.txt"
    $data | Out-File -FilePath $path -Encoding utf8
    Write-Host "    [+] $name"
}

Save "system-info"      (Get-ComputerInfo | Out-String)
Save "processes"        (Get-Process | Sort-Object CPU -Descending |
                         Select-Object Id, ProcessName, CPU, Path | Format-Table -Auto | Out-String)
Save "services-running" (Get-Service | Where-Object Status -eq 'Running' |
                         Select-Object Name, DisplayName | Format-Table -Auto | Out-String)
Save "network-conns"    (Get-NetTCPConnection -ErrorAction SilentlyContinue |
                         Where-Object State -eq 'Established' |
                         Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, OwningProcess |
                         Format-Table -Auto | Out-String)
Save "scheduled-tasks"  (Get-ScheduledTask -ErrorAction SilentlyContinue |
                         Where-Object State -ne 'Disabled' |
                         Select-Object TaskName, TaskPath, State | Format-Table -Auto | Out-String)
Save "local-users"      (Get-LocalUser -ErrorAction SilentlyContinue |
                         Select-Object Name, Enabled, LastLogon | Format-Table -Auto | Out-String)
Save "startup-items"    (Get-CimInstance Win32_StartupCommand -ErrorAction SilentlyContinue |
                         Select-Object Name, Command, Location | Format-Table -Auto | Out-String)

Write-Host "[+] Done. Review the files in $OutDir"
