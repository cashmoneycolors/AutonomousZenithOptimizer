# Backup System Scripts

## Übersicht

Es gibt zwei Versionen des Backup-Skripts:

### 1. `backup_system.ps1` - Aktuelle Version (EMPFOHLEN)
- **Beschreibung**: Erweiterte Version mit Uncommitted-Changes-Erkennung
- **Feature**: Prüft vor dem Backup auf nicht committete Git-Änderungen
- **Warnung**: Zeigt "Es wurden Änderungen ohne Commit erkannt." wenn uncommitted changes vorhanden sind
- **Optionen**: 
  - `[F]ortfahren` - Backup trotzdem erstellen
  - `[A]bbrechen` - Backup abbrechen für manuelles Commit
- **Verwendung**: `.\backup_system.ps1`

### 2. `backup_system.original.ps1` - Original Version (FALLBACK)
- **Beschreibung**: Original-Version ohne Uncommitted-Changes-Prüfung
- **Zweck**: Notfall-Backup falls die neue Version Probleme verursacht
- **Feature**: Erstellt Backup ohne zusätzliche Prüfungen
- **Verwendung**: `.\backup_system.original.ps1`

## Empfehlung

Verwenden Sie **`backup_system.ps1`** für regelmäßige Backups. Diese Version bietet zusätzliche Sicherheit durch die Warnung bei uncommitted changes.

Falls die neue Version aus irgendeinem Grund nicht funktioniert oder Probleme verursacht, können Sie jederzeit auf **`backup_system.original.ps1`** zurückgreifen.

## Backup-Inhalt (beide Versionen)

Beide Skripte erstellen vollständige System-Backups mit:
1. Git Bundle (vollständiges Repository)
2. Git History (letzte 10 Commits)
3. Projekt-Dateien (vollständiges Verzeichnis)
4. VS Code Settings (Einstellungen und Erweiterungen)
5. .NET Projekt-Dateien (csproj, sln, bin, obj)
6. Datenbanken (SQLite-DBs)
7. Python Environment (.venv, requirements.txt)
8. Logs & Reports (alle Logs und Optimierungsberichte)

## Wiederherstellung

Siehe `BACKUP_INVENTORY.txt` im erstellten Backup-Verzeichnis für detaillierte Wiederherstellungsanweisungen.
