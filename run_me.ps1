# run_me.ps1
# Empfohlen: pwsh (PowerShell 7). Dieses Skript:
# - erstellt .venv (falls nicht vorhanden)
# - installiert requirements.txt (falls vorhanden)
# - legt eine Desktop-Verknüpfung an, die pythonw verwendet (kein Konsolenfenster)
# - startet die App mit pythonw

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

# Hinweis zur PowerShell-Version
if ($PSVersionTable.PSVersion.Major -lt 7) {
    Write-Warning "Du benutzt PowerShell $($PSVersionTable.PSVersion). Empfehlung: PowerShell 7 (pwsh). Dieses Skript läuft trotzdem."
}

# Python finden (py -3 bevorzugt)
$pythonName = $null
$pythonExtraArgs = ""
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonName = (Get-Command py).Source
    $pythonExtraArgs = "-3"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonName = (Get-Command python).Source
    $pythonExtraArgs = ""
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonName = (Get-Command python3).Source
    $pythonExtraArgs = ""
} else {
    Write-Error "Python nicht gefunden. Bitte installiere Python von https://python.org oder über den Microsoft Store."
    exit 1
}

# Pfade
$venvPath = Join-Path $projectDir '.venv'
$scriptPath = Join-Path $projectDir 'main.py'

# venv erstellen
if (-not (Test-Path $venvPath)) {
    Write-Output "Erstelle virtuelle Umgebung in $venvPath ..."
    if ($pythonExtraArgs -ne "") {
        & $pythonName $pythonExtraArgs -m venv $venvPath
    } else {
        & $pythonName -m venv $venvPath
    }
} else {
    Write-Output "Virtuelle Umgebung existiert bereits: $venvPath"
}

# Pfad zu venv python / pip
$venvPython = Join-Path $venvPath 'Scripts\python.exe'
$venvPip = Join-Path $venvPath 'Scripts\pip.exe'

if (-not (Test-Path $venvPython)) {
    Write-Warning "venv python nicht gefunden. Verwende System-Python."
    $venvPython = (Get-Command python -ErrorAction SilentlyContinue).Source
}

# requirements installieren falls vorhanden
$reqFile = Join-Path $projectDir 'requirements.txt'
if (Test-Path $reqFile) {
    Write-Output "Installiere Abhängigkeiten aus requirements.txt ..."
    if (Test-Path $venvPip) {
        & $venvPip install -r $reqFile
    } else {
        & $venvPython -m pip install -r $reqFile
    }
}

# pythonw (für kein Konsolenfenster) bevorzugt aus venv
$pythonw = Join-Path $venvPath 'Scripts\pythonw.exe'
if (-not (Test-Path $pythonw)) {
    $pythonwCmd = Get-Command pythonw -ErrorAction SilentlyContinue
    if ($pythonwCmd) {
        $pythonw = $pythonwCmd.Source
    } else {
        # fallback auf python (zeigt dann ggf. Konsole) - aber wir versuchen weiterhin pythonw
        $pythonw = $venvPython
    }
}

# Desktop-Verknüpfung erstellen
$desktop = [Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktop 'MeinePythonApp.lnk'
$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $pythonw
$shortcut.Arguments = "`"$scriptPath`""
$shortcut.WorkingDirectory = $projectDir
# Icon setzen (optional)
if (Test-Path $pythonw) {
    $shortcut.IconLocation = "$pythonw,0"
}
$shortcut.Save()
Write-Output "Desktop-Verknüpfung erstellt: $shortcutPath"

# App jetzt starten (mit pythonw, also ohne Konsole)
Write-Output "Starte die App (keine Konsole sollte erscheinen)..."
Start-Process -FilePath $pythonw -ArgumentList "`"$scriptPath`""
