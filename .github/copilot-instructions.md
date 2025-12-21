# GitHub Copilot Instructions  AutonomousZenithOptimizer

## Überblick (Big Picture)
- Einstieg: `Program.cs` (Host/DI, `appsettings.json`, Main-Loop, optional Demo-Szenarien).
- Orchestrator: `Core/ZenithController.cs` (koordinierte QML-Decision, Trades, Text-Gen, Governance/Compliance).
- Integrationsgrenzen: `Adapters/` und `Modules/` sind die Außenkante (HTTP/Redis/HFT/CRM/KI). Änderungen hier sind potenziell breaking.

## Projektstruktur & Kernkonzepte
- `Core/Interfaces.cs`: stabile Contracts (`IProfitGuarantor_QML`, `IHyperCache`, `IHFT_AMAD_Adapter`, ). Signaturänderungen immer repo-weit + Tests mitziehen.
- `Core/DataModels.cs`: Domain-Records (`Order`, `DRL_StateVector`). `DRL_StateVector.ToString()` wird als Reporting-/Log-Format genutzt.
- `Core/OptimizerSettings.cs`: Runtime-Schalter (Retries, `ComplianceThreshold`, Demo, Redis, Cycle-Delay).
- `Modules/QMLBridge.cs`: QML-Integration (HTTP nach `http://localhost:8501/api/qml_decision?...` + Fallback).
- `Modules/HoloCache.cs`: Cache/Redis-Abstraktion; Keys nach Muster `context:{query}`; TTL (aktuell ~5 Min) + `ContextualMemoryHandler`.
- `Modules/Infrastructure.cs`: zentrales Logging (`ZenithLogger`), Governance (`RegulatoryHyperAdaptor`), Event-Routing (`AetherArchitecture`).

## Kritische Flows (wo Logik zusammenläuft)
- `RunAutonomousGrowthStrategy()`:
  - baut `DRL_StateVector`  `ExecuteQMLWithRetry()`.
  - bei `SCALE_UP:x`  `IHFT_AMAD_Adapter.ExecuteTrade()`.
  - bei Compliance > `OptimizerSettings.ComplianceThreshold`  `IGEF_MSA_Adapter.GenerateText()`.
  - Feedback: `IProfitGuarantor_QML.ReportPerformanceFeedback(...)`.
- `ExecuteQMLWithRetry()` ist Single Source of Truth für Retry/Backoff/Fallback (Fallback: `MAINTAIN_LEVEL:1.0`).
- `ProcessIncomingOrder(Order)` blockiert bei `RegulatoryHyperAdaptor.PerformLegalIntegrityCheck(order)==false` (z.B. FR + >10k) und liefert Kontext via `ContextualMemoryHandler`.

## Konfiguration
- `appsettings.json`  `Optimizer`:
  - `RedisConnectionString`: leer  Redis-Mock; gesetzt  echter `StackExchange.Redis` Multiplexer (in `Program.cs`).
  - Flags wie `SimulateQmlFailure`, `EnableDemoScenarios`, `CycleDelaySeconds` steuern Laufzeitverhalten.

## Developer Workflow (lokal wie CI)
- CI: `.github/workflows/dotnet.yml` (Windows, .NET 8.0.x).
- Restore: `dotnet restore AutonomousZenithOptimizer.sln`
- Build: `dotnet build AutonomousZenithOptimizer.sln -c Release --no-restore`
- Test + Coverage: `dotnet test AutonomousZenithOptimizer.sln -c Release --no-build --collect:"XPlat Code Coverage"`
- Run: `dotnet run --project ZenithCoreSystem.csproj`

## Tests (repo-spezifisches Pattern)
- `tests/ZenithCoreSystem.Tests/AutonomousZenithOptimizerTests.cs` nutzt In-Process-Fakes (z.B. `AlwaysFailingQml`, `Recording*Adapter`) statt echte HTTP/Redis/Adapter.


## Robustheit (repo-spezifisch)
- QML-Integration: Retry/Backoff/Fallback ausschließlich in `ExecuteQMLWithRetry()` anfassen; Fallback-Decision bleibt exakt `MAINTAIN_LEVEL:1.0`.
- Adapter-Grenzen: Side-Effects (HTTP/Redis/HFT/CRM/KI) bleiben in `Adapters/` bzw. `Modules/`; Core-Logik ruft nur Interfaces aus `Core/Interfaces.cs`.
- Compliance/Governance: Gatekeeping nicht umgehen  Checks bleiben zentral in `RegulatoryHyperAdaptor` und werden aus `ProcessIncomingOrder(Order)` heraus genutzt.
- Tests bleiben offline: Für neue Adapter immer einen In-Process-Fake/Recording-Adapter nach dem Pattern in `tests/ZenithCoreSystem.Tests/AutonomousZenithOptimizerTests.cs` mitliefern (keine echten Calls in Unit-Tests).
- Cache/Memory: Wenn du Keys/TTL änderst, bleib beim Prefix `context:{query}` und halte das Verhalten über Redis-Mock und echten Redis konsistent.
## Änderungsregeln (wichtig für Agenten)
- Neue Integrationen immer hinter ein Interface legen + in `Program.cs` per DI registrieren (kein verstreutes `new`).
- QML-Retry/Fallback nur in `ExecuteQMLWithRetry()` erweitern.
- Wenn du `Core/Interfaces.cs` anfasst: Implementierungen + Tests in derselben Änderung aktualisieren.

