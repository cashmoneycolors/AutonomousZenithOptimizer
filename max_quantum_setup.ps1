# ========================================================================
# 🌟 MAXIMALE QUANTENSTUFE AUTONOMES SETUP-SKRIPT (PowerShell) 🌟
# Passt sich automatisch an: WinGet, Chocolatey, manuell – alles abgedeckt!
# ========================================================================

$ProjectName = "AutomatisierterKI-Quanten-Projekt"
$EnvName = "venv"
$ProjectDir = Join-Path $Home $ProjectName

Write-Host ""
Write-Host "=======================================================" -ForegroundColor DarkCyan
Write-Host "--- Start des maximal autonomen Setups ---" -ForegroundColor Yellow
Write-Host "=======================================================" -ForegroundColor DarkCyan

# 1. PRÜFUNG: Python & VS Code bereits installiert?
function Test-Command($cmd) { return (Get-Command $cmd -ErrorAction SilentlyContinue) -ne $null }
$PythonOK = Test-Command "python"
$VSCodeOK = Test-Command "code"

# 2. PRÜFUNG: WinGet/Chocolatey verfügbar?
$UseWinGet = Test-Command "winget"
$UseChoco = Test-Command "choco"

# 3. Installation Python
if (-not $PythonOK) {
    if ($UseWinGet) {
        Write-Host "✅ Installiere Python 3.11 über WinGet..." -ForegroundColor Green
        winget install --id Python.Python.3.11 -e --accept-package-agreements --accept-source-agreements
    } elseif ($UseChoco) {
        Write-Host "✅ Installiere Python 3.11 über Chocolatey..." -ForegroundColor Green
        choco install python --version=3.11.0 -y
    } else {
        Write-Host "⚠️ Bitte installiere Python 3.11 manuell: https://www.python.org/downloads/" -ForegroundColor Yellow
        Read-Host "Drücke Enter, wenn Python installiert ist"
    }
} else {
    Write-Host "✅ Python ist bereits installiert." -ForegroundColor Green
}

# 4. Installation VS Code
if (-not $VSCodeOK) {
    if ($UseWinGet) {
        Write-Host "✅ Installiere VS Code über WinGet..." -ForegroundColor Green
        winget install --id Microsoft.VisualStudioCode -e --accept-package-agreements --accept-source-agreements
    } elseif ($UseChoco) {
        Write-Host "✅ Installiere VS Code über Chocolatey..." -ForegroundColor Green
        choco install vscode -y
    } else {
        Write-Host "⚠️ Bitte installiere VS Code manuell: https://code.visualstudio.com/download" -ForegroundColor Yellow
        Read-Host "Drücke Enter, wenn VS Code installiert ist"
    }
} else {
    Write-Host "✅ VS Code ist bereits installiert." -ForegroundColor Green
}

Start-Sleep -Seconds 5

# 5. Projektordner erstellen und wechseln
Write-Host "✅ Erstelle und navigiere zum Projektordner: $ProjectDir" -ForegroundColor Green
if (-not (Test-Path $ProjectDir)) { mkdir $ProjectDir }
cd $ProjectDir

# 6. Virtuelle Umgebung
Write-Host "✅ Erstelle die virtuelle Umgebung '$EnvName'..." -ForegroundColor Green
python -m venv $EnvName

$PythonExecutable = ".\$EnvName\Scripts\python.exe"
if (-not (Test-Path $PythonExecutable)) {
    Write-Host "❌ FEHLER: Python-Interpreter in venv nicht gefunden. Installation fehlgeschlagen?" -ForegroundColor Red
    exit
}

# 7. KI- und Quantenpakete
Write-Host "✅ Installiere KI-Basis-Pakete und Quanten-Frameworks..." -ForegroundColor Green
& $PythonExecutable -m pip install --upgrade pip
& $PythonExecutable -m pip install requests numpy qiskit cirq

# 8. Ollama + DeepSeek
Write-Host "✅ Installiere Ollama und lade DeepSeek-Modell..." -ForegroundColor Green
$ollamaUrl = "https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip"
$ollamaZip = Join-Path $ProjectDir "ollama.zip"
$ollamaDir = Join-Path $ProjectDir "ollama"
if (-not (Test-Path $ollamaDir)) {
    Invoke-WebRequest -Uri $ollamaUrl -OutFile $ollamaZip
    Expand-Archive -Path $ollamaZip -DestinationPath $ollamaDir
    Remove-Item $ollamaZip
}
$env:PATH += ";$ollamaDir"
& "$ollamaDir\ollama.exe" pull deepseek-coder
Start-Process -FilePath "$ollamaDir\ollama.exe" -ArgumentList "serve" -NoNewWindow
Write-Host "✅ DeepSeek-Modell geladen und Ollama-Server gestartet!" -ForegroundColor Green

# 9. VS Code Extensions
Write-Host "✅ Installiere VS Code Extensions..." -ForegroundColor Green
$extensions = @(
    "GitHub.copilot",
    "GitHub.copilot-chat",
    "blackboxapp.blackbox",
    "ms-python.python",
    "gen-ai.openai-chat-gpt",
    "qiskit-community.qiskit-vscode"
)
foreach ($ext in $extensions) {
    code --install-extension $ext
}

# 10. requirements.txt
Write-Host "✅ Erstelle requirements.txt..." -ForegroundColor Green
& $PythonExecutable -m pip freeze > requirements.txt

# 11. Beispielskript
Write-Host "✅ Erstelle Beispiel-Quanten-Skript (quanten_app.py)..." -ForegroundColor Green
@'
# Quanten-Hello-World mit Qiskit
from qiskit import QuantumCircuit
import numpy as np

def run_quantum_example():
    print("Starte Qiskit-Beispiel...")

    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    print("Quantenschaltkreis erfolgreich erstellt (Superposition erzeugt):")
    print(qc.draw(output="text"))

if __name__ == "__main__":
    run_quantum_example()
'@ | Set-Content -Path quanten_app.py

# 12. Abschluss
Write-Host ""
Write-Host "=======================================================" -ForegroundColor Green
Write-Host "🌟 QUANTENSTUFE ERREICHT! Setup abgeschlossen! 🌟" -ForegroundColor Green
Write-Host "Projektordner: $(Get-Location)" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "!!! Nächster SCHRITT MUSS MANUELL ERFOLGEN !!!" -ForegroundColor Red
Write-Host "1. Öffne den Ordner in VS Code: code ." -ForegroundColor Cyan
Write-Host "2. Melde dich in VS Code an (GitHub Copilot, OpenAI etc.)"
Write-Host "3. Aktiviere die Umgebung: .\\venv\\Scripts\\Activate.ps1" -ForegroundColor Cyan
