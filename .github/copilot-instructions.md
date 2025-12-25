# GitHub Copilot Instructions — AutonomousZenithOptimizer

## Big Picture
- Einstieg: [Program.cs](Program.cs) (DI, Config-Overlays, Live-Guardrails, Endlosschleife).
- Orchestrator: [Core/ZenithController.cs](Core/ZenithController.cs) baut DRL-State → holt QML-Decision → führt Side-Effects (Trade/Text/Orders) aus → meldet Feedback.
- Grenzen: Verträge in [Core/Interfaces.cs](Core/Interfaces.cs); externe Effekte in [Adapters](Adapters); Infrastruktur/State in [Modules](Modules).

## Kritische Invarianten
- Retry: `ExecuteQMLWithRetry` mit Exponential-Backoff (Basis*2^i, max 30s) muss final exakt `MAINTAIN_LEVEL:1.0` liefern.
- NormalizeDecision: akzeptiert nur `SCALE_UP:<factor>`; robustes Parsen (`,`→`.`); Clamp auf Settings-Min/Max (Hardcap 100).
- Compliance-Gate: Text-Generierung nur wenn `RH_ComplianceScore > ComplianceThreshold`.

## Konfiguration & LiveMode
- Settings in [Core/OptimizerSettings.cs](Core/OptimizerSettings.cs); Overlays via `appsettings.json` + `appsettings.{Environment}.json` (`DOTNET_ENVIRONMENT`).
- Live: `OptimizerSettings.LiveMode` oder `AZO_LIVE_MODE=true` erzwingt Guardrails und gültigen `Optimizer:QmlEndpoint`/`AZO_QML_ENDPOINT`.
- Stubs: In LiveMode werfen Adapter-Stubs (siehe HFT/GEF/ECA in [Adapters](Adapters)).

## Cache-Muster
- `HoloCache` in [Modules/HoloCache.cs](Modules/HoloCache.cs) mit `IConnectionMultiplexer` oder `RedisMock`.
- Keys/TTL: `context:{query}`, `context:probe:{id}` (5 min); Hits/Misses erneuern TTL.

## Dev-Workflows
- Format-Gate: `dotnet format AutonomousZenithOptimizer.sln --verify-no-changes`.
- Build/Test/Run:
	- `dotnet restore AutonomousZenithOptimizer.sln`
	- `dotnet build AutonomousZenithOptimizer.sln -c Release --no-restore`
	- `dotnet test AutonomousZenithOptimizer.sln -c Release --no-build --collect:"XPlat Code Coverage" --results-directory ./test-results`
	- `dotnet run --project ZenithCoreSystem.csproj`
- Tests/Fakes: [tests/ZenithCoreSystem.Tests/AutonomousZenithOptimizerTests.cs](tests/ZenithCoreSystem.Tests/AutonomousZenithOptimizerTests.cs).
- CI: [.github/workflows/dotnet.yml](.github/workflows/dotnet.yml) auf `pull_request` und ausgewählten Branches.

## Produktions-Gate (Env-Variablen)
- Development (Default):
  - `$env:DOTNET_ENVIRONMENT = "Development"`
  - `EnableDemoScenarios=true`, Retry mit Failure-Simulation.
- Production (Live-Ready):
  - `$env:DOTNET_ENVIRONMENT = "Production"`
  - `$env:AZO_LIVE_MODE = "true"` (erzwingt Guardrails, blockiert Stubs)
  - `$env:AZO_QML_ENDPOINT = "https://<your-qml-service>"` (z. B. Azure Function)
  - Vor Push/PR: `dotnet format ... --verify-no-changes` + `dotnet test ...`.

