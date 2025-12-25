# GitHub Copilot Instructions — AutonomousZenithOptimizer

## Architektur (wo anfangen?)
- Einstieg/Host: [Program.cs](Program.cs) richtet DI ein, lädt `Optimizer`-Config, erzwingt Live-Guardrails und läuft in einer Endlosschleife.
- Orchestrator: [Core/ZenithController.cs](Core/ZenithController.cs) (`AutonomousZenithOptimizer`) baut DRL-State → holt QML-Decision → führt Side-Effects (Trade/Text/Orders) aus → reportet Feedback.
- Verträge & Grenzen: Interfaces in [Core/Interfaces.cs](Core/Interfaces.cs); Side-Effects liegen in [Adapters](Adapters), Infrastruktur/State in [Modules](Modules).

## Kritische Invarianten (Tests schützen diese)
- QML-Retry/Fallback: `ExecuteQMLWithRetry` nutzt Exponential-Backoff (`QmlBaseDelayMilliseconds * 2^i`, max 30s) und muss final **exakt** `MAINTAIN_LEVEL:1.0` zurückgeben.
- Decision-Normalisierung: `NormalizeDecision` akzeptiert nur `SCALE_UP:<factor>`, parst robust (`,`→`.`), clamp’t auf `ScaleUpMinFactor..ScaleUpMaxFactor` (zusätzlich hard cap 100).
- Compliance-Gate: Text-Gen läuft nur wenn `RH_ComplianceScore > ComplianceThreshold` (siehe Orchestrator-Flow).

## Konfiguration & Live-Mode Guardrails
- Settings: [Core/OptimizerSettings.cs](Core/OptimizerSettings.cs) (Defaults) + Overlays via `appsettings.json`/`appsettings.{Environment}.json` (`DOTNET_ENVIRONMENT`).
- LiveMode: `OptimizerSettings.LiveMode` oder `AZO_LIVE_MODE=true` → in [Program.cs](Program.cs) wird erzwungen: `EnableDemoScenarios=false`, `SimulateQmlFailure=false`, und QML Endpoint vorhanden (`Optimizer:QmlEndpoint` oder `AZO_QML_ENDPOINT`).
- Adapter-Stubs werfen in LiveMode absichtlich (`InvalidOperationException`): [Adapters/HFT_AMAD_Adapter.cs](Adapters/HFT_AMAD_Adapter.cs), [Adapters/GEF_MSA_Adapter.cs](Adapters/GEF_MSA_Adapter.cs), [Adapters/ECA_AHA_Adapter.cs](Adapters/ECA_AHA_Adapter.cs).

## Cache/Memory Pattern
- Redis ist abstrakt über `IConnectionMultiplexer` + `RedisMock` (ohne `REDIS_CONNECTION_STRING`) in [Modules/HoloCache.cs](Modules/HoloCache.cs).
- Keys/TTL: `context:{query}` und `context:probe:{id}` (5 Minuten). Hits und Misses setzen TTL erneut.

## Wo ändern? (ohne Architekturbruch)
- Neue externe Provider integrieren: Interface in [Core/Interfaces.cs](Core/Interfaces.cs) beibehalten, Implementierung in [Adapters](Adapters) austauschen/ergänzen (LiveMode darf keine Stubs nutzen).
- Decision/State/Retry anpassen: ausschließlich im Orchestrator [Core/ZenithController.cs](Core/ZenithController.cs) (insb. `ExecuteQMLWithRetry`, `NormalizeDecision`).
- Cache/State-Mechanik ändern: [Modules/HoloCache.cs](Modules/HoloCache.cs) und die Probe-Calls im Orchestrator (jede Iteration misst Latenz).

## Dev-Workflows (Repo-Konvention)
- CI ist in [.github/workflows/dotnet.yml](.github/workflows/dotnet.yml) definiert und prüft Format + Tests auf Windows.
- Hinweis: [.github/workflows/workflow.yml](.github/workflows/workflow.yml) ist nur ein Template/Beispiel und nicht die relevante CI-Pipeline.
- Format-Gate (CI): `dotnet format AutonomousZenithOptimizer.sln --verify-no-changes`.
- Build/Test/Run: `dotnet restore AutonomousZenithOptimizer.sln` · `dotnet build AutonomousZenithOptimizer.sln -c Release --no-restore` · `dotnet test AutonomousZenithOptimizer.sln -c Release --no-build --collect:"XPlat Code Coverage" --results-directory ./test-results` · `dotnet run --project ZenithCoreSystem.csproj`.
- Tests/Fakes sind maßgeblich in [tests/ZenithCoreSystem.Tests/AutonomousZenithOptimizerTests.cs](tests/ZenithCoreSystem.Tests/AutonomousZenithOptimizerTests.cs) (z. B. `AlwaysFailingQml`, `ScaleUpQml`, Recording-Adapter). Interface-Änderungen erfordern Updates in allen Adaptern + Tests.

## GitHub/PR Hinweise (CI-relevant)
- CI läuft bei `pull_request` und bei `push` auf `main`, `master`, `blackboxai/repository-recovery` (siehe [.github/workflows/dotnet.yml](.github/workflows/dotnet.yml)).
- Vor Push/PR lokal denselben Gate laufen lassen wie CI: `dotnet format ... --verify-no-changes` und `dotnet test ... --collect:"XPlat Code Coverage"`.
- PR-Hygiene: Änderungen an Editor/Setup-Dateien nur committen wenn beabsichtigt (z. B. [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json), [.vscode/extensions.json](.vscode/extensions.json)).

## Logging (projekt-spezifisch)
- Strukturiertes Logging läuft über `ZenithLogger.LogAutonomousCycle`/`LogCriticalError` in [Modules/Infrastructure.cs](Modules/Infrastructure.cs) (Scope-Properties via `BeginScope`).

## Tooling (Editor/Container)
- Devcontainer ist vorhanden: [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json) (Dotnet/Node/Python/PowerShell/Android-SDK-Feature-Set).
- VS Code Empfehlungen: [.vscode/extensions.json](.vscode/extensions.json) (Copilot Chat, GitHub PR/Actions, Python/PowerShell, Dev Containers).

## Remote Hub & Mobile (separater Subsystem-Edge)
- Node UI + Flask Stats in [remote_hub](remote_hub) (Ports 3000/8503, Startscript: [remote_hub/start_hub.ps1](remote_hub/start_hub.ps1)); Android WebView-Client in [ZenithMobileApp](ZenithMobileApp).
- Quickstart (Details in [remote_hub/README.md](remote_hub/README.md)): Python `python -m venv .venv` + `./.venv/Scripts/pip install -r requirements.txt` + `./.venv/Scripts/python webhook_server.py` und Node `npm install` + `npm start`.
- Python-Utilities (`agent.py`, [python_modules](python_modules)) sind standalone; .NET Host ruft sie nicht automatisch.

