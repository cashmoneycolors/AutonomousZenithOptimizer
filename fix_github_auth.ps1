# GitHub Authentication Fix Script
# Behebt den 401 Token Expired Fehler

Write-Host "=== GitHub Token Refresh Script ===" -ForegroundColor Cyan
Write-Host ""

# Option 1: Token über gh CLI erneuern
Write-Host "Option 1: GitHub CLI Token erneuern (empfohlen)" -ForegroundColor Green
Write-Host "Führe aus: gh auth refresh -h github.com -s repo,workflow,gist,read:org" -ForegroundColor Yellow
Write-Host ""

# Option 2: Neu anmelden
Write-Host "Option 2: Neu bei GitHub anmelden" -ForegroundColor Green
Write-Host "Führe aus: gh auth login" -ForegroundColor Yellow
Write-Host ""

# Option 3: Git Credential Manager löschen und neu setzen
Write-Host "Option 3: Git Credentials zurücksetzen" -ForegroundColor Green
Write-Host "Führe aus:" -ForegroundColor Yellow
Write-Host "  git credential-manager-core erase" -ForegroundColor Yellow
Write-Host "  dann: gh auth login" -ForegroundColor Yellow
Write-Host ""

# Option 4: Manuelles PAT
Write-Host "Option 4: Neues Personal Access Token (PAT) erstellen" -ForegroundColor Green
Write-Host "1. Gehe zu: https://github.com/settings/tokens" -ForegroundColor Yellow
Write-Host "2. Klicke 'Generate new token (classic)'" -ForegroundColor Yellow
Write-Host "3. Wähle Scopes: repo, workflow, gist, read:org" -ForegroundColor Yellow
Write-Host "4. Kopiere das Token" -ForegroundColor Yellow
Write-Host "5. Führe aus: git config --global credential.helper manager" -ForegroundColor Yellow
Write-Host "6. Beim nächsten git push/pull Token als Passwort eingeben" -ForegroundColor Yellow
Write-Host ""

# Automatischer Versuch
Write-Host "=== Automatischer Fix-Versuch ===" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Möchten Sie einen automatischen Token-Refresh versuchen? (j/n)"

if ($choice -eq 'j' -or $choice -eq 'J' -or $choice -eq 'y' -or $choice -eq 'Y') {
    Write-Host "Starte Token-Refresh..." -ForegroundColor Green
    
    try {
        # Versuche gh auth refresh
        $process = Start-Process -FilePath "gh" -ArgumentList "auth", "refresh", "-h", "github.com", "-s", "repo,workflow,gist,read:org" -NoNewWindow -Wait -PassThru
        
        if ($process.ExitCode -eq 0) {
            Write-Host "✓ Token erfolgreich erneuert!" -ForegroundColor Green
            
            # Git Credentials aktualisieren
            Write-Host "Aktualisiere Git Credentials..." -ForegroundColor Yellow
            git config --global credential.helper manager
            
            Write-Host ""
            Write-Host "=== Fertig! ===" -ForegroundColor Green
            Write-Host "Sie können jetzt git push/pull verwenden." -ForegroundColor Green
        }
        else {
            Write-Host "⚠ Token-Refresh fehlgeschlagen. Bitte manuell anmelden." -ForegroundColor Red
            Write-Host "Führe aus: gh auth login" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "❌ Fehler: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Bitte manuell mit 'gh auth login' anmelden." -ForegroundColor Yellow
    }
}
else {
    Write-Host "Abgebrochen. Bitte wählen Sie eine der obigen Optionen manuell aus." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Zusätzliche Hinweise ===" -ForegroundColor Cyan
Write-Host "- Wenn alle Optionen fehlschlagen, starte den Computer neu" -ForegroundColor White
Write-Host "- Stelle sicher, dass du mit dem Internet verbunden bist" -ForegroundColor White
Write-Host "- Überprüfe, ob dein GitHub-Account noch aktiv ist" -ForegroundColor White
Write-Host ""
