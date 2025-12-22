#!/usr/bin/env python3
import os
import shutil
import subprocess

def run_command(cmd, cwd=None):
    """Führt einen Command aus und gibt stdout/stderr zurück."""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Fehler bei Command: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        return False
    return True

def main():
    repo_root = r"C:\Users\nazmi\AutonomousZenithOptimizer"
    workspace = r"C:\.github\copilot-instructions\AutonomousZenithOptimizer\.github\workflows"
    print(f"Workspace: {workspace}")
    print("Dateien im Workspace:", os.listdir(workspace))

    # 1. Originale sichern
    print("Sichere Originaldateien...")
    shutil.copy(os.path.join(repo_root, "Core", "OptimizerSettings.cs"),
                os.path.join(repo_root, "Core", "OptimizerSettings.original.cs"))
    shutil.copy(os.path.join(repo_root, "Core", "ZenithController.cs"),
                os.path.join(repo_root, "Core", "ZenithController.original.cs"))
    shutil.copy(os.path.join(repo_root, "Modules", "Infrastructure.cs"),
                os.path.join(repo_root, "Modules", "Infrastructure.original.cs"))

    # 2. Optimierte Versionen kopieren
    print("Kopiere optimierte Dateien...")
    shutil.copy(os.path.join(workspace, "OptimizerSettings_optimized.cs"),
                os.path.join(repo_root, "Core", "OptimizerSettings.cs"))
    shutil.copy(os.path.join(workspace, "ZenithController_optimized.cs"),
                os.path.join(repo_root, "Core", "ZenithController.cs"))
    shutil.copy(os.path.join(workspace, "Infrastructure_optimized.cs"),
                os.path.join(repo_root, "Modules", "Infrastructure.cs"))

    # 3. Build und Test
    print("Baue und teste...")
    if not run_command("dotnet restore AutonomousZenithOptimizer.sln", cwd=repo_root):
        return
    if not run_command("dotnet format AutonomousZenithOptimizer.sln", cwd=repo_root):
        return
    if not run_command("dotnet build AutonomousZenithOptimizer.sln --configuration Release --no-restore", cwd=repo_root):
        return
    if not run_command("dotnet test AutonomousZenithOptimizer.sln --configuration Release --no-build --collect:\"XPlat Code Coverage\" --results-directory ./test-results", cwd=repo_root):
        return

    # 4. Git Commit
    print("Committe Änderungen...")
    if not run_command("git add .", cwd=repo_root):
        return
    if not run_command("git commit -m \"Optimierte Versionen mit exponentiellem Backoff, deterministischer Compliance und ENV Secrets\" --author=\"Kilo Code <cashmoeycolors@gmail.com>\"", cwd=repo_root):
        return

    # 5. Git Pull und Push
    print("Pulle und pushe...")
    if not run_command("git pull --rebase", cwd=repo_root):
        return
    if not run_command("git push", cwd=repo_root):
        return

    print("Erfolgreich optimiert und gepusht!")

if __name__ == "__main__":
    main()