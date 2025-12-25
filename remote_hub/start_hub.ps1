# Startet Node (3000) + Python (8503) und macht einen sicheren Health-Check.
# Fix: URLs werden mit Invoke-WebRequest geprüft (nicht als Befehl ausgeführt).

$ErrorActionPreference = "Stop"

$HostIp = $env:REMOTE_HUB_HOST
if ([string]::IsNullOrWhiteSpace($HostIp)) { $HostIp = "127.0.0.1" }

$NodePort = 3000
$ApiPort = 8503

Write-Host "--- Remote Hub Start ---" -ForegroundColor Cyan

# Ports freigeben
foreach ($p in @($NodePort, $ApiPort)) {
  $conn = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) {
    Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    Write-Host "Port $p freigegeben." -ForegroundColor Yellow
  }
}

Push-Location $PSScriptRoot

Write-Host "Starte Python API..." -ForegroundColor Green
$py = Start-Process -FilePath "python" -ArgumentList "webhook_server.py" -PassThru

Write-Host "Starte Node Server..." -ForegroundColor Green
$node = Start-Process -FilePath "node" -ArgumentList "server.mjs" -PassThru

Start-Sleep -Seconds 2

try {
  $res1 = Invoke-WebRequest -Uri "http://$HostIp:$NodePort/health" -UseBasicParsing -TimeoutSec 5
  $res2 = Invoke-WebRequest -Uri "http://$HostIp:$ApiPort/health" -UseBasicParsing -TimeoutSec 5
  Write-Host "OK: Node + API sind online." -ForegroundColor Green
  Write-Host "UI:    http://$HostIp:$NodePort/mobile" -ForegroundColor White
  Write-Host "Stats: http://$HostIp:$ApiPort/stats" -ForegroundColor White
}
catch {
  Write-Host "WARN: Health-Check fehlgeschlagen: $_" -ForegroundColor Red
  Write-Host "Node PID: $($node.Id) | Python PID: $($py.Id)" -ForegroundColor DarkGray
}

Pop-Location
