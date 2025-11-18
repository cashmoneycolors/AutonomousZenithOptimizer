# Docker Desktop Fix Script für Windows 10
# Dieses Skript behebt häufige Probleme mit Docker Desktop, indem es WSL2 aktiviert und konfiguriert.

Write-Host "Docker Desktop Fix Script gestartet..." -ForegroundColor Green

# 1. Prüfen, ob WSL installiert ist
Write-Host "Prüfe WSL-Status..." -ForegroundColor Yellow
try {
    $wslOutput = wsl --list --verbose 2>&1
    if ($wslOutput -match "No distributions installed") {
        Write-Host "WSL nicht installiert. Installiere Ubuntu..." -ForegroundColor Yellow
        wsl --install -d Ubuntu
        Write-Host "Ubuntu installiert. Starte neu..." -ForegroundColor Green
        Restart-Computer -Force
    } else {
        Write-Host "WSL ist installiert:" -ForegroundColor Green
        Write-Host $wslOutput
    }
} catch {
    Write-Host "Fehler bei WSL-Prüfung: $_" -ForegroundColor Red
}

# 2. WSL2 als Standard setzen
Write-Host "Setze WSL2 als Standardversion..." -ForegroundColor Yellow
wsl --set-default-version 2

# 3. Prüfen, ob Docker Desktop läuft
Write-Host "Prüfe Docker-Status..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "Docker CLI gefunden: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "Docker CLI nicht gefunden. Installiere Docker Desktop..." -ForegroundColor Red
    # Installiere Docker Desktop mit winget
    winget install --id Docker.DockerDesktop -e --accept-package-agreements --accept-source-agreements
}

# 4. Anweisungen für den Benutzer
Write-Host ""
Write-Host '=== NÄCHSTE SCHRITTE ===' -ForegroundColor Cyan
Write-Host '1. Schließe alle PowerShell-Fenster und VS Code.' -ForegroundColor White
Write-Host '2. Öffne Docker Desktop als Administrator (Rechtsklick > Als Administrator ausführen).' -ForegroundColor White
Write-Host '3. In Docker Desktop: Gehe zu Settings > General > Aktiviere ''Use the WSL 2 based engine''.' -ForegroundColor White
Write-Host '4. Gehe zu Settings > Resources > WSL Integration > Aktiviere Ubuntu.' -ForegroundColor White
Write-Host '5. Klicke auf ''Apply & Restart''.' -ForegroundColor White
Write-Host '6. Warte, bis Docker Desktop vollständig gestartet ist (grünes Icon).' -ForegroundColor White
Write-Host '7. Öffne VS Code und versuche den Dev Container neu zu bauen.' -ForegroundColor White
Write-Host ''
Write-Host 'Wenn es immer noch nicht funktioniert, deinstalliere Docker Desktop komplett und installiere es neu.' -ForegroundColor Yellow
