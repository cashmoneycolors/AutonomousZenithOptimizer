# ==============================================================================
# 🚀 ULTRA-MAXIMALES KI/QUANTEN-TOOLKIT-SETUP (PowerShell) 🚀
# Dieses Skript ist der finale Build. Es installiert:
# 1. Alle Basis-Tools (Python, VS Code, Node.js).
# 2. Alle Top-Cloud-Agenten (Copilot, OpenAI, AWS CodeWhisperer).
# 3. Den lokalen Autonomie-Agenten OLLAMA (Basis für "Grok-ähnliche" Modelle).
# 4. Quanten-Entwicklungs-Frameworks (Qiskit, Cirq).
# ==============================================================================

# Definiert Namen für das Projekt und die virtuelle Umgebung
$ProjectName = "ULTRA_KI_Quanten_Toolkit_Projekt"
$EnvName = "venv"
$ProjectDir = Join-Path $Home $ProjectName

Write-Host ""
Write-Host "=======================================================" -ForegroundColor DarkCyan
Write-Host "--- Start des FINALEN TOOLKIT-Setups ---" -ForegroundColor Yellow
Write-Host "=======================================================" -ForegroundColor DarkCyan

# 1. PRÜFUNG: WinGet-Verfügbarkeit
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "❌ FEHLER: WinGet ist nicht installiert. Bitte WinGet installieren oder das Skript anpassen." -ForegroundColor Red
    exit
}

# 2. BASIS-SOFTWARE INSTALLATION
Write-Host "✅ Installiere Basis-Tools (Python, VS Code, Node.js, Ollama)..." -ForegroundColor Green
# Installiert Python (Basis für KI/Quanten)
winget install --id Python.Python.3.11 -e --accept-package-agreements --accept-source-agreements
# Installiert VS Code (Ihre IDE)
winget install --id Microsoft.VisualStudioCode -e --accept-package-agreements --accept-source-agreements
# Installiert Node.js (Basis für viele moderne CLI-Tools)
winget install OpenJS.Nodejs.LTS -e --accept-package-agreements --accept-source-agreements
# Installiert OLLAMA (Die Plattform für lokale KI-Agenten)
winget install Ollama.Ollama -e --accept-package-agreements --accept-source-agreements

# Wartezeit für PATH-Aktualisierung
Start-Sleep -Seconds 7

# 3. PROJEKT-SETUP
Write-Host "✅ Erstelle Projektordner, VENV und Pfade..." -ForegroundColor Green
mkdir $ProjectDir
cd $ProjectDir
python -m venv $EnvName
$PythonExecutable = ".\$EnvName\Scripts\python.exe"

# 4. PYTHON PAKETE INSTALLIEREN (Quanten- und KI-Schnittstellen)
Write-Host "✅ Installiere Quanten-Frameworks (qiskit, cirq) und KI-Basispakete..." -ForegroundColor Green
& $PythonExecutable -m pip install requests numpy qiskit cirq openai

# 5. VS Code ERWEITERUNGEN INSTALLIEREN (MAXIMALE KI-TOOLBOX)
Write-Host "✅ Installiere ALLE KI-Agenten (Cloud- und Lokal-Spezialisten)..." -ForegroundColor Green

# --- CLOUD- & ABONNEMENT-AGENTEN (Der Copilot-Standard) ---
code --install-extension GitHub.copilot
code --install-extension GitHub.copilot-chat
code --install-extension gen-ai.openai-chat-gpt
code --install-extension AmazonWebServices.aws-toolkit

# --- KOSTENLOSE & LOKALE AGENTEN (Grok/Code Llama-Ersatz) ---
code --install-extension Codeium.Codeium # Kostenloser, schneller Code-Vervollständiger
code --install-extension TabNine.tabnine-vscode
code --install-extension VisualStudioExptTeam.vscodeintellicode
code --install-extension ms-toolsai.vscode-ai-toolkit
code --install-extension gen-ai.ollama # VS Code Client für lokale Modelle (Code Llama)

# --- QUANTEN-BASIS ---
code --install-extension ms-python.python
code --install-extension qiskit-community.qiskit-vscode

# 6. ABSCHLUSS
Write-Host "✅ Erstelle requirements.txt..." -ForegroundColor Green
& $PythonExecutable -m pip freeze > requirements.txt

# 7. MANUELLE ANLEITUNG (Zwingend für Funktion)
Write-Host ""
Write-Host "=======================================================" -ForegroundColor Green
Write-Host "🌟 FINALER BUILD ABGESCHLOSSEN! 🌟" -ForegroundColor Green
Write-Host "Projektpfad: $(Get-Location)" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "!!! NÄCHSTE SCHRITTE: AKTIVIERUNG DES AGENTEN !!!" -ForegroundColor Red
Write-Host "1. **VS Code öffnen**: `code .`" -ForegroundColor Cyan
Write-Host "2. **Grok-Ersatz (Code Llama) laden**: Führen Sie im VS Code Terminal ein:"
Write-Host " -> ``ollama pull codellama:7b``" -ForegroundColor Cyan
Write-Host " (Dies lädt das Modell, das am besten für Code-Geschwindigkeit optimiert ist.)"
Write-Host "3. **Agenten-Anmeldung**: Melden Sie sich bei Copilot, OpenAI und AWS an, um die Cloud-Agenten freizuschalten."
Write-Host "4. **Umgebung aktivieren**: ``.\venv\Scripts\Activate.ps1``"
