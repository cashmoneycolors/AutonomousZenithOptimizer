# Schneller GitHub Auth Fix
Write-Host "Erneuere GitHub Token..." -ForegroundColor Cyan

# Methode 1: Token löschen und neu setzen
try {
    # Git Credential Helper neu setzen
    git config --global credential.helper manager
    
    # Alte Credentials löschen
    cmdkey /delete:git:https://github.com 2>$null
    
    Write-Host "✓ Alte Credentials entfernt" -ForegroundColor Green
    Write-Host ""
    Write-Host "Bitte jetzt neu anmelden mit:" -ForegroundColor Yellow
    Write-Host "  gh auth login" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Oder beim nächsten git push/pull werden Sie nach Credentials gefragt." -ForegroundColor Yellow
}
catch {
    Write-Host "Fehler: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Schnell-Kommandos ===" -ForegroundColor Cyan
Write-Host "1. gh auth login                    # GitHub CLI Login" -ForegroundColor White
Write-Host "2. gh auth refresh                  # Token erneuern" -ForegroundColor White
Write-Host "3. git push                         # Zum Testen" -ForegroundColor White
