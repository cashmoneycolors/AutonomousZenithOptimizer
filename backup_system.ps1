# ==============================================================================
# 🚀 COMPREHENSIVE SYSTEM BACKUP SCRIPT 🚀
# Backs up GitHub repository, laptop files, and Visual Studio settings
# ------------------------------------------------------------------------------
# ZWECK: Vollständige Sicherung des Autonomous Zenith Optimizer Projekts
# ==============================================================================

# Definiert Backup-Verzeichnis und Zeitstempel
$BackupDir = Join-Path $Home "AutonomousZenithOptimizer_Backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$ProjectDir = "C:\Users\Laptop\Desktop\Autonomous Zenith Optimizer"
$Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

Write-Host ""
Write-Host "=======================================================" -ForegroundColor DarkCyan
Write-Host "--- COMPREHENSIVE SYSTEM BACKUP START ---" -ForegroundColor Yellow
Write-Host "Backup Directory: $BackupDir" -ForegroundColor Green
Write-Host "Timestamp: $Timestamp" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor DarkCyan

# 1. ERSTELLE BACKUP-VERZEICHNIS
Write-Host "✅ Erstelle Backup-Verzeichnis..." -ForegroundColor Green
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

# 1a. PRÜFE AUF UNCOMMITTED CHANGES
Write-Host "🔍 Prüfe auf nicht committete Änderungen..." -ForegroundColor Yellow
cd $ProjectDir
$GitStatus = git status --porcelain
if ($GitStatus) {
    Write-Host ""
    Write-Host "⚠️  WARNUNG: Es wurden Änderungen ohne Commit erkannt." -ForegroundColor Red
    Write-Host ""
    Write-Host "Folgende Dateien haben nicht committete Änderungen:" -ForegroundColor Yellow
    Write-Host $GitStatus
    Write-Host ""
    Write-Host "OPTIONEN:" -ForegroundColor Cyan
    Write-Host "1. [F]ortfahren - Backup trotzdem erstellen (uncommitted Änderungen werden eingeschlossen)" -ForegroundColor Green
    Write-Host "2. [A]bbrechen - Backup abbrechen, damit Sie zuerst committen können" -ForegroundColor Red
    Write-Host ""
    
    $Antwort = Read-Host "Ihre Auswahl (F/A)"
    
    if ($Antwort -ne "F" -and $Antwort -ne "f") {
        Write-Host ""
        Write-Host "❌ BACKUP ABGEBROCHEN" -ForegroundColor Red
        Write-Host "Bitte committen Sie Ihre Änderungen und führen Sie das Backup erneut aus." -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
    
    Write-Host ""
    Write-Host "✅ Fahre mit Backup fort trotz uncommitted Änderungen..." -ForegroundColor Yellow
    Write-Host ""
}

# 2. BACKUP GITHUB REPOSITORY (GIT BUNDLE)
Write-Host "✅ Erstelle Git Bundle für GitHub Repository..." -ForegroundColor Green
git bundle create "$BackupDir\autonomous_zenith_optimizer.bundle" --all
git log --oneline -10 > "$BackupDir\git_history.txt"

# 3. BACKUP LAPTOP FILES (VOLLSTÄNDIGES PROJEKT)
Write-Host "✅ Backup aller lokalen Projektdateien..." -ForegroundColor Green
Copy-Item -Path $ProjectDir -Destination "$BackupDir\project_files" -Recurse -Force

# 4. BACKUP VISUAL STUDIO SETTINGS
Write-Host "✅ Backup Visual Studio Code Settings..." -ForegroundColor Green
$VSCodeUserDir = "$env:APPDATA\Code\User"
if (Test-Path $VSCodeUserDir) {
    Copy-Item -Path $VSCodeUserDir -Destination "$BackupDir\vscode_settings" -Recurse -Force
}

# 5. BACKUP .NET PROJECT FILES
Write-Host "✅ Backup .NET Projekt spezifische Dateien..." -ForegroundColor Green
Copy-Item -Path "$ProjectDir\*.csproj" -Destination "$BackupDir\dotnet_project" -Force -ErrorAction SilentlyContinue
Copy-Item -Path "$ProjectDir\*.sln" -Destination "$BackupDir\dotnet_project" -Force -ErrorAction SilentlyContinue
Copy-Item -Path "$ProjectDir\bin" -Destination "$BackupDir\dotnet_project" -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path "$ProjectDir\obj" -Destination "$BackupDir\dotnet_project" -Recurse -Force -ErrorAction SilentlyContinue

# 6. BACKUP DATENBANKEN
Write-Host "✅ Backup Datenbanken..." -ForegroundColor Green
Copy-Item -Path "$ProjectDir\data" -Destination "$BackupDir\databases" -Recurse -Force -ErrorAction SilentlyContinue

# 7. BACKUP PYTHON ENVIRONMENT
Write-Host "✅ Backup Python Environment..." -ForegroundColor Green
Copy-Item -Path "$ProjectDir\.venv" -Destination "$BackupDir\python_env" -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path "$ProjectDir\requirements.txt" -Destination "$BackupDir\python_env" -Force -ErrorAction SilentlyContinue

# 8. BACKUP LOGS UND REPORTS
Write-Host "✅ Backup Logs und Reports..." -ForegroundColor Green
Copy-Item -Path "$ProjectDir\logs" -Destination "$BackupDir\logs_reports" -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path "$ProjectDir\optimization_reports" -Destination "$BackupDir\logs_reports" -Recurse -Force -ErrorAction SilentlyContinue

# 9. ERSTELLE BACKUP-INVENTAR
Write-Host "✅ Erstelle Backup-Inventar..." -ForegroundColor Green
$Inventory = @"
AUTONOMOUS ZENITH OPTIMIZER - COMPLETE SYSTEM BACKUP
==================================================

Backup Date: $Timestamp
Backup Location: $BackupDir
Original Project: $ProjectDir

CONTENTS:
---------
1. Git Bundle: autonomous_zenith_optimizer.bundle (complete repository)
2. Git History: git_history.txt (last 10 commits)
3. Project Files: project_files/ (complete project directory)
4. VS Code Settings: vscode_settings/ (user settings and extensions)
5. .NET Project: dotnet_project/ (project files, bin, obj)
6. Databases: databases/ (affiliate_system.db, enterprise_orchestrator.db)
7. Python Environment: python_env/ (.venv, requirements.txt)
8. Logs & Reports: logs_reports/ (all logs and optimization reports)

RESTORE INSTRUCTIONS:
--------------------
1. Extract backup to desired location
2. For Git: git clone autonomous_zenith_optimizer.bundle restored_repo
3. For VS Code: Copy vscode_settings to %APPDATA%\Code\User
4. For Python: Recreate venv and pip install -r requirements.txt
5. For .NET: Restore project files and rebuild

BACKUP CREATED SUCCESSFULLY!
"@

$Inventory | Out-File -FilePath "$BackupDir\BACKUP_INVENTORY.txt" -Encoding UTF8

# 10. ERSTELLE ZIP-ARCHIV
Write-Host "✅ Erstelle komprimiertes ZIP-Archiv..." -ForegroundColor Green
Compress-Archive -Path $BackupDir -DestinationPath "$BackupDir.zip" -Force

# 11. BERECHNE BACKUP-GRÖSSE
$BackupSize = (Get-ChildItem $BackupDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
$ZipSize = (Get-Item "$BackupDir.zip").Length / 1MB

# 12. ABSCHLUSS
Write-Host ""
Write-Host "=======================================================" -ForegroundColor Green
Write-Host "🌟 BACKUP ERFOLGREICH ABGESCHLOSSEN! 🌟" -ForegroundColor Green
Write-Host "Backup Directory: $BackupDir" -ForegroundColor Green
Write-Host "ZIP Archive: $BackupDir.zip" -ForegroundColor Green
Write-Host "Backup Size: $([math]::Round($BackupSize, 2)) MB" -ForegroundColor Green
Write-Host "ZIP Size: $([math]::Round($ZipSize, 2)) MB" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "!!! WICHTIGE INFORMATIONEN !!!" -ForegroundColor Red
Write-Host "1. **Backup-Verzeichnis**: $BackupDir" -ForegroundColor Cyan
Write-Host "2. **ZIP-Archiv**: $BackupDir.zip (für einfache Speicherung)" -ForegroundColor Cyan
Write-Host "3. **Git Bundle**: Vollständige Repository-Sicherung" -ForegroundColor Cyan
Write-Host "4. **VS Code Settings**: Alle Einstellungen und Erweiterungen gesichert" -ForegroundColor Cyan
Write-Host "5. **Datenbanken**: Alle SQLite-Datenbanken gesichert" -ForegroundColor Cyan
Write-Host ""
Write-Host "Für Wiederherstellung siehe BACKUP_INVENTORY.txt im Backup-Verzeichnis" -ForegroundColor Yellow
exit 0
