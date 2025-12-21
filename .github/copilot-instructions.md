# Copilot Instructions  AutonomousZenithOptimizer

## Big Picture (wo anfangen)
- Startpunkt: `Program.cs` (HostBuilder + DI, Settings aus `appsettings.json`, Main-Loop, optional Demo-Szenarien).
- Orchestrator: `AutonomousZenithOptimizer` in `Core/ZenithController.cs` (steuert QML-Decision, Trades, Text-Gen, Governance).

## Struktur & Verantwortlichkeiten
- `Core/`
  - `Core/Interfaces.cs`: **stabile Contracts** für Adapter/Module (`IProfitGuarantor_QML`, `IHyperCache`, `IHFT_AMAD_Adapter`, ...).
  - `Core/DataModels.cs`: Domain-Records (`Order`, `DRL_StateVector`), `DRL_StateVector.ToString()` ist das Reporting-Format.
  - `Core/OptimizerSettings.cs`: Runtime-Schalter (Retry, ComplianceThreshold, Demo, Redis, CycleDelay).
- `Modules/`
  - `Modules/QMLBridge.cs`: `IProfitGuarantor_QML` (HTTP zu `http://localhost:8501/api/qml_decision?...` + lokale Fallback-Logik).
  - `Modules/HoloCache.cs`: Cache/Redis-Abstraktion, Key: `context:{query}`, TTL aktuell 5 Minuten; enthält `ContextualMemoryHandler`.
  - `Modules/Infrastructure.cs`: zentrales Logging (`ZenithLogger`), Governance (`RegulatoryHyperAdaptor`), Event-Routing (`AetherArchitecture`).
- `Adapters/`: Side-Effects/Integrationsgrenzen (HFT/CRM/KI). Änderungen hier sind die Außenkante des Systems.

## Kritische Flows (Datenfluss)
- `RunAutonomousGrowthStrategy()`:
  - baut `DRL_StateVector`  `ExecuteQMLWithRetry()`  bei `SCALE_UP:x` ruft `IHFT_AMAD_Adapter.ExecuteTrade()`.
  - bei Compliance > `OptimizerSettings.ComplianceThreshold`: `IGEF_MSA_Adapter.GenerateText()`.
  - reportet Feedback via `IProfitGuarantor_QML.ReportPerformanceFeedback(...)` und loggt strukturiert.
- `ExecuteQMLWithRetry()` (eine zentrale Stelle!):
  - Versuche: `OptimizerSettings.QmlRetryCount`, Delay: `QmlBaseDelayMilliseconds * (i+1)`, Fallback-Aktion: `MAINTAIN_LEVEL:1.0`.
- `ProcessIncomingOrder(Order)`:
  - Blockiert bei `RegulatoryHyperAdaptor.PerformLegalIntegrityCheck(order)==false` (FR + > 10k).
  - ruft `ContextualMemoryHandler.DeliverPreventiveContext(...)` und (bei `PremiumLicense`) `IECA_AHA_Adapter.SubmitOrder(...)`.

## Konfiguration (real im Repo)
- `appsettings.json`  `Optimizer`:
  - `RedisConnectionString`: leer  `RedisMock`, gesetzt  echter `StackExchange.Redis` Multiplexer in `Program.cs`.
  - `SimulateQmlFailure`, `EnableDemoScenarios`, `CycleDelaySeconds` steuern Laufzeitverhalten.

## Build / Run / Test (wie CI)
- Restore: `dotnet restore AutonomousZenithOptimizer.sln`
- Build: `dotnet build AutonomousZenithOptimizer.sln -c Release --no-restore`
- Test + Coverage: `dotnet test AutonomousZenithOptimizer.sln -c Release --no-build --collect:"XPlat Code Coverage"`
- Run: `dotnet run --project ZenithCoreSystem.csproj`
- CI: `.github/workflows/dotnet.yml` (windows-latest, .NET 8.0.x, XPlat Code Coverage).

## Tests (konkretes Pattern)
- `tests/ZenithCoreSystem.Tests/AutonomousZenithOptimizerTests.cs` nutzt In-Process-Fakes (`AlwaysFailingQml`, `Recording*Adapter`) statt echte HTTP/Redis/Adapter.

## Änderungsregeln (repo-spezifisch, wichtig)
- `Core/Interfaces.cs` nicht heimlich brechen: bei Signaturänderungen immer Implementierungen + Tests in einem Zug anpassen.
- Neue Integrationen immer hinter ein Interface legen und in `Program.cs` per DI registrieren (kein verstreutes `new`).
- Retry/Fallback der QML-Integration nur über `ExecuteQMLWithRetry()` erweitern (Single Source of Truth).
